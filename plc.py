import socket


class PLCInterface:
    def __init__(self, ip_plc="172.20.10.2", porta_plc=5000):
        self.ip = ip_plc
        self.port = porta_plc
        self.sock = None

        # Liga logo ao arrancar
        self.ligar()

    def ligar(self):
        """
        Estabelece uma ligação persistente ao PLC.
        Se já existir ligação válida, não faz nada.
        """
        if self.sock is not None:
            return True

        print(f"[PLC] A ligar ao PLC em {self.ip}:{self.port}...")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.ip, self.port))

            print("[PLC] Ligação persistente estabelecida com sucesso.")
            return True

        except Exception as e:
            print(f"[Erro PLC] Não foi possível ligar ao PLC: {e}")
            self.sock = None
            return False

    def desligar(self):
        """
        Fecha a ligação persistente ao PLC.
        """
        if self.sock is not None:
            try:
                self.sock.close()
                print("[PLC] Ligação ao PLC encerrada.")
            except Exception as e:
                print(f"[Erro PLC] Erro ao fechar ligação: {e}")
            finally:
                self.sock = None

    def garantir_ligacao(self):
        """
        Garante que existe ligação ao PLC.
        Se a socket tiver caído, tenta voltar a ligar.
        """
        if self.sock is None:
            return self.ligar()
        return True

    def avaliar_peca_no_plc(self, id_padrao, zonas):
        """
        Envia os dados da peça ao PLC através da ligação persistente
        e devolve a decisão final.
        """
        try:
            if not self.garantir_ligacao():
                return "NOK"

            str_segmentos = ""
            for z in zonas:
                x = z.get("x_cie", 0.333)
                y = z.get("y_cie", 0.333)
                lum = z.get("brilho_medio", 0)
                xp = z.get("xp_cie", 0.333)
                yp = z.get("yp_cie", 0.333)
                lump = z.get("lump_padrao", lum)

                str_segmentos += f"|{x:.4f};{y:.4f};{lum:.1f};{xp:.4f};{yp:.4f};{lump:.1f}"

            mensagem = f"AVALIAR|{id_padrao}{str_segmentos}"

            # envia pedido
            self.sock.sendall(mensagem.encode("utf-8"))

            # recebe resposta
            resposta = self.sock.recv(1024).decode("utf-8").strip()

            if not resposta:
                print("[Erro PLC] Resposta vazia do PLC.")
                self.desligar()
                return "NOK"

            print(f"[PLC] O PLC decidiu: {resposta}")
            return resposta

        except Exception as e:
            print(f"[Erro PLC] Falha ao comunicar com o PLC: {e}")

            # Se houver erro, fecha a socket para forçar reconnect na próxima tentativa
            self.desligar()
            return "NOK"