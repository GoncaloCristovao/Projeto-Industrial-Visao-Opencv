import cv2

class CameraHandler:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        
    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Erro: Não foi possível capturar a imagem.")
            return None
        return frame

    def release(self):
        self.cap.release()