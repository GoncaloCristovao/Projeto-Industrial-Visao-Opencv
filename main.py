import cv2
import threading
import time
from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms
from plc import PLCInterface

plc = PLCInterface(ip_plc="192.168.1.100", porta_plc=5000)

def iniciar_maquina():
    print("A iniciar módulos...")
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    servidor = ServerComms(ip="127.0.0.1", port=8080)

    foto_em_memoria = None

    # função que trata comandos vindos do servidor
    def tratar_comando(cliente, comando):
        nonlocal foto_em_memoria

        print(f"[MAIN] {cliente} pediu: {comando}")

        # WATCHDOG
        if comando == "PING":
            servidor.send_message("PONG", cliente)

        # AUTO
        elif comando == "AUTO":
            frame = camara.capture_frame()
            if frame is not None:
                # 1. Visão lê os dados
                _, frame_proc, dados = visao.process_and_decide(frame)
                
                # 2. Extrai corretamente os dados para o PLC
                id_padrao = dados.get("padrão_selecionado", {}).get("id", 1) if isinstance(dados.get("padrão_selecionado"), dict) else 1
                zonas = dados.get("zonas", [])
                
                # 3. Pede ao PLC para decidir E GRAVA A RESPOSTA
                decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                is_ok_final = (decisao_plc == "OK")
                
                # 4. Envia a decisão DO PLC para a HMI
                servidor.send_auto_result(is_ok_final, frame_proc, destino=cliente)

        # CAPTURAR
        elif comando == "CAPTURAR":
            frame = camara.capture_frame()
            if frame is not None:
                foto_em_memoria = frame
                servidor.send_auto_result(True, frame, destino=cliente)

        # PROCESSAR
        elif comando == "PROCESSAR":
            if foto_em_memoria is not None:
                # 1. Visão lê os dados da memória
                _, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                
                # 2. Extrai corretamente os dados
                id_padrao = dados.get("padrão_selecionado", {}).get("id", 1) if isinstance(dados.get("padrão_selecionado"), dict) else 1
                zonas = dados.get("zonas", [])
                
                # 3. Pede ao PLC para decidir
                decisao_plc = plc.avaliar_peca_no_plc(id_padrao, zonas)
                is_ok_final = (decisao_plc == "OK")
                
                # 4. Envia a decisão do PLC e os dados para os gráficos da HMI
                servidor.send_manual_result(is_ok_final, dados, frame_proc, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_FOTO\n", cliente)

        # =======================================================
        # VERIFICAR SE O LUGAR ESTÁ OCUPADO (NOVO)
        # =======================================================
        elif comando.startswith("CHECK_PADRAO"):
            try:
                partes = comando.split("|")
                id_check = int(partes[1])
                
                # Vai ao dicionário ver se o ID já existe
                if id_check in visao.pattern_db.patterns:
                    nome_atual = visao.pattern_db.patterns[id_check].name
                    servidor.send_message(f"OCUPADO|{nome_atual}\n", cliente)
                else:
                    servidor.send_message("LIVRE\n", cliente)
            except Exception as e:
                print(f"[MAIN] Erro ao verificar padrão: {e}")
                servidor.send_message("ERRO|CHECK_FALHOU\n", cliente)    

        # PADRAO - Definir novo padrão na BD
        # Comando esperado: "PADRAO|ID|NOME"
        # Exemplo: "PADRAO|1|Guia_BMW"
        elif comando.startswith("PADRAO"):
            try:
                partes = comando.split("|")
                
                # Valida o parsing do comando
                if len(partes) < 3:
                    servidor.send_message("ERRO|FORMATO_INVALIDO", cliente)
                    return
                
                # Extrai ID e nome
                id_alvo = int(partes[1])
                nome_alvo = partes[2]
                
                # Validação de segurança
                if id_alvo < 1 or id_alvo > 12:
                    servidor.send_message("ERRO|ID_FORA_INTERVALO", cliente)
                    return
                
                print(f"[MAIN] Recebido comando de padrão: ID={id_alvo}, Nome={nome_alvo}")
                
                # Captura a frame e a adiciona como novo padrão
                frame = camara.capture_frame()
                
                if frame is None:
                    servidor.send_message("ERRO|CAMERA_FALHOU", cliente)
                    return
                
                # Chama a lógica de gravação da V2
                success, msg = visao.add_new_standard(frame, name=nome_alvo)
                
                if success:
                    print(f"[MAIN] Padrão gravado com sucesso: {msg}")
                    
                    # Codifica a imagem em JPEG
                    ret, jpeg_buffer = cv2.imencode('.jpg', frame)
                    
                    if ret:
                        tamanho_img = len(jpeg_buffer.tobytes())
                        
                        # Envia confirmação com tamanho da imagem
                        # Formato: "PADRAO_OK|{tamanho_imagem}\n"
                        cabecalho = f"PADRAO_OK|{tamanho_img}\n"
                        servidor.send_message(cabecalho, cliente)
                        
                        # Pequena pausa para garantir que o cabeçalho foi enviado
                        import time
                        time.sleep(0.05)
                        
                        # Envia os dados binários da imagem
                        try:
                            servidor.clients[cliente].sendall(jpeg_buffer.tobytes())
                        except Exception as e:
                            print(f"[MAIN] Erro ao enviar imagem JPEG: {e}")
                    else:
                        servidor.send_message("ERRO|ENCODE_JPEG_FALHOU", cliente)
                else:
                    print(f"[MAIN] Falha ao adicionar padrão: {msg}")
                    servidor.send_message(f"ERRO|{msg}", cliente)
            
            except ValueError:
                print("[MAIN] Erro: ID do padrão não é um número válido")
                servidor.send_message("ERRO|ID_NAO_NUMERICO", cliente)
            
            except Exception as e:
                print(f"[MAIN] Erro inesperado no comando PADRAO: {e}")
                servidor.send_message(f"ERRO|{str(e)}", cliente)

    # liga o servidor ao main
    servidor.on_command = tratar_comando

    try:
        # servidor corre numa thread separada
        threading.Thread(target=servidor.iniciar_servidor, daemon=True).start()

        print("[Sistema] Servidor iniciado. À espera de clientes...")

        # loop principal (mantém programa vivo sem queimar CPU)
        while True:
            time.sleep(1) 

    except KeyboardInterrupt:
        print("\nEncerrar sistema...")

    finally:
        camara.release()
        servidor.fechar_servidor()


if __name__ == "__main__":
    iniciar_maquina()