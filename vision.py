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
    
    """
class VisionProcessor:
    def __init__(self):
        # Parâmetros padrão (serão depois substituídos pelos do Servidor)
        self.reference_params = {
            "min_intensity": 100, # Intensidade mínima exigida (0 a 255)
            "roi_x": 100,         # Posição X do corte
            "roi_y": 200,         # Posição Y do corte
            "roi_w": 400,         # Largura da zona de inspeção
            "roi_h": 100          # Altura da zona de inspeção
        }

    def set_parameters(self, params):
        self.reference_params.update(params)

    def process_and_decide(self, frame):
        #Recebe a imagem da câmara, extrai a luminosidade e devolve OK/NOK.
        # 1. Definir a Região de Interesse (ROI)
        # Em vez de processar a imagem toda (pesado para o Raspberry Pi),
        # olhamos só para a zona onde o guia de luz assenta no molde.
        x = self.reference_params["roi_x"]
        y = self.reference_params["roi_y"]
        w = self.reference_params["roi_w"]
        h = self.reference_params["roi_h"]
        
        # Proteção caso a ROI seja maior que a imagem
        if y+h > frame.shape[0] or x+w > frame.shape[1]:
            print("Aviso: ROI fora dos limites da imagem!")
            return False, frame

        # Recorta a imagem (Cria a sub-imagem)
        roi = frame[y:y+h, x:x+w]

        # 2. Converter a ROI para CIE L*a*b*
        # O espaço Lab separa a Luminosidade (L) das cores (a, b)
        lab_image = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)

        # 3. Criar uma Máscara para ignorar o fundo escuro
        # Tudo o que tiver luminosidade abaixo de 30 (quase preto) é ignorado.
        # Assim, a média não é "puxada para baixo" pelo fundo da caixa escura.
        _, mascara_luz = cv2.threshold(l_channel, 30, 255, cv2.THRESH_BINARY)

        # 4. Calcular a Intensidade Média APENAS na zona acesa
        # cv2.mean devolve a média considerando apenas a zona da máscara
        media_luminosidade = cv2.mean(l_channel, mask=mascara_luz)[0]

        # 5. Tomar a Decisão (A peça tem luz suficiente?)
        limite_minimo = self.reference_params["min_intensity"]
        is_ok = media_luminosidade >= limite_minimo

        # 6. Desenhar Grafismos para a HMI (Interface)
        # Escolhe a cor da caixa: Verde se OK, Vermelho se NOK
        cor_caixa = (0, 255, 0) if is_ok else (0, 0, 255)
        texto_resultado = "OK" if is_ok else "NOK"
        
        # Desenha o retângulo na imagem original
        cv2.rectangle(frame, (x, y), (x+w, y+h), cor_caixa, 2)
        
        # Escreve os dados no ecrã para o operador ver
        info_texto = f"Estado: {texto_resultado} | Luz: {media_luminosidade:.1f} / {limite_minimo}"
        cv2.putText(frame, info_texto, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_caixa, 2)

        return is_ok, frame
    """