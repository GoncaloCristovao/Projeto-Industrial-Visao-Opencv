import socket

class PLCInterface:
    def __init__(self, ip_plc="192.168.1.100", porta_plc=5000):
        """
        Define o IP e a Porta onde o programa VB.NET do teu colega (PLC) está à escuta.
        """
        self.ip = ip_plc
        self.port = porta_plc

    def avaliar_peca_no_plc(self, id_padrao, zonas):
        """
        Constrói a string de valores, envia para o PLC e devolve a decisão final.
        """
        try:
            # 1. Constrói a string com os valores exatos de cada segmento
            # Formato: X;Y;Lum;Xp;Yp;Lump
            str_segmentos = ""
            for z in zonas:
                x = z.get("x_cie", 0.333)
                y = z.get("y_cie", 0.333)
                lum = z.get("brilho_medio", 0)
                xp = z.get("xp_cie", 0.333) 
                yp = z.get("yp_cie", 0.333)
                lump = z.get("lump_padrao", lum)
                
                str_segmentos += f"|{x:.4f};{y:.4f};{lum:.1f};{xp:.4f};{yp:.4f};{lump:.1f}"

            # A mensagem que vai para o PLC: AVALIAR|ID_PADRAO|Seg1|Seg2...
            mensagem = f"AVALIAR|{id_padrao}{str_segmentos}\n"

            # 2. Liga-se ao PLC, envia e espera a resposta
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0) # Espera no máximo 5 segundos pela resposta do PLC
                s.connect((self.ip, self.port))
                s.sendall(mensagem.encode('utf-8'))
                
                # O PLC do teu colega tem de responder apenas "OK\n" ou "NOK\n"
                resposta = s.recv(1024).decode('utf-8').strip()
                
                print(f"[PLC] O PLC decidiu: {resposta}")
                return resposta # Retorna "OK" ou "NOK"

        except Exception as e:
            print(f"[Erro PLC] Falha ao comunicar com o PLC: {e}")
            # Em caso de falha de segurança (cabo desligado), assume NOK para não enviar lixo
            return "NOK"