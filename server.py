import socket
import cv2
import time

class ServerComms:
    def __init__(self, ip="127.0.0.1", port=8080):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar a porta imediatamente se reiniciar o programa
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)
        self.conn = None
        self.addr = None
        print(f"[Servidor TCP/IP] A escutar na porta {self.port}...")

    def aguardar_interface(self):
        """Bloqueia e espera que o Visual Basic se ligue."""
        print("[Servidor TCP/IP] A aguardar ligação do Visual Basic...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"[Servidor TCP/IP] Interface ligada com sucesso: {self.addr}")

    def aguardar_comando(self):
        """Espera por um comando do VB ('AUTO', 'MANUAL' ou 'PADRAO')."""
        if self.conn:
            try:
                data = self.conn.recv(1024)
                if data:
                    return data.decode('utf-8').strip()
            except Exception as e:
                print(f"[Servidor TCP/IP] Erro ao receber comando: {e}")
                self.conn = None
        return None

    def send_auto_result(self, is_ok, image_frame):
        """Envia o resultado simplificado e a foto para a Aba Automático."""
        estado = "OK" if is_ok else "NOK"
        if self.conn:
            try:
                # Converte a imagem real do OpenCV para JPG
                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                img_bytes = jpeg_buffer.tobytes()
                tam = len(img_bytes)
                
                # Cabeçalho: TIPO | ESTADO | TAMANHO (Ex: "AUTO|OK|45000")
                cabecalho = f"AUTO|{estado}|{tam}"
                self.conn.sendall(cabecalho.encode('utf-8'))
                
                time.sleep(0.05) # Pausa técnica para a rede não "encavalar" pacotes
                
                # Envia os bytes da fotografia real
                self.conn.sendall(img_bytes)
            except Exception as e:
                print(f"[Servidor TCP/IP] Erro de envio (Auto): {e}")
                self.conn = None

    def send_manual_result(self, is_ok, dados_cie, image_frame):
        """Envia o resultado detalhado, valores CIE e a foto para a Aba Manual."""
        estado = "OK" if is_ok else "NOK"
        if self.conn:
            try:
                # Converte a imagem real do OpenCV para JPG
                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                img_bytes = jpeg_buffer.tobytes()
                tam = len(img_bytes)
                
                # Extrai os dados do dicionário (se não existirem, envia 0)
                val_x = dados_cie.get("X", 0)
                val_y = dados_cie.get("Y", 0)
                val_lum = dados_cie.get("Lum", 0)
                
                # Cabeçalho: TIPO | ESTADO | X | Y | LUMINOSIDADE | TAMANHO
                cabecalho = f"MANUAL|{estado}|{val_x}|{val_y}|{val_lum}|{tam}"
                self.conn.sendall(cabecalho.encode('utf-8'))
                
                time.sleep(0.05)
                
                # Envia os bytes da fotografia real
                self.conn.sendall(img_bytes)
            except Exception as e:
                print(f"[Servidor TCP/IP] Erro de envio (Manual): {e}")
                self.conn = None

    def fechar_servidor(self):
        """Fecha as ligações de rede de forma segura."""
        if self.conn:
            self.conn.close()
        self.server_socket.close()
        print("[Servidor TCP/IP] Encerrado.")