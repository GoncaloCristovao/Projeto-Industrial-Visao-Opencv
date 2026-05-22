import cv2
import time
import os
import numpy as np
from pathlib import Path
from typing import List

print("[DEBUG INIT] A iniciar a leitura do módulo camera.py...")

# --- ADIÇÃO PARA SUPORTE RASPBERRY PI 5 ---
try:
    from picamera2 import Picamera2
    HAS_PICAMERA = True
    print("[DEBUG INIT] Biblioteca picamera2 importada com sucesso (Estamos num RPi 5!).")
except ImportError as e:
    HAS_PICAMERA = False
    print(f"[DEBUG INIT] Biblioteca picamera2 NAO encontrada ({e}). A assumir ambiente Windows/PC Clássico.")
# ------------------------------------------

class CameraHandler:
    """
    Câmara com Modo SIMULAÇÃO usando pasta de imagens.
    
    MODO REAL: Usa webcam ligada (ou Pi Camera no RPi 5, quando disponível)
    MODO SIMULAÇÃO: Carrega imagens sequencialmente de uma pasta
    """
    
    def __init__(self, camera_id=0, simulation_mode=True, image_folder="imagens_teste"):
        """
        Args:
            camera_id: ID da câmara física (0 = webcam principal)
            simulation_mode: True = usar pasta de imagens, False = câmara real
            image_folder: Nome da pasta com as imagens de teste
        """
        print(f"[DEBUG CÂMARA] A inicializar CameraHandler | Camera ID: {camera_id} | Simulação: {simulation_mode}")
        
        self.camera_id = camera_id
        self.simulation_mode = simulation_mode
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.image_folder = Path(base_path) / image_folder
        self.test_images: List[Path] = []
        self.current_image_index = 0
        self.cap = None
        self.uso_picamera = False  # Nova flag para saber se estamos a usar o Pi 5
        
        if self.simulation_mode:
            print("[Câmara] MODO SIMULAÇÃO ativado desde o início.")
            self._load_test_images_from_folder()
        else:
            print(f"[Câmara] Tentando ligar à câmara física (ID: {camera_id})...")
            try:
                # SE FOR UM RASPBERRY PI 5 E TIVER CÂMARA OFICIAL:
                if HAS_PICAMERA:
                    print("[DEBUG CÂMARA] A tentar iniciar o motor Picamera2 (RPi 5)...")
                    self.picam2 = Picamera2()
                    # Forçamos o conversor do Pi a entregar a imagem a 8-bits (BGR)
                    print("[DEBUG CÂMARA] A configurar pipeline BGR888 a 1280x720...")
                    config = self.picam2.create_preview_configuration(main={"size": (1280, 720), "format": "BGR888"})
                    self.picam2.configure(config)
                    self.picam2.start()
                    self.uso_picamera = True
                    print("[Câmara] Câmara física conectada com sucesso (via libcamera)!")
                    time.sleep(1)
                
                # SE FOR UM PC NORMAL OU WEBCAM USB:
                else:
                    print(f"[DEBUG CÂMARA] A tentar aceder via OpenCV Clássico na porta {self.camera_id}...")
                    self.cap = cv2.VideoCapture(self.camera_id)
                    
                    if not self.cap.isOpened():
                        print(f"[Câmara] OpenCV falhou ao abrir a porta {self.camera_id}. A mudar para MODO SIMULAÇÃO...")
                        self.simulation_mode = True
                        self._load_test_images_from_folder()
                    else:
                        print(f"[Câmara] Câmara OpenCV física conectada com sucesso!")
                        time.sleep(1)  # Tempo para ajuste automático
            except Exception as e:
                print(f"[Câmara] Erro fatal ao aceder à câmara: {e}")
                print("[DEBUG CÂMARA] Traceback do erro capturado. A forçar MODO SIMULAÇÃO.")
                self.simulation_mode = True
                self._load_test_images_from_folder()
    
    def _load_test_images_from_folder(self):
        """Carrega todas as imagens da pasta de teste"""
        print(f"[DEBUG SIMULAÇÃO] A procurar imagens na pasta: {self.image_folder}")
        
        # Cria a pasta se não existir
        if not self.image_folder.exists():
            self.image_folder.mkdir(parents=True, exist_ok=True)
            print(f"[Câmara] Pasta '{self.image_folder}' criada.")
            print(f"[Câmara] Coloque imagens de teste (.jpg, .png, .bmp) nesta pasta!")
            self.test_images = []
            return
        
        # Suporta JPG, PNG, BMP
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
        for ext in extensions:
            self.test_images.extend(sorted(self.image_folder.glob(ext)))
        
        if self.test_images:
            print(f"[Câmara] {len(self.test_images)} imagens carregadas de '{self.image_folder}'")
        else:
            print(f"[Câmara] Nenhuma imagem encontrada em '{self.image_folder}'!")
            print(f"[Câmara] Coloque ficheiros .jpg, .png ou .bmp na pasta!")
    
    def capture_frame(self):
        """
        Capta uma fotografia.
        """
        if self.simulation_mode:
            return self._capture_from_folder()
        else:
            return self._capture_from_camera()
    
    def _capture_from_camera(self):
        """Captura frame de câmara física"""
        if self.uso_picamera:
            # O Pi 5 tira a foto e já entrega a matriz de 8-bits
            try:
                frame = self.picam2.capture_array()
                # print("[DEBUG CAPTURA] Frame PiCamera2 capturado com sucesso.") # Descomenta se quiseres spam no terminal a cada frame
                return frame
            except Exception as e:
                print(f"[Câmara] Falha ao capturar imagem da Picamera2: {e}")
                return None
        else:
            # OpenCV Clássico
            if not self.cap or not self.cap.isOpened():
                print("[DEBUG CAPTURA] OpenCV reporta que a câmara não está aberta.")
                return None
            
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                print("[DEBUG CAPTURA] O OpenCV fez .read() mas recebeu False ou None.")
                return None
            
            return frame
    
    def _capture_from_folder(self):
        """
        Carrega próxima imagem da pasta (modo rotativo).
        """
        if not self.test_images:
            print("[Câmara] Nenhuma imagem disponível na pasta de simulação!")
            return None
        
        # Carrega imagem atual
        img_path = self.test_images[self.current_image_index]
        frame = cv2.imdecode(np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR)        
        
        if frame is None:
            print(f"[DEBUG SIMULAÇÃO] Falha crítica do OpenCV ao tentar decodificar '{img_path.name}'")
            # Tenta próxima imagem
            self.current_image_index = (self.current_image_index + 1) % len(self.test_images)
            return self._capture_from_folder()  # Recursivo até encontrar válida
        
        # Avança para próxima imagem
        self.current_image_index = (self.current_image_index + 1) % len(self.test_images)
        return frame
    
    def reset_image_index(self):
        self.current_image_index = 0
        print("[Câmara] Índice de imagens reiniciado para o início.")
    
    def get_current_image_name(self) -> str:
        if self.simulation_mode and self.test_images:
            idx = (self.current_image_index - 1) % len(self.test_images)
            return self.test_images[idx].name
        return "Câmara Real"
    
    def get_total_images(self) -> int:
        return len(self.test_images)
    
    def has_images(self) -> bool:
        return len(self.test_images) > 0
    
    def release(self):
        print("[DEBUG] A libertar recursos da câmara...")
        if self.simulation_mode:
            print("[Câmara] Modo simulação encerrado.")
        else:
            if self.uso_picamera:
                self.picam2.stop()
                print("[Câmara] Câmara física do RPi 5 desligada com segurança.")
            elif self.cap and self.cap.isOpened():
                self.cap.release()
                print("[Câmara] Câmara física desligada com segurança.")


# ============================================================================
# CÓDIGO DE TESTE DIRECTO
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTE DO MÓDULO CÂMARA (MODO SIMULAÇÃO)")
    print("="*70 + "\n")
    
    camera = CameraHandler(simulation_mode=True, image_folder="imagens_teste")
    
    if not camera.has_images():
        print("\nAVISO: Nenhuma imagem encontrada!")
    else:
        print(f"\n{camera.get_total_images()} imagens prontas para teste")
        print("\nA capturar 3 imagens de exemplo...\n")
        
        for i in range(3):
            frame = camera.capture_frame()
            if frame is not None:
                print(f"   Frame {i+1}: Capturado com sucesso! Resolução: {frame.shape[1]}x{frame.shape[0]}")
                time.sleep(0.5)
            else:
                print(f"   Frame {i+1}: ✗ Falha")
    
    camera.release()
    print("\n" + "="*70)