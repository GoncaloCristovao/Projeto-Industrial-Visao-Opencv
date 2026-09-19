import socket
import threading
import cv2
import time

class ServerComms:
    def __init__(self, ip="0.0.0.0", port=5000):
        self.ip = ip
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar a porta imediatamente se reiniciar o programa
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)  # Permite até 5 conexões pendentes
        
        self.clients = {}
        self.on_command = None # Iniciar sem callback definido para garantir integridade

        print(f"[Servidor TCP/IP] À escuta em {self.ip}:{self.port}...")

    def iniciar_servidor(self):
        print("[Servidor TCP/IP] A aguardar clientes...")
        while True:
            conn, addr = self.server_socket.accept()
            print(f"[Servidor TCP/IP] Nova conexão estabelecida a partir de: {addr}")
            
            threading.Thread(target=self.registar_cliente, args=(conn, addr)).start()

    def registar_cliente(self, conn, addr):
        try:
            # Aguarda a string de identificação (A HMI em VB envia "PLC" logo após o Connect)
            tipo = conn.recv(1024).decode('utf-8').strip()  
            print(f"[Servidor TCP/IP] Cliente identificado com sucesso como: {tipo}")

            self.clients[tipo] = conn

            self.lidar_cliente(conn, tipo)
        except Exception as e:
            print(f"[Servidor TCP/IP] Erro ao registar cliente de {addr}: {e}")

    def lidar_cliente(self, conn, tipo):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                comando = data.decode('utf-8').strip()
                print(f"[{tipo}] Comando recebido: {comando}")

                # Encaminha o comando para processamento na Main
                if self.on_command:
                    self.on_command(tipo, comando)

            except Exception as e:
                print(f"[Servidor TCP/IP] Erro na ligação com o cliente {tipo}: {e}")
                break

        print(f"[Servidor TCP/IP] Cliente {tipo} desligado.")
        conn.close()
        if tipo in self.clients:
            del self.clients[tipo]

    def send_auto_result(self, is_ok, image_frame, destino="PLC"):
        """Envia o resultado simplificado e a foto para a Aba Automático."""
        estado = "OK" if is_ok else "NOK"
        if destino in self.clients:
            conn = self.clients[destino]

            try:
                if image_frame is None:
                    print("[Servidor] Frame inválido (AUTO)")
                    self.send_message("ERRO|FRAME_INVALIDO\n", destino) 
                    return

                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                img_bytes = jpeg_buffer.tobytes()
                tam = len(img_bytes)

                cabecalho = f"AUTO|{estado}|{tam}\n" 
                conn.sendall(cabecalho.encode('utf-8'))

                time.sleep(0.05)
                conn.sendall(img_bytes)

            except Exception as e:
                print(f"[Servidor TCP/IP] Erro no envio AUTO para {destino}: {e}")
                conn.close()
                if destino in self.clients: del self.clients[destino]

    def send_manual_result(self, is_ok, dados_cie, image_frame, destino="PLC"):
        """Envia o resultado detalhado, valores CIE por segmento e a foto para a Aba Manual."""
        estado = "OK" if is_ok else "NOK"
        if destino in self.clients:
            conn = self.clients[destino]

            try:
                if image_frame is None:
                    print("[Servidor] Frame inválido (MANUAL)")
                    self.send_message("ERRO|FRAME_INVALIDO\n", destino)
                    return

                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                img_bytes = jpeg_buffer.tobytes()
                tam = len(img_bytes)

                zonas = dados_cie.get("zonas", [])
                str_segmentos = ""
                
                for z in zonas:
                    x = z.get("x_cie", 0.333)
                    y = z.get("y_cie", 0.333)
                    lum = z.get("brilho_medio", 0)
                    xp = z.get("xp_cie", 0.333) 
                    yp = z.get("yp_cie", 0.333)
                    lump = z.get("lump_padrao", lum) 
                    
                    str_segmentos += f"|{x:.4f};{y:.4f};{lum:.1f};{xp:.4f};{yp:.4f};{lump:.1f}"

                cabecalho = f"MANUAL|{estado}{str_segmentos}|{tam}\n"
                conn.sendall(cabecalho.encode('utf-8'))

                time.sleep(0.05)
                conn.sendall(img_bytes)

            except Exception as e:
                print(f"[Servidor TCP/IP] Erro no envio MANUAL para {destino}: {e}")
                conn.close()
                if destino in self.clients: del self.clients[destino]

    def send_image_only(self, image_frame, tag="CAPTURAR", destino="PLC"):
        if destino in self.clients:
            conn = self.clients[destino]
            try:
                ret, jpeg_buffer = cv2.imencode('.jpg', image_frame)
                img_bytes = jpeg_buffer.tobytes()
                tam = len(img_bytes)
                
                cabecalho = f"{tag}|OK|{tam}\n"
                conn.sendall(cabecalho.encode('utf-8'))
                time.sleep(0.05)
                conn.sendall(img_bytes)
            except Exception as e:
                print(f"[Servidor] Erro ao enviar imagem pura: {e}")

    def send_message(self, mensagem, destino):
        if destino in self.clients:
            try:
                self.clients[destino].sendall(mensagem.encode('utf-8'))
            except:
                print(f"[Servidor TCP/IP] Falha ao enviar mensagem direta para {destino}")

    def fechar_servidor(self):
        for conn in self.clients.values():
            try: conn.close()
            except: pass
        try: self.server_socket.close()
        except: pass
        print("[Servidor TCP/IP] Encerrado com sucesso.")
