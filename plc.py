import time

class PLCInterface:
    def __init__(self):
        pass
        
    def wait_for_trigger(self):
        print("A aguardar sinal de trigger do PLC...")
        time.sleep(2) 
        return True

    def send_result(self, is_ok):
        if is_ok:
            print(">>> SINAL PLC: Peça APROVADA (OK) <<<")
        else:
            print(">>> SINAL PLC: Peça REJEITADA (NOK) <<<")