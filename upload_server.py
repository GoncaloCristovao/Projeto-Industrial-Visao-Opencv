import os
import socket
import threading


class UploadServer:
    def _init_(self, ip="0.0.0.0", port=8081, pasta_destino="uploads"):
        self.ip = ip
        self.port = port
        self.pasta_destino = pasta_destino

        os.makedirs(self.pasta_destino, exist_ok=True)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)

        self.ultima_imagem_peca = None

        print(f"[UPLOAD] Servidor de upload ativo em {self.ip}:{self.port}")

    def iniciar(self):
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self._tratar_cliente, args=(conn, addr), daemon=True).start()

    def _tratar_cliente(self, conn, addr):
        try:
            print(f"[UPLOAD] Cliente ligado: {addr}")

            cabecalho = self._ler_linha(conn)
            print(f"[UPLOAD] Cabeçalho recebido: {cabecalho}")

            partes = cabecalho.split("|")
            if len(partes) != 4:
                conn.sendall(b"UPLOAD_ERRO")
                return

            comando, tipo, nome_ficheiro, tamanho_str = partes

            if comando != "UPLOAD" or tipo != "PECA":
                conn.sendall(b"UPLOAD_ERRO")
                return

            tamanho = int(tamanho_str)
            dados = self._ler_bytes(conn, tamanho)

            if len(dados) != tamanho:
                conn.sendall(b"UPLOAD_ERRO")
                return

            nome_final = f"peca_{nome_ficheiro}"
            caminho = os.path.join(self.pasta_destino, nome_final)

            with open(caminho, "wb") as f:
                f.write(dados)

            self.ultima_imagem_peca = caminho
            print(f"[UPLOAD] Nova imagem peça guardada: {caminho}")

            conn.sendall(b"UPLOAD_OK")

        except Exception as e:
            print(f"[UPLOAD] Erro: {e}")
            try:
                conn.sendall(b"UPLOAD_ERRO")
            except:
                pass
        finally:
            conn.close()

    def _ler_linha(self, conn):
        dados = b""
        while not dados.endswith(b"\n"):
            bloco = conn.recv(1)
            if not bloco:
                break
            dados += bloco
        return dados.decode("utf-8").strip()

    def _ler_bytes(self, conn, tamanho):
        dados = b""
        while len(dados) < tamanho:
            bloco = conn.recv(min(4096, tamanho - len(dados)))
            if not bloco:
                break
            dados += bloco
        return dados