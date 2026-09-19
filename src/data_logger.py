import os
import re
from datetime import datetime

def guardar(guia, tipo, img_data, txt_data, img_res_data=None):
    """
    Guarda ficheiros de imagem (.jpg) e texto (.txt) com numeração automática.
    """
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # pasta_guia = os.path.join(base_dir, "Registos", guia)

    home_dir = os.path.expanduser("~")
    pasta_guia = os.path.join(home_dir, "Desktop", "Registos", guia)
    
    # 1. Verificar/Criar pasta
    if tipo == "p":
        if not os.path.exists(pasta_guia):
            os.makedirs(pasta_guia)
            print(f"[Logger] Nova pasta criada em: {pasta_guia}")
    elif tipo == "t":
        if not os.path.exists(pasta_guia):
            print(f"Erro: Nenhum padrão foi guardado para este guia ('{guia}').")
            return
    else:
        print("[Logger] Erro: Tipo inválido. Use 'p' ou 't'.")
        return

    # 2. Lógica do Contador
    proximo_id = obter_proximo_id(pasta_guia, tipo)
    
    # 3. Gerar Timestamp e Nomes de Ficheiro
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_nome = f"{tipo}_{proximo_id}_{guia}_{now}"

    try:
        # Guardar Imagem Principal (.jpg)
        with open(os.path.join(pasta_guia, f"{base_nome}_imagem.jpg"), "wb") as f:
            f.write(img_data)
        
        # Guardar Texto (Valores .txt)
        with open(os.path.join(pasta_guia, f"{base_nome}_valores.txt"), "w", encoding="utf-8") as f:
            f.write(txt_data)
        
        # Guardar Imagem de Resultados (.jpg) - apenas se tipo for 't'
        if tipo == "t" and img_res_data:
            with open(os.path.join(pasta_guia, f"{base_nome}_imagem_resultados.jpg"), "wb") as f:
                f.write(img_res_data)
        
        print(f"[Logger] Registado com sucesso: {base_nome}")

    except Exception as e:
        print(f"[Logger] Erro ao gravar ficheiros: {e}")

def obter_proximo_id(pasta, prefixo):
    ficheiros = os.listdir(pasta)
    numeros = []
    padrao = re.compile(rf"^{prefixo}_(\d+)_")
    
    for f in ficheiros:
        match = padrao.match(f)
        if match:
            numeros.append(int(match.group(1)))
    
    return max(numeros) + 1 if numeros else 1
