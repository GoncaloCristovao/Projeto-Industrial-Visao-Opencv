import cv2
import time

class CameraHandler:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"[Erro Câmara] Não foi possível aceder à câmara {self.camera_id}.")
        else:
            print(f"[Câmara] Sensor iniciado com sucesso.")
            time.sleep(1) # Tempo para o sensor focar

    def capture_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret or frame is None:
            print("[Erro Câmara] Falha ao capturar a imagem.")
            return None
            
        return frame

    def release(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            print("[Câmara] Desligada com segurança.")