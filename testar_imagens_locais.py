import cv2
import json
from pathlib import Path
from vision import VisionProcessor

def executar_teste_local():
    print("=" * 60)
    print(" INICIANDO TESTE COM IMAGENS LOCAIS (SEM CÂMARA)")
    print("=" * 60)
    
    # Inicia a visão apontando para uma pasta de testes para não estragar a principal
    visao = VisionProcessor(db_path="pattern_database_teste")
    
    # Caminho para a tua pasta de imagens
    pasta_imagens = Path("ImagensPadrao")
    
    # Lista com as imagens que fizeste upload
    imagens_teste = [
        "Padrao_Guia_Luz_Continua.png",
        "Padrao_Guia_Luz_Segmentada_6.png",
        "Padrao_Guia_Luz_Segmentada_8.png",
        "Padrao_Guia_Luz_Segmentada_10.png"
    ]
    
    # Simular o Modo Operador: Gravar cada imagem num Slot
    for slot_id, nome_imagem in enumerate(imagens_teste, start=1):
        caminho_completo = pasta_imagens / nome_imagem
        
        if caminho_completo.exists():
            print(f"\n>> A ler imagem: {nome_imagem}")
            
            # Simula a câmara a tirar a foto (lê do disco)
            frame = cv2.imread(str(caminho_completo))
            
            # Pede à Visão para adicionar como um Novo Padrão no Slot definido
            nome_padrao = nome_imagem.replace(".png", "")
            sucesso, msg = visao.add_new_standard(frame, name=nome_padrao, pattern_id=slot_id)
            
            print(f"Resultado (Slot {slot_id}): {msg}")
        else:
            print(f"\n[ERRO] Imagem não encontrada: {caminho_completo}")

    # ==========================================================
    # VERIFICAÇÃO DO METADATA.JSON NO FINAL
    # ==========================================================
    caminho_json = Path("pattern_database_teste") / "metadata.json"
    
    print("\n" + "=" * 60)
    print(" VERIFICAR DADOS GUARDADOS NO METADATA.JSON")
    print("=" * 60)
    
    if caminho_json.exists():
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
            for pid, info in dados.items():
                nome = info.get("name")
                zonas = info.get("zone_profiles", [])
                
                print(f"\n[Padrão {pid}] - {nome}")
                print(f" -> A guia foi cortada em {len(zonas)} segmentos/fatias de estudo.")
                
                if len(zonas) > 0:
                    # Imprime a Zona 1 para confirmar os valores
                    z1 = zonas[0]
                    print(f" -> Zona 1: Brilho (Y) = {z1.get('brilho_medio')}, "
                          f"x = {z1.get('x_cie'):.4f}, y = {z1.get('y_cie'):.4f}")
    else:
        print("O ficheiro metadata.json não foi criado!")

if __name__ == "__main__":
    executar_teste_local()