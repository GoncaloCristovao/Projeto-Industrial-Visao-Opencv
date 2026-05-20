import socket

class PLCInterface:
    def __init__(self, servidor_comms=None):
        """
        Agora o PLC é um cliente ligado ao nosso próprio servidor.
        Mantemos uma referência ao objeto de comunicação do servidor.
        """
        self.servidor = servidor_comms

    def garantir_ligacao(self):
        """
        Verifica se o cliente com identificação 'PLC' está conectado ao servidor.
        """
        if self.servidor is None:
            return False
        return "PLC" in self.servidor.clients

    def avaliar_peca_no_plc(self, id_padrao, zonas):
        """
        Envia os dados da peça ao PLC através da ligação TCP ativa no servidor
        e aguarda imediatamente a decisão final (OK ou NOK).
        """
        try:
            if not self.garantir_ligacao():
                print("[Erro PLC] O cliente 'PLC' não se encontra conectado ao servidor.")
                return "NOK"

            # Obtém a socket do cliente PLC ativo no servidor
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

            print(f"[PLC] A enviar dados para avaliação...")
            # Envia o pedido de avaliação para o VB.NET
            sock.sendall(mensagem.encode("utf-8"))

            # Bloqueia temporariamente à espera da resposta direta (OK ou NOK)
            resposta = sock.recv(1024).decode("utf-8").strip()

            if not resposta:
                print("[Erro PLC] Resposta vazia ou desconexão do PLC durante a avaliação.")
                return "NOK"

            print(f"[PLC] O PLC decidiu: {resposta}")
            return resposta

        except Exception as e:
            print(f"[Erro PLC] Falha crítica ao comunicar com o PLC: {e}")
            return "NOK"

    def desligar(self):
        """
        Mantido apenas por compatibilidade com a Main. 
        A desconexão real agora é tratada pelo encerramento do servidor.
        """
        print("[PLC] O fecho da ligação agora é gerido pelo servidor principal.")