import cv2
import threading
from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms

def iniciar_maquina():
    print("A iniciar módulos...")
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    servidor = ServerComms(ip="0.0.0.0", port=8080)

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
                is_ok, frame_proc, dados = visao.process_and_decide(frame)
                servidor.send_auto_result(is_ok, frame_proc, destino=cliente)

        # CAPTURAR
        elif comando == "CAPTURAR":
            frame = camara.capture_frame()
            if frame is not None:
                foto_em_memoria = frame
                servidor.send_auto_result(True, frame, destino=cliente)

        # PROCESSAR
        elif comando == "PROCESSAR":
            if foto_em_memoria is not None:
                is_ok, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                servidor.send_manual_result(is_ok, dados, frame_proc, destino=cliente)
            else:
                servidor.send_message("ERRO|SEM_FOTO", cliente)

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

        # loop principal vazio (mantém programa vivo)
        while True:
            pass

    except KeyboardInterrupt:
        print("\nEncerrar sistema...")

    finally:
        camara.release()
        servidor.fechar_servidor()


if __name__ == "__main__":
    iniciar_maquina()