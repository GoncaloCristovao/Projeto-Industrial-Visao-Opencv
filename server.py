import socket
import cv2
import time
import numpy as np # Adicionado para gerar uma imagem de teste

class ServerComms:
    def __init__(self, ip="127.0.0.1", port=8080):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)
        self.conn = None
        self.addr = None
        print(f"[Servidor TCP/IP] A escutar na porta {self.port}...")

    def aguardar_interface(self):
        print("[Servidor TCP/IP] A aguardar ligação do Visual Basic...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"[Servidor TCP/IP] Interface ligada com sucesso: {self.addr}")

    def aguardar_comando(self):
        if self.conn:
            try:
                data = self.conn.recv(1024)
                if data:
                    return data.decode('utf-8').strip()
            except Exception as e:
                print(f"[Servidor TCP/IP] Erro ao receber: {e}")
                self.conn = None
        return None

    def send_inspection_result(self, is_ok, image_frame):
        estado = "OK" if is_ok else "NOK"
        if self.conn:
            try:
                # 1. Converter imagem para JPG (comprime a imagem para enviar rápido)
                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                imagem_bytes = jpeg_buffer.tobytes()
                tamanho_imagem = len(imagem_bytes)
                
                # 2. Enviar o Cabeçalho
                cabecalho = f"{estado}|{tamanho_imagem}"
                self.conn.sendall(cabecalho.encode('utf-8'))
                
                # Pausa minúscula para o VB processar o texto antes de levar com a imagem
                time.sleep(0.05) 
                
                # 3. Enviar a imagem propriamente dita
                self.conn.sendall(imagem_bytes)
                print(f"[Servidor] Enviado: {estado} | Tamanho: {tamanho_imagem} bytes")
                
            except Exception as e:
                print(f"[Servidor TCP/IP] Erro ao enviar para o VB: {e}")
                self.conn = None

    def fechar_servidor(self):
        if self.conn:
            self.conn.close()
        self.server_socket.close()
        print("[Servidor TCP/IP] Encerrado.")

# --- CICLO PRINCIPAL DO PROGRAMA ---
if __name__ == "__main__":
    servidor = ServerComms()
    
    try:
        servidor.aguardar_interface() # O programa pausa aqui até o VB se ligar
        
        simular_peca_ok = True # Variável para testarmos OK e NOK alternados
        
        while True:
            comando = servidor.aguardar_comando()
            
            if comando == "TESTAR":
                # AQUI ENTRARIA A SUA CÂMARA (ex: frame = camera.get_frame())
                # Para testar agora, vamos gerar uma imagem (Verde = OK, Vermelho = NOK)
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                if simular_peca_ok:
                    frame[:] = (0, 255, 0) # Fundo Verde
                    cv2.putText(frame, "GUIA DE LUZ - OK", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    frame[:] = (0, 0, 255) # Fundo Vermelho
                    cv2.putText(frame, "GUIA DE LUZ - NOK (FALHA)", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Enviar o resultado para o VB
                servidor.send_inspection_result(simular_peca_ok, frame)
                
                # Alternar entre OK e NOK para o próximo teste para ver as labels a mudar
                simular_peca_ok = not simular_peca_ok 
                
            elif comando is None:
                # Se o VB for fechado, volta a esperar que ele abra
                print("Ligação perdida. A aguardar nova ligação...")
                servidor.aguardar_interface()
                
    except KeyboardInterrupt:
        servidor.fechar_servidor()