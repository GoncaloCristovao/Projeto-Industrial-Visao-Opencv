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

        # PADRAO
        elif comando == "PADRAO":
            frame = camara.capture_frame()
            if frame is not None:
                visao.save_new_standard(frame)
                servidor.send_message("PADRAO_OK", cliente)
            else:
                servidor.send_message("PADRAO_ERRO", cliente)

    # liga o servidor ao main
    servidor.on_command = tratar_comando

    try:
        # 🔥 servidor corre numa thread separada
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