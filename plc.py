import socket

class PLCInterface:
    def _init_(self, ip_plc="172.20.10.2", porta_plc=5000):
        self.ip = ip_plc
        self.port = porta_plc
        self.testar_conexao() # Faz o teste logo ao arrancar!

    def testar_conexao(self):
        """Tenta dar um 'toque' na porta do PLC só para ver se ele está lá."""
        print(f"[PLC] A procurar o PLC no IP {self.ip}:{self.port}...")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0) # Espera no máximo 2 segundos
                s.connect((self.ip, self.port))
            print("[PLC] LIGAÇÃO ESTABELECIDA COM SUCESSO! ")
        except Exception as e:
            print(f"[Erro PLC] AVISO: PLC não encontrado na rede! Verifique o IP ou o cabo. ({e})")

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