import cv2
from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms

def iniciar_maquina():
    print("A iniciar módulos...")
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    servidor = ServerComms(ip="127.0.0.1", port=8080)
    
    try:
        servidor.aguardar_interface()
        
        foto_em_memoria = None 
        
        while True:
            comando = servidor.aguardar_comando()
            
            if comando is None:
                print("Ligação perdida. A aguardar nova ligação...")
                servidor.aguardar_interface()
                continue
            
            # WATCHDOG: O VB envia "PING" a cada 3 segundos para verificar
            # se a Raspberry Pi está viva. Responde imediatamente com "PONG".
            if comando == "PING":
                try:
                    servidor.conn.sendall("PONG".encode('utf-8'))
                except Exception as e:
                    print(f"[Watchdog] Erro ao responder PONG: {e}")

            # 1. MODO AUTOMÁTICO
            elif comando == "AUTO":
                frame = camara.capture_frame()
                if frame is not None:
                    is_ok, frame_proc, dados = visao.process_and_decide(frame)
                    servidor.send_auto_result(is_ok, frame_proc)

            # 2. MANUAL — Capturar imagem
            elif comando == "CAPTURAR":
                frame = camara.capture_frame()
                if frame is not None:
                    foto_em_memoria = frame
                    servidor.send_auto_result(True, frame)

            # 3. MANUAL — Processar imagem guardada em memória
            elif comando == "PROCESSAR":
                if foto_em_memoria is not None:
                    is_ok, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                    servidor.send_manual_result(is_ok, dados, frame_proc)
                else:
                    print("[Aviso] Tentativa de processar sem captura prévia.")
                    # Envia um resultado nulo para não bloquear o VB
                    servidor.conn.sendall("ERRO|SEM_FOTO".encode('utf-8'))

            # 4. CONFIGURAÇÃO — Guardar novo padrão
            elif comando == "PADRAO":
                frame = camara.capture_frame()
                if frame is not None:
                    visao.save_new_standard(frame)
                    servidor.conn.sendall("PADRAO_OK".encode('utf-8'))
                else:
                    servidor.conn.sendall("PADRAO_ERRO".encode('utf-8'))

    except KeyboardInterrupt:
        print("\nEncerrar sistema...")
    finally:
        camara.release()
        servidor.fechar_servidor()

if __name__ == "__main__":
    iniciar_maquina()