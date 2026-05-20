import cv2
import time
import os
from pathlib import Path
from typing import List


class CameraHandler:
    """
    Câmara com Modo SIMULAÇÃO usando pasta de imagens.
    
    MODO REAL: Usa webcam ligada (quando disponível)
    MODO SIMULAÇÃO: Carrega imagens sequencialmente de uma pasta
    """
    
    def __init__(self, camera_id=0, simulation_mode=True, image_folder="imagens_teste"):
        """
        Args:
            camera_id: ID da câmara física (0 = webcam principal)
            simulation_mode: True = usar pasta de imagens, False = câmara real
            image_folder: Nome da pasta com as imagens de teste
        """
        self.camera_id = camera_id
        self.simulation_mode = simulation_mode
        self.image_folder = Path(image_folder)
        self.test_images: List[Path] = []
        self.current_image_index = 0
        self.cap = None
        
        if self.simulation_mode:
            print(f"[Câmara]  MODO SIMULAÇÃO ativado")
            self._load_test_images_from_folder()
        else:
            print(f"[Câmara]  Tentando ligar à câmara física (ID: {camera_id})...")
            try:
                self.cap = cv2.VideoCapture(self.camera_id)
                
                if not self.cap.isOpened():
                    print(f"[Câmara]  Câmara não disponível. A mudar para MODO SIMULAÇÃO...")
                    self.simulation_mode = True
                    self._load_test_images_from_folder()
                else:
                    print(f"[Câmara] Câmara física conectada com sucesso!")
                    time.sleep(1)  # Tempo para ajuste automático
            except Exception as e:
                print(f"[Câmara]  Erro ao aceder câmara: {e}")
                print("[Câmara]  A mudar automaticamente para MODO SIMULAÇÃO")
                self.simulation_mode = True
                self._load_test_images_from_folder()
    
    def _load_test_images_from_folder(self):
        """Carrega todas as imagens da pasta de teste"""
        # Cria a pasta se não existir
        if not self.image_folder.exists():
            self.image_folder.mkdir(parents=True, exist_ok=True)
            print(f"[Câmara]  Pasta '{self.image_folder}' criada.")
            print(f"[Câmara]  Coloque imagens de teste (.jpg, .png, .bmp) nesta pasta!")
            self.test_images = []
            return
        
        # Suporta JPG, PNG, BMP
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
        for ext in extensions:
            self.test_images.extend(sorted(self.image_folder.glob(ext)))
        
        if self.test_images:
            print(f"[Câmara]  {len(self.test_images)} imagens carregadas de '{self.image_folder}'")
            print(f"[Câmara]  Imagens encontradas:")
            for i, img_path in enumerate(self.test_images, 1):
                print(f"         {i}. {img_path.name}")
        else:
            print(f"[Câmara]  Nenhuma imagem encontrada em '{self.image_folder}'!")
            print(f"[Câmara]  Coloque ficheiros .jpg, .png ou .bmp na pasta!")
    
    def capture_frame(self):
        """
        Capta uma fotografia.
        
        MODO REAL: Captura da webcam
        MODO SIMULAÇÃO: Retorna próxima imagem da pasta (modo rotativo)
        """
        if self.simulation_mode:
            return self._capture_from_folder()
        else:
            return self._capture_from_camera()
    
    def _capture_from_camera(self):
        """Captura frame de câmara física"""
        if not self.cap or not self.cap.isOpened():
            print("[Câmara]  Câmara não está disponível")
            return None
        
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            print("[Câmara]  Falha ao capturar imagem da câmara")
            return None
        
        return frame
    
    def _capture_from_folder(self):
        """
        Carrega próxima imagem da pasta (modo rotativo).
        
        Quando chega ao fim da lista, volta ao início automaticamente.
        """
        if not self.test_images:
            print("[Câmara]  Nenhuma imagem disponível na pasta!")
            print(f"[Câmara] Coloque imagens em '{self.image_folder}'")
            return None
        
        # Carrega imagem atual
        img_path = self.test_images[self.current_image_index]
        frame = cv2.imread(str(img_path))
        
        if frame is None:
            print(f"[Câmara]  Erro ao carregar '{img_path.name}'")
            # Tenta próxima imagem
            self.current_image_index = (self.current_image_index + 1) % len(self.test_images)
            return self._capture_from_folder()  # Recursivo até encontrar válida
        
        print(f"[Câmara]  Imagem capturada: {img_path.name} ({self.current_image_index + 1}/{len(self.test_images)})")
        
        # Avança para próxima imagem (modo rotativo - quando chegar ao fim, volta ao início)
        self.current_image_index = (self.current_image_index + 1) % len(self.test_images)
        
        return frame
    
    def reset_image_index(self):
        """Reinicia o índice para a primeira imagem (útil para recomeçar testes)"""
        self.current_image_index = 0
        print("[Câmara]  Índice de imagens reiniciado para o início.")
    
    def get_current_image_name(self) -> str:
        """Retorna o nome da imagem atual (útil para debug)"""
        if self.simulation_mode and self.test_images:
            # -1 porque já avançou para a próxima
            idx = (self.current_image_index - 1) % len(self.test_images)
            return self.test_images[idx].name
        return "Câmara Real"
    
    def get_total_images(self) -> int:
        """Retorna o total de imagens disponíveis"""
        return len(self.test_images)
    
    def has_images(self) -> bool:
        """Verifica se há imagens disponíveis"""
        return len(self.test_images) > 0
    
    def release(self):
        """Liberta a câmara"""
        if self.simulation_mode:
            print("[Câmara]  Modo simulação encerrado.")
            print(f"[Câmara]  Total de imagens processadas: {self.current_image_index}")
        else:
            if self.cap and self.cap.isOpened():
                self.cap.release()
                print("[Câmara]  Câmara física desligada com segurança.")


# ============================================================================
# CÓDIGO DE TESTE (executar diretamente este ficheiro para testar)
# ============================================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTE DO MÓDULO CÂMARA (MODO SIMULAÇÃO)")
    print("="*70 + "\n")
    
    # Cria instância em modo simulação
    camera = CameraHandler(simulation_mode=True, image_folder="imagens_teste")
    
    if not camera.has_images():
        print("\n AVISO: Nenhuma imagem encontrada!")
        print("Por favor, coloque algumas imagens de teste na pasta 'imagens_teste'")
    else:
        print(f"\n {camera.get_total_images()} imagens prontas para teste")
        print("\nA capturar 5 imagens de exemplo...\n")
        
        for i in range(5):
            frame = camera.capture_frame()
            if frame is not None:
                print(f"   Frame {i+1}:  Capturado ({frame.shape[1]}x{frame.shape[0]} pixels)")
                time.sleep(0.5)  # Simula delay
            else:
                print(f"   Frame {i+1}: ✗ Falha")
    
    camera.release()
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70 + "\n")

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