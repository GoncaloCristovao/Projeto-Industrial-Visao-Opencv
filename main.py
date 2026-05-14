import cv2
import threading
import time
from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms
from plc import PLCInterface

plc = PLCInterface(ip_plc="192.168.54.251", porta_plc=5000)

def iniciar_maquina():
    print("A iniciar módulos...")
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    servidor = ServerComms(ip="0.0.0.0", port=8080)

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
                zonas = dados.get("zonas", [])
                
                decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                is_ok_final = (decisao_plc == "OK")
                
                servidor.send_auto_result(is_ok_final, frame_proc, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_IMAGEM\n", cliente)

        elif cmd_limpo == "CAPTURAR":
            frame = camara.capture_frame()
            if frame is not None:
                foto_em_memoria = frame
                servidor.send_auto_result(True, frame, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_IMAGEM\n", cliente)

        elif cmd_limpo == "PROCESSAR":
            if foto_em_memoria is not None:
                _, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                id_padrao = dados.get("padrão_selecionado", {}).get("id", 1) if isinstance(dados.get("padrão_selecionado"), dict) else 1
                zonas = dados.get("zonas", [])
                
                decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                is_ok_final = (decisao_plc == "OK")
                
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
                
                success, msg = visao.add_new_standard(frame, name=nome_alvo, pattern_id=id_alvo)
                if success:
                    ret, jpeg_buffer = cv2.imencode('.jpg', frame)
                    if ret:
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
        print("[Sistema] Servidor iniciado. À espera de clientes...")
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print("\nEncerrar sistema...")
    finally:
        camara.release()
        servidor.fechar_servidor()

if __name__ == "__main__":
    iniciar_maquina()