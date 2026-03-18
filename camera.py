from camera import CameraHandler
from vision import VisionProcessor
from server import ServerComms

def iniciar_maquina():
    # 1. Inicializa os componentes
    camara = CameraHandler(camera_id=0)
    visao = VisionProcessor()
    servidor = ServerComms(ip="127.0.0.1", port=8080)
    
    try:
        # 2. Fica à espera que o operador abra o Visual Basic e carregue na aba "Automático"
        servidor.aguardar_interface()
        
        while True:
            # 3. Fica à escuta do comando do Timer do Visual Basic
            comando = servidor.aguardar_comando()
            
            if comando == "TESTAR":
                # --- O CICLO DE INSPEÇÃO ---
                
                # Passo A: Tira a foto
                frame = camara.capture_frame()
                
                if frame is not None:
                    # Passo B: Analisa a luz/cor (CIE LAB)
                    is_ok, frame_processado = visao.process_and_decide(frame)
                    
                    # Passo C: Envia o resultado (OK/NOK) e a foto de volta para o VB
                    servidor.send_inspection_result(is_ok, frame_processado)
                else:
                    print("[Aviso] Falha ao capturar imagem da câmara.")
            
            elif comando is None:
                print("Ligação ao Visual Basic perdida. A aguardar que volte a ligar...")
                servidor.aguardar_interface()

    except KeyboardInterrupt:
        print("\nDesligar o sistema...")
    finally:
        # Garante que a câmara e a porta de rede são fechadas corretamente
        camara.release()
        servidor.fechar_servidor()

if __name__ == "__main__":
    iniciar_maquina()