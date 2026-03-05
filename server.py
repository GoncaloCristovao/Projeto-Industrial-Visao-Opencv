class ServerComms:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        
    def fetch_program_parameters(self):
        return {"min_intensity": 120, "color_tolerance": 5}
        
    def send_inspection_result(self, is_ok, intensity_data):
        estado = "OK" if is_ok else "NOK"
        print(f"[Servidor TCP/IP] Registo guardado: {estado} | Dados: {intensity_data}")