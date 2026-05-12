import socket
import threading
import cv2
import time

class ServerComms:
    def __init__(self, ip="127.0.0.1", port=8080):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.clients = {}
        self.on_command = None
        print(f"[Servidor TCP/IP] A escutar em {self.ip}:{self.port}...")

    def iniciar_servidor(self):
        print("[Servidor TCP/IP] A aguardar clientes...")
        while True:
            try:
                conn, addr = self.server_socket.accept()
                print(f"[Servidor TCP/IP] Cliente ligado: {addr}...")
                threading.Thread(target=self.registar_cliente, args=(conn, addr), daemon=True).start()
            except OSError:
                break

    def registar_cliente(self, conn, addr):
        try:
            tipo = conn.recv(1024).decode('utf-8').strip()
            self.clients[tipo] = conn
            self.lidar_cliente(conn, tipo)
        except Exception as e:
            print(f"[Servidor TCP/IP] Erro ao registar: {e}")

    def lidar_cliente(self, conn, tipo):
        while True:
            try:
                data = conn.recv(1024)
                if not data: break
                comando = data.decode('utf-8').strip()
                if self.on_command: self.on_command(tipo, comando)
            except Exception as e:
                break
        conn.close()
        if tipo in self.clients: del self.clients[tipo]

    def send_auto_result(self, is_ok, image_frame, destino="VB"):
        estado = "OK" if is_ok else "NOK"
        if destino in self.clients:
            conn = self.clients[destino]
            try:
                if image_frame is None:
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
                conn.close()
                del self.clients[destino]

    def send_manual_result(self, is_ok, dados_cie, image_frame, destino="VB"):
        estado = "OK" if is_ok else "NOK"
        if destino in self.clients:
            conn = self.clients[destino]
            try:
                if image_frame is None:
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
                conn.close()
                del self.clients[destino]

    def send_message(self, mensagem, destino):
        if destino in self.clients:
            try:
                if not mensagem.endswith('\n'): mensagem += '\n'
                self.clients[destino].sendall(mensagem.encode('utf-8'))
            except: pass

    def fechar_servidor(self):
        for conn in self.clients.values(): conn.close()
        self.server_socket.close()