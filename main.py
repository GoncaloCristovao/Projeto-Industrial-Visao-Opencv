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
        
        # Variável fundamental para separar o "Capturar" do "Processar" no Modo Manual
        foto_em_memoria = None 
        
        while True:
            comando = servidor.aguardar_comando()
            
            if comando is None:
                print("Ligação perdida. A aguardar...")
                servidor.aguardar_interface()
                continue
                
            # 1. ABA AUTOMÁTICO (Capta, processa e devolve OK/NOK e a foto)
            if comando == "AUTO":
                frame = camara.capture_frame()
                if frame is not None:
                    # O vision processa e devolve se está OK e os dados (ignoramos os dados no Auto)
                    is_ok, frame_proc, dados = visao.process_and_decide(frame)
                    servidor.send_auto_result(is_ok, frame_proc)

            # 2. ABA MANUAL -> BOTÃO "CAPTURAR IMAGEM" (Apenas tira a foto e guarda na memória)
            elif comando == "CAPTURAR":
                frame = camara.capture_frame()
                if frame is not None:
                    foto_em_memoria = frame # Guarda a foto na memória RAM!
                    
                    # Usamos o send_auto_result porque ele envia apenas a imagem limpa para o ecrã
                    # (Não precisamos de mandar valores matemáticos ainda)
                    servidor.send_auto_result(True, frame)

            # 3. ABA MANUAL -> BOTÃO "PROCESSAR TESTE" (Vai à memória e faz a matemática)
            elif comando == "PROCESSAR":
                if foto_em_memoria is not None:
                    # Vai buscar a foto à variável e aplica o OpenCV
                    is_ok, frame_proc, dados = visao.process_and_decide(foto_em_memoria)
                    
                    # Agora sim, envia o resultado com os dados CIE xyY
                    servidor.send_manual_result(is_ok, dados, frame_proc)
                else:
                    print("[Aviso] O operador tentou processar sem capturar uma foto primeiro.")

            # 4. ABA CONFIGURAÇÃO / PADRÃO (Guarda a imagem atual como referência)
            elif comando == "PADRAO":
                frame = camara.capture_frame()
                if frame is not None:
                    # Manda o vision guardar esta foto como a nova imagem perfeita
                    visao.save_new_standard(frame) 
                    # Responde ao Visual Basic que correu tudo bem
                    servidor.conn.sendall("PADRAO_OK".encode('utf-8'))

    except KeyboardInterrupt:
        print("\nEncerrar sistema...")
    finally:
        # Libertar os recursos físicos
        camara.release()
        servidor.fechar_servidor()

if __name__ == "__main__":
    iniciar_maquina()