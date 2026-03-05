import cv2
import numpy as np

class VisionProcessor:
    def __init__(self):
        self.reference_params = {} 
        
    def set_parameters(self, params):
        self.reference_params = params

    def process_and_decide(self, frame):
        # Conversão para CIE L*a*b*
        lab_image = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        
        # Análise de Intensidade da luz
        intensidade_media = np.mean(l_channel)
        limite_minimo = self.reference_params.get("min_intensity", 100)
        
        if intensidade_media >= limite_minimo:
            resultado = True  # OK
        else:
            resultado = False # NOK
            
        return resultado, frame