"""
Script de Teste do Sistema de Padrões Múltiplos V2.0

Este script demonstra como usar o novo sistema de detecção inteligente,
múltiplos padrões e matching automático.

Executar: python test_vision.py
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Importar módulos do sistema
try:
    from vision import VisionProcessor
    from guide_detector import GuideCharacteristicDetector
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)


class TestVisionV2:
    """Testes do novo sistema de visão"""
    
    def __init__(self):
        self.vision = VisionProcessor(db_path="test_pattern_database")
        self.detector = GuideCharacteristicDetector(px_to_mm_ratio=0.1)
    
    def test_1_criar_padroes_sinteticos(self):
        print("\n" + "="*70)
        print("TESTE 1: Criar Padrões Sintéticos (Corrigido)")
        print("="*70)
        
        # Lista de testes para automatizar
        testes = [
            ("Guia_Continua_Standard", self._gerar_guia_continua(400, 80, 220), "Guia contínua"),
            ("Guia_Segmentada_8seg", self._gerar_guia_segmentada(8, 40, 400, 80), "8 segmentos"),
            ("Guia_Segmentada_10seg", self._gerar_guia_segmentada(10, 35, 400, 80), "10 segmentos")
        ]
        
        for nome, frame, desc in testes:
            print(f"\n[Processando] {nome}...")
            
            # Forçamos a análise antes de guardar para validar
            chars = self.vision.guide_detector.analyze_guide(frame)
            if chars.num_segments == 0 and not chars.is_continuous:
                print(f"  ✗ Erro: Detector não encontrou a guia no frame sintético.")
                continue
                
            success, msg = self.vision.add_new_standard(frame, name=nome, notes=desc)
            print(f"  Resultado: {'✓' if success else '✗'} {msg}")
        
        # Padrão 3: Guia Segmentada 10 segmentos
        print("\n[1.3] Criando padrão segmentado 10 segmentos...")
        frame_seg10 = self._gerar_guia_segmentada(
            num_segments=10,
            segment_spacing=35,
            width=400,
            height=80
        )
        success, msg = self.vision.add_new_standard(
            frame_seg10,
            name="Guia_Segmentada_10seg",
            notes="Guia com 10 segmentos espaçados 35px"
        )
        print(f"  Resultado: {'✓' if success else '✗'} {msg}")
        
        # Padrão 4: Guia Segmentada com espaçamento diferente
        print("\n[1.4] Criando padrão segmentado com espaçamento 50px...")
        frame_seg6_large = self._gerar_guia_segmentada(
            num_segments=6,
            segment_spacing=50,
            width=400,
            height=80
        )
        success, msg = self.vision.add_new_standard(
            frame_seg6_large,
            name="Guia_Segmentada_6seg_50px",
            notes="Guia com 6 segmentos, espaçamento maior"
        )
        print(f"  Resultado: {'✓' if success else '✗'} {msg}")
    
    def test_2_listar_padroes(self):
        """TESTE 2: Lista padrões disponíveis"""
        print("\n" + "="*70)
        print("TESTE 2: Listar Padrões Disponíveis")
        print("="*70)
        
        # CORREÇÃO: Chama o método diretamente pela pattern_db
        patterns = self.vision.pattern_db.list_patterns()
        
        if not patterns:
            print("  Nenhum padrão encontrado!")
            return
        
        print(f"\n  Total de padrões: {len(patterns)}")
        print("\n  ID | Nome                           | Tipo        | Segs | Tamanho")
        print("  " + "-"*70)
        
        for p in patterns:
            tipo = "Contínua" if p['type'] == "Contínua" else "Segmentada"
            segs = f"{p['segments']}" if p['segments'] > 0 else "-"
            tamanho = f"{p['width']}x{p['height']}"
            nome = p['name'][:25].ljust(25)
            
            print(f"  {p['id']:2d} | {nome} | {tipo:11s} | {segs:>4s} | {tamanho}")
    
    def test_3_analisar_caracteristicas(self):
        """TESTE 3: Analisa características de guias"""
        print("\n" + "="*70)
        print("TESTE 3: Analisar Características de Guias")
        print("="*70)
        
        test_cases = [
            ("Contínua OK", self._gerar_guia_continua(400, 80, 220)),
            ("Segmentada 8 OK", self._gerar_guia_segmentada(8, 40, 400, 80)),
            ("Segmentada com defeito", self._gerar_guia_segmentada(8, 40, 400, 80, com_defeito=True)),
        ]
        
        for name, frame in test_cases:
            print(f"\n[{name}]")
            characteristics = self.detector.analyze_guide(frame)
            
            print(f"  Tipo: {'Contínua' if characteristics.is_continuous else 'Segmentada'}")
            print(f"  Segmentos: {characteristics.num_segments}")
            print(f"  Espaçamento: {characteristics.segment_spacing_mm:.2f}mm")
            print(f"  Confiança: {characteristics.confidence:.3f}")
    
    def test_4_matching_e_comparacao(self):
        """TESTE 4: Matching e comparação com padrões"""
        print("\n" + "="*70)
        print("TESTE 4: Matching e Comparação com Padrões")
        print("="*70)
        
        print("\n[4.1] Testando guia segmentada 8 seg (deve dar match com padrão)")
        frame_test = self._gerar_guia_segmentada(8, 40, 400, 80, ruido=True)
        is_ok, frame_viz, dados = self.vision.process_and_decide(frame_test)
        
        print(f"  Resultado Final Calculado pela IA: {'✓ OK' if is_ok else '✗ NOK'}")
        print(f"  Padrão Reconhecido na BD: {dados.get('padrão_selecionado', {}).get('nome')}")
        print(f"  Quantidade de Zonas extraídas para a HMI: {len(dados.get('zonas', []))}")
        
        print("\n[4.2] Testando guia contínua (deve dar match com padrão contínuo)")
        frame_cont = self._gerar_guia_continua(400, 80, 215)
        is_ok, frame_viz, dados = self.vision.process_and_decide(frame_cont)
        
        print(f"  Resultado Final Calculado pela IA: {'✓ OK' if is_ok else '✗ NOK'}")
        print(f"  Padrão Reconhecido na BD: {dados.get('padrão_selecionado', {}).get('nome')}")
    
    def test_5_remocao_padrao(self):
        """TESTE 5: Remoção de padrão"""
        print("\n" + "="*70)
        print("TESTE 5: Remoção de Padrão")
        print("="*70)
        
        # CORREÇÃO: Usa a chamada correta para a DB
        patterns_antes = self.vision.pattern_db.list_patterns()
        print(f"\n  Padrões antes: {len(patterns_antes)}")
        
        if patterns_antes:
            pattern_para_remover = patterns_antes[-1]
            print(f"  Removendo: {pattern_para_remover['name']} (ID: {pattern_para_remover['id']})")
            
            # CORREÇÃO: Método correto delete_pattern
            success, msg = self.vision.pattern_db.delete_pattern(pattern_para_remover['id'])
            print(f"  Resultado: {'✓' if success else '✗'} {msg}")
            
            patterns_depois = self.vision.pattern_db.list_patterns()
            print(f"  Padrões depois: {len(patterns_depois)}")
    
    def test_6_edge_cases(self):
        """TESTE 6: Casos extremos"""
        print("\n" + "="*70)
        print("TESTE 6: Casos Extremos")
        print("="*70)
        
        print("\n[6.1] Imagem muito escura...")
        frame_escuro = self._gerar_guia_continua(400, 80, 50)
        is_ok, _, dados = self.vision.process_and_decide(frame_escuro)
        print(f"  Resultado: {'✓ OK' if is_ok else '✗ NOK'}")
        
        print("\n[6.2] Guia segmentada com defeito severo...")
        frame_defeito = self._gerar_guia_segmentada(8, 40, 400, 80, com_defeito=True)
        is_ok, _, dados = self.vision.process_and_decide(frame_defeito)
        print(f"  Resultado: {'✓ OK' if is_ok else '✗ NOK'}")

    # =========================================================================
    # Funções de Simulação
    # =========================================================================
    def _gerar_guia_continua(self, width=400, height=80, brightness=220):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        center_y = height // 2
        cv2.rectangle(frame, (20, center_y-10), (width-20, center_y+10), 
                     (brightness, brightness, brightness), -1)
        return frame
    
    def _gerar_guia_segmentada(self, num_segments=8, segment_spacing=40, 
                              width=400, height=80, ruido=False, com_defeito=False):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        center_y = height // 2
        
        # 1. Desenha o "Corpo" em acrílico da guia (brilho 160)
        cv2.rectangle(frame, (20, center_y-5), (width-20, center_y+5), (160, 160, 160), -1)

        # 2. Desenha os segmentos brilhantes
        start_x = (width - (num_segments-1) * segment_spacing) // 2
        for i in range(num_segments):
            x = start_x + i * segment_spacing
            brightness = 100 if (com_defeito and i % 2 == 0) else 255
            size = 6 
            cv2.rectangle(frame, (x-size, center_y-15), (x+size, center_y+15),
                         (brightness, brightness, brightness), -1)
        
        if ruido:
            noise = np.random.normal(0, 10, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)
        
        return frame
    
    def executar_todos_testes(self):
        try:
            self.test_1_criar_padroes_sinteticos()
            self.test_2_listar_padroes()
            self.test_3_analisar_caracteristicas()
            self.test_4_matching_e_comparacao()
            self.test_5_remocao_padrao()
            self.test_6_edge_cases()
            
            print("\n" + "="*70)
            print("✓ TODOS OS TESTES COMPLETADOS COM SUCESSO")
            print("="*70)
            
        except Exception as e:
            print(f"\n✗ ERRO DURANTE TESTES: {e}")


def main():
    print("""
     TESTE DO SISTEMA DE PADRÕES MÚLTIPLOS V2.0              
      Testa:                                                            
        Criação de padrões múltiplos                                 
        Detecção automática de características                       
        Matching inteligente de padrões                              
        Comparação e decisão OK/NOK                                  
        Casos extremos e edge cases                                  
    """)
    tester = TestVisionV2()
    tester.executar_todos_testes()

if __name__ == "__main__":
    main()