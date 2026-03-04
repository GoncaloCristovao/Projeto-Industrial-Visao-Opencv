import cv2
import numpy as np

# 1. Teste básico: Criar uma imagem e mostrar texto
print("A abrir janela de teste... Prime qualquer tecla para fechar.")
janela = np.zeros((300, 600, 3), dtype="uint8")
cv2.putText(janela, "Eng. Automacao - OpenCV OK!", (50, 150), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

cv2.imshow("Teste de Visao", janela)

cv2.waitKey(0)
cv2.destroyAllWindows()