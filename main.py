import cv2
from camera import CameraHandler
from vision import VisionProcessor
from plc import PLCInterface
from server import ServerComms

class MainController:
    def __init__(self):
        self.camera = CameraHandler()
        self.vision = VisionProcessor()
        self.plc = PLCInterface()
        self.server = ServerComms("192.168.1.100", 5000)
        
        params = self.server.fetch_program_parameters()
        self.vision.set_parameters(params)

    def run_automatic_mode(self):
        print("\n--- A INICIAR MODO AUTOMÁTICO ---")
        while True:
            self.plc.wait_for_trigger()
            
            frame = self.camera.capture_frame()
            if frame is None: 
                continue
            
            is_ok, processed_img = self.vision.process_and_decide(frame)
            
            self.plc.send_result(is_ok)
            self.server.send_inspection_result(is_ok, "Dados de luminosidade recolhidos")
            
            # Mostra a imagem na HMI
            cv2.imshow("HMI - Visao do Operador", processed_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def shutdown(self):
        self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    sistema = MainController()
    try:
        sistema.run_automatic_mode()
    except KeyboardInterrupt:
        print("\nSistema encerrado pelo utilizador.")
        sistema.shutdown()