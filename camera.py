import cv2
import time

class CameraHandler:
    def __init__(self, camera_id=0):
        """
        Inicializa a ligação à câmara. 
        O ID 0 é normalmente a webcam principal ou a primeira câmara USB ligada.
        """
        self.camera_id = camera_id
        # Tenta ligar à câmara através do OpenCV
        self.cap = cv2.VideoCapture(self.camera_id)
        
        # Verificação de segurança industrial vital: a câmara abriu mesmo?
        if not self.cap.isOpened():
            print(f"[Erro Câmara] Não foi possível aceder à câmara com ID {self.camera_id}. Verifique o cabo USB!")
        else:
            print(f"[Câmara] Sensor iniciado com sucesso (ID: {self.camera_id}).")
            # Pequena pausa (1 seg) para dar tempo ao sensor de ajustar o brilho automático e focar
            time.sleep(1)

    def capture_frame(self):
        #Capta uma única fotografia (frame) e devolve-a.
        
        if not self.cap.isOpened():
            return None
            
        # Tira a foto
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            print("[Erro Câmara] O sensor falhou ao capturar a imagem neste instante.")
            return None
            
        return frame

    def release(self):
        # Liberta a câmara para que outros programas a possam usar quando fecharmos o nosso.
        
        if self.cap.isOpened():
            self.cap.release()
            print("[Câmara] Desligada com segurança.")