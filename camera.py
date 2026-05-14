
import cv2
import os
import time

class CameraHandler:
    def __init__(self, folder_path="teste"):
        """
        Emulador de Câmara: Em vez de hardware, lê imagens de uma pasta.
        :param folder_path: Caminho para a pasta com as imagens (ex: imagens geradas pelo test_vision.py)
        """
        self.folder_path = folder_path
        self.image_files = []
        self.current_index = 0

        # Verifica se a pasta existe
        if not os.path.exists(self.folder_path):
            print(f"[Erro Câmara] A pasta '{self.folder_path}' não existe.")
            return

        # Lista apenas ficheiros de imagem (jpg, png, bmp)
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
        self.image_files = sorted([
            f for f in os.listdir(self.folder_path) 
            if f.lower().endswith(valid_extensions)
        ])

        if not self.image_files:
            print(f"[Erro Câmara] Nenhuma imagem encontrada em '{self.folder_path}'.")
        else:
            print(f"[Câmara Emulada] Encontradas {len(self.image_files)} imagens.")
            print(f"[Câmara Emulada] Modo de teste por pasta ativo.")
            time.sleep(1)

    def capture_frame(self):
        """Lê a próxima imagem da lista como se fosse um frame da câmara."""
        if not self.image_files:
            print("[Erro Câmara] Sem imagens para capturar.")
            return None
        
        # Obtém o caminho da imagem atual
        image_path = os.path.join(self.folder_path, self.image_files[self.current_index])
        frame = cv2.imread(image_path)

        if frame is None:
            print(f"[Erro Câmara] Falha ao ler a imagem: {image_path}")
            return None

        print(f"[Câmara Emulada] Capturado: {self.image_files[self.current_index]}")

        # Atualiza o índice para a próxima imagem (ciclo infinito)
        self.current_index = (self.current_index + 1) % len(self.image_files)
            
        return frame

    def release(self):
        """Simula o fecho da câmara."""
        print("[Câmara Emulada] Sessão de teste terminada.")

"""
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
"""