import cv2
import time
import numpy as np
from pathlib import Path

class CameraHandler:
    def __init__(self, camera_id=0):
        """
        Inicializa a câmara VIRTUAL para testes.
        Em vez de usar hardware, vai ler imagens da pasta 'ImagensPadrao'.
        """
        self.camera_id = camera_id
        print(f"[Câmara VIRTUAL] A iniciar modo de simulação...")

        # ==========================================================
        # CÓDIGO ORIGINAL (CÂMARA REAL) - COMENTADO PARA TESTES
        # ==========================================================
        # self.cap = cv2.VideoCapture(self.camera_id)
        # if not self.cap.isOpened():
        #     print(f"[Erro Câmara] Não foi possível aceder à câmara com ID {self.camera_id}. Verifique o cabo USB!")
        # else:
        #     print(f"[Câmara] Sensor iniciado com sucesso (ID: {self.camera_id}).")
        #     time.sleep(1)
        # ==========================================================

        # NOVO CÓDIGO: Carregar ficheiros da pasta "ImagensPadrao"
        pasta_script = Path(__file__).parent.absolute()
        pasta_imagens = pasta_script / "ImagensPadrao"
        
        if not pasta_imagens.exists():
            print(f"[Erro Câmara VIRTUAL] A pasta {pasta_imagens} não existe!")
            self.image_files = []
        else:
            # Procura ficheiros PNG e JPG na pasta
            self.image_files = list(pasta_imagens.glob("*.[pP][nN][gG]")) + list(pasta_imagens.glob("*.[jJ][pP][gG]"))
            self.image_files.sort() # Ordena por nome para ser previsível
            print(f"[Câmara VIRTUAL] Encontradas {len(self.image_files)} imagens para simulação.")

        self.current_index = 0 # Ponteiro para sabermos qual é a próxima foto a "tirar"

    def capture_frame(self):
        """
        Capta uma fotografia simulada.
        Sempre que a HMI ou o main.py pedem uma foto, entrega a próxima da pasta.
        """
        
        # ==========================================================
        # CÓDIGO ORIGINAL - COMENTADO PARA TESTES
        # ==========================================================
        # if not hasattr(self, 'cap') or not self.cap.isOpened():
        #     return None
        # ret, frame = self.cap.read()
        # if not ret or frame is None:
        #     print("[Erro Câmara] O sensor falhou ao capturar a imagem neste instante.")
        #     return None
        # return frame
        # ==========================================================

        # NOVO CÓDIGO: Simular a fotografia
        if len(self.image_files) == 0:
            print("[Erro Câmara VIRTUAL] Não há imagens na pasta para simular.")
            return None

        # Pequeno atraso para simular o tempo de foco/obturador de uma câmara real
        time.sleep(0.2) 

        # Lê a imagem atual da lista com proteção contra acentos no Windows
        caminho_imagem = self.image_files[self.current_index]
        
        # O Python lê os bytes, e o OpenCV descodifica a partir da memória
        array_bytes = np.fromfile(str(caminho_imagem), dtype=np.uint8)
        frame = cv2.imdecode(array_bytes, cv2.IMREAD_COLOR)
        
        if frame is not None:
            print(f"[Câmara VIRTUAL] 'CLICK!' Foto capturada: {caminho_imagem.name}")
        else:
            print(f"[Erro Câmara VIRTUAL] Falha ao ler a imagem: {caminho_imagem.name}")

        # Avança para a próxima foto. Se chegar ao fim da lista, volta à primeira! (Loop infinito)
        self.current_index = (self.current_index + 1) % len(self.image_files)

        return frame

    def release(self):
        """Desliga a câmara."""
        # ==========================================================
        # CÓDIGO ORIGINAL - COMENTADO PARA TESTES
        # ==========================================================
        # if hasattr(self, 'cap') and self.cap.isOpened():
        #     self.cap.release()
        #     print("[Câmara] Desligada com segurança.")
        # ==========================================================
        print("[Câmara VIRTUAL] Simulador Desligado.")