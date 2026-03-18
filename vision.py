import cv2
import os 

class VisionProcessor:
    def __init__(self):
        # Nome do ficheiro onde vamos gravar o guia de luz perfeito
        self.caminho_padrao = "guia_luz_padrao.jpg" 
        
        # Tenta carregar o padrão existente ao iniciar o programa
        if os.path.exists(self.caminho_padrao):
            self.imagem_padrao = cv2.imread(self.caminho_padrao)
            print("[Visão] Padrão existente carregado do disco.")
        else:
            self.imagem_padrao = None
            print("[Visão] Aviso: Nenhum padrão guardado no disco. Precisa de configurar um!")

    # ... (outras funções como set_parameters, process_and_decide ...) ...

    def save_new_standard(self, frame):
        """
        Recebe a foto crua da câmara, guarda-a num ficheiro e atualiza o padrão na memória.
        """
        if frame is not None:
            try:
                # 1. Usa o OpenCV para gravar a foto no formato JPG real
                # Isto garante que o padrão persiste mesmo se a máquina for desligada
                sucesso = cv2.imwrite(self.caminho_padrao, frame)
                
                if sucesso:
                    # 2. Atualiza a "memória RAM" do Python para as próximas comparações
                    self.imagem_padrao = frame.copy()
                    print(f"[Visão] NOVO PADRÃO INDUSTRIAL GUARDADO: {self.caminho_padrao}")
                else:
                    print("[Visão] Erro técnico ao gravar o ficheiro JPG no disco.")
                    
            except Exception as e:
                print(f"[Visão] Erro ao guardar novo padrão: {e}")