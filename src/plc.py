import socket
import threading

class PLCInterface:
    def __init__(self, servidor_comms=None):
        self.servidor = servidor_comms
        self.ultima_decisao = "NOK"
        self.evento_resposta = threading.Event()

    def garantir_ligacao(self):
        if self.servidor is None:
            return False
        return "PLC" in self.servidor.clients

    def avaliar_peca_no_plc(self, id_padrao, zonas):
        try:
            if not self.garantir_ligacao():
                print("[Erro PLC] O cliente 'PLC' não se encontra conectado ao servidor.")
                return "NOK"

            sock = self.servidor.clients["PLC"]

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

            # Limpa o evento antes de enviar
            self.evento_resposta.clear()
            self.ultima_decisao = "NOK"

            print(f"[PLC] A enviar dados para avaliação...")
            sock.sendall(mensagem.encode("utf-8"))

            # Bloqueia (com timeout de 5s) até o main.py lhe dar ordem para avançar
            sucesso = self.evento_resposta.wait(timeout=5.0)
            
            if not sucesso:
                print("[Erro PLC] Timeout! O PLC não respondeu a tempo.")
                return "NOK"

            print(f"[PLC] O PLC decidiu: {self.ultima_decisao}")
            return self.ultima_decisao

        except Exception as e:
            print(f"[Erro PLC] Falha crítica ao comunicar com o PLC: {e}")
            return "NOK"

    def desligar(self):
        print("[PLC] O fecho da ligação agora é gerido pelo servidor principal.")
