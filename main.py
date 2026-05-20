import cv2
import threading
import time
from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms
from plc import PLCInterface
from data_logger import guardar
from datetime import datetime

# Instanciação limpa do módulo PLC (os parâmetros antigos de IP/Porta saíram)
plc = PLCInterface()

def iniciar_maquina():
    print("A iniciar módulos internos...")
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    
    # Inicia o servidor na porta 5000 para receber a conexão do VB.NET
    servidor = ServerComms(ip="0.0.0.0", port=5000)
    
    # Vincula o servidor ao módulo PLC para intercâmbio de dados na mesma socket
    plc.servidor = servidor

    foto_em_memoria = None

    def tratar_comando(cliente, comando):
        nonlocal foto_em_memoria
        
        # Filtro Antibloqueio para não colidir o PING com os Botões
        if "CHECK_PADRAO" in comando or "PADRAO" in comando:
            cmd_limpo = comando.replace("PING", "").strip()
        else:
            if "PROCESSAR" in comando: cmd_limpo = "PROCESSAR"
            elif "CAPTURAR" in comando: cmd_limpo = "CAPTURAR"
            elif "AUTO" in comando: cmd_limpo = "AUTO"
            elif "PING" in comando: cmd_limpo = "PING"
            else: cmd_limpo = comando

        if cmd_limpo == "PING":
            servidor.send_message("PONG\n", cliente)

        elif cmd_limpo == "AUTO":
            frame = camara.capture_frame()
            if frame is not None:
                _, frame_proc, dados = visao.process_and_decide(frame)
                id_padrao = dados.get("padrão_selecionado", {}).get("id", 1) if isinstance(dados.get("padrão_selecionado"), dict) else 1
                nome_padrao = dados.get("padrão_selecionado", {}).get("nome", "Desconhecido") if isinstance(dados.get("padrão_selecionado"), dict) else "Desconhecido"
                zonas = dados.get("zonas", [])
                
                # Executa a avaliação reutilizando o canal TCP aberto
                decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                is_ok_final = (decisao_plc == "OK")
                
                # ==========================================
                #  GUARDAR DADOS DO MODO AUTOMÁTICO
                # ==========================================
                txt_info = f"--- RESULTADO DA INSPEÇÃO (MODO AUTO) ---\n"
                txt_info += f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                txt_info += f"Decisão PLC: {decisao_plc}\n"
                txt_info += f"Padrão Analisado: {nome_padrao} (ID: {id_padrao})\n\n"
                txt_info += "--- VALORES POR ZONA ---\n"
                for z in zonas:
                    txt_info += f"Zona {z.get('zona', '?')}: Brilho={z.get('brilho_medio', 0):.1f} | X_CIE={z.get('x_cie', 0):.4f} | Y_CIE={z.get('y_cie', 0):.4f}\n"

                ret1, jpeg_raw = cv2.imencode('.jpg', frame)
                ret2, jpeg_proc = cv2.imencode('.jpg', frame_proc)
                if ret1 and ret2:
                    guardar(guia=nome_padrao, tipo="t", img_data=jpeg_raw.tobytes(), txt_data=txt_info, img_res_data=jpeg_proc.tobytes())
                # ==========================================

                servidor.send_auto_result(is_ok_final, frame_proc, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_IMAGEM\n", cliente)

        elif cmd_limpo == "CAPTURAR":
            frame = camara.capture_frame()
            if frame is not None:
                foto_em_memoria = frame
                servidor.send_image_only(frame, tag="CAPTURAR", destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_IMAGEM\n", cliente)

        elif cmd_limpo == "PROCESSAR":
            if foto_em_memoria is not None:
                _, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                
                id_padrao = dados.get("padrão_selecionado", {}).get("id", 0) if isinstance(dados.get("padrão_selecionado"), dict) else 0
                nome_padrao = dados.get("padrão_selecionado", {}).get("nome", "Desconhecido") if isinstance(dados.get("padrão_selecionado"), dict) else "Desconhecido"
                
                if id_padrao == 0 or nome_padrao == "Desconhecido":
                    servidor.send_message("ERRO|DESCONHECIDO\n", cliente)
                else:
                    zonas = dados.get("zonas", [])
                    
                    # Executa a avaliação reutilizando o canal TCP aberto
                    decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                    is_ok_final = (decisao_plc == "OK")

                    # ==========================================
                    #  GUARDAR DADOS DO MODO PROCESSAR (MANUAL)
                    # ==========================================
                    txt_info = f"--- RESULTADO DA INSPEÇÃO (MODO MANUAL) ---\n"
                    txt_info += f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    txt_info += f"Decisão PLC: {decisao_plc}\n"
                    txt_info += f"Padrão Analisado: {nome_padrao} (ID: {id_padrao})\n\n"
                    txt_info += "--- VALORES POR ZONA ---\n"
                    for z in zonas:
                        txt_info += f"Zona {z.get('zona', '?')}: Brilho={z.get('brilho_medio', 0):.1f} | X_CIE={z.get('x_cie', 0):.4f} | Y_CIE={z.get('y_cie', 0):.4f}\n"

                    ret1, jpeg_raw = cv2.imencode('.jpg', foto_em_memoria)
                    ret2, jpeg_proc = cv2.imencode('.jpg', frame_proc)
                    if ret1 and ret2:
                        guardar(guia=nome_padrao, tipo="t", img_data=jpeg_raw.tobytes(), txt_data=txt_info, img_res_data=jpeg_proc.tobytes())
                    # ==========================================
                    
                    servidor.send_manual_result(is_ok_final, dados, frame_proc, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_FOTO\n", cliente)

        elif cmd_limpo.startswith("CHECK_PADRAO"):
            try:
                partes = cmd_limpo.split("|")
                id_check = int(partes[1])
                if id_check in visao.pattern_db.patterns:
                    nome_atual = visao.pattern_db.patterns[id_check].name
                    servidor.send_message(f"OCUPADO|{nome_atual}\n", cliente)
                else:
                    servidor.send_message("LIVRE\n", cliente)
            except Exception as e:
                servidor.send_message("ERRO|CHECK_FALHOU\n", cliente)    

        elif cmd_limpo.startswith("PADRAO"):
            try:
                partes = cmd_limpo.split("|")
                id_alvo = int(partes[1])
                nome_alvo = partes[2]
                
                frame = camara.capture_frame()
                if frame is None:
                    servidor.send_message("ERRO|CAMERA_FALHOU\n", cliente)
                    return
                
                characteristics = visao.guide_detector.analyze_guide(frame)
                _, _, dados_zonas = visao._process_zone_segmentation(frame, characteristics)
                zonas_padrao = dados_zonas.get("zonas", [])

                success, msg = visao.add_new_standard(frame, name=nome_alvo, pattern_id=id_alvo)
                if success:
                    ret, jpeg_buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        img_bytes = jpeg_buffer.tobytes()
                        txt_padrao = f"--- NOVO PADRÃO MESTRE CRIADO ---\n"
                        txt_padrao += f"Nome: {nome_alvo}\n"
                        txt_padrao += f"Data de Criação: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        txt_padrao += "--- VALORES DE REFERÊNCIA GRAVADOS POR ZONA ---\n"
                        
                        for z in zonas_padrao:
                            txt_padrao += f"Zona {z.get('zona', '?')}: Brilho Base={z.get('brilho_medio', 0):.1f} | X_CIE={z.get('x_cie', 0):.4f} | Y_CIE={z.get('y_cie', 0):.4f}\n"
                        
                        guardar(guia=nome_alvo, tipo="p", img_data=img_bytes, txt_data=txt_padrao)

                        tamanho_img = len(jpeg_buffer.tobytes())
                        servidor.send_message(f"PADRAO_OK|{tamanho_img}\n", cliente)
                        time.sleep(0.05)
                        servidor.clients[cliente].sendall(jpeg_buffer.tobytes())
                    else:
                        servidor.send_message("ERRO|ENCODE_JPEG_FALHOU\n", cliente)
                else:
                    servidor.send_message(f"ERRO|{msg}\n", cliente)
            except Exception as e:
                servidor.send_message(f"ERRO|{str(e)}\n", cliente)

    servidor.on_command = tratar_comando

    try:
        threading.Thread(target=servidor.iniciar_servidor, daemon=True).start()
        print("[Sistema] Servidor ativo e pronto. À espera que o cliente VB conecte...")
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nA encerrar o sistema de forma segura...")
    finally:
        camara.release()
        plc.desligar()  
        servidor.fechar_servidor()

if __name__ == "__main__":
    iniciar_maquina()