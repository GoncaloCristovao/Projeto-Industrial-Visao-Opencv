import socket

class PLCInterface:
    def __init__(self, ip_plc="192.168.54.251", porta_plc=5000):
        self.ip = ip_plc
        self.port = porta_plc

    def avaliar_peca_no_plc(self, id_padrao, zonas):
        try:
            str_segmentos = ""
            for z in zonas:
                x = z.get("x_cie", 0.333)
                y = z.get("y_cie", 0.333)
                lum = z.get("brilho_medio", 0)
                xp = z.get("xp_cie", 0.333) 
                yp = z.get("yp_cie", 0.333)
                lump = z.get("lump_padrao", lum)
                str_segmentos += f"|{x:.4f};{y:.4f};{lum:.1f};{xp:.4f};{yp:.4f};{lump:.1f}"

            mensagem = f"AVALIAR|{id_padrao}{str_segmentos}\n"

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                s.connect((self.ip, self.port))
                s.sendall(mensagem.encode('utf-8'))
                
                resposta = s.recv(1024).decode('utf-8').strip()
                print(f"[PLC] O PLC decidiu: {resposta}")
                return resposta 

        except Exception as e:
            print(f"[Erro PLC] Falha ao comunicar com o PLC: {e}")
            return "NOK"