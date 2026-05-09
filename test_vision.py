"""
Script de Teste do Sistema de Padrões Múltiplos

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
    print("Certifique-se de que os módulos estão no mesmo diretório:")
    print("  - vision.py")
    print("  - guide_detector.py")
    print("  - pattern_matcher.py")
    print("  - pattern_manager.py")
    sys.exit(1)


class TestVisionV2:
    """Testes do novo sistema de visão"""
    
    def __init__(self):
        self.vision = VisionProcessor(db_path="test_pattern_database")
        self.detector = GuideCharacteristicDetector(px_to_mm_ratio=0.1)
    
    def test_1_criar_padroes_sinteticos(self):
        """TESTE 1: Cria padrões sintéticos para teste"""
        print("\n" + "="*70)
        print("TESTE 1: Criar Padrões Sintéticos")
        print("="*70)
        
        # Padrão 1: Guia Contínua
        print("\n[1.1] Criando padrão contínuo...")
        frame_continuo = self._gerar_guia_continua(width=400, height=80, brightness=220)
        success, msg = self.vision.add_new_standard(
            frame_continuo,
            name="Guia_Continua_Standard",
            notes="Guia com luz contínua uniforme"
        )
        print(f"  Resultado: {'✓' if success else '✗'} {msg}")
        
        # Padrão 2: Guia Segmentada 8 segmentos
        print("\n[1.2] Criando padrão segmentado 8 segmentos...")
        frame_seg8 = self._gerar_guia_segmentada(
            num_segments=8,
            segment_spacing=40,
            width=400,
            height=80
        )
        success, msg = self.vision.add_new_standard(
            frame_seg8,
            name="Guia_Segmentada_8seg",
            notes="Guia com 8 segmentos espaçados 40px"
        )
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
        
        patterns = self.vision.list_available_patterns()
        
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
        
        # Cria guias de teste
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
            print(f"  Tamanho: {characteristics.guide_length_px}x{characteristics.guide_width_px}px")
            print(f"  Confiança: {characteristics.confidence:.3f}")
            
            if characteristics.debug_info:
                info = characteristics.debug_info
                print(f"  Brilho (mean/min/max): {info.get('intensity_mean', 0):.0f}/{info.get('intensity_min', 0):.0f}/{info.get('intensity_max', 0):.0f}")
    
    def test_4_matching_e_comparacao(self):
        """TESTE 4: Matching e comparação com padrões"""
        print("\n" + "="*70)
        print("TESTE 4: Matching e Comparação com Padrões")
        print("="*70)
        
        # Cria um teste similar a um dos padrões
        print("\n[4.1] Testando guia segmentada 8 seg (deve dar match com padrão)")
        frame_test = self._gerar_guia_segmentada(8, 40, 400, 80, ruido=True)
        
        is_ok, frame_viz, dados = self.vision.process_and_decide(frame_test)
        
        print(f"\n  Resultado Final: {'✓ OK' if is_ok else '✗ NOK'}")
        print(f"  Tipo Detectado: {dados['caracteristicas']['tipo']}")
        print(f"  Segmentos: {dados['caracteristicas']['num_segmentos']}")
        print(f"  Confiança: {dados['caracteristicas']['confiança_detecção']:.3f}")
        
        print(f"\n  Padrão Selecionado: {dados['padrão_selecionado']['nome']}")
        print(f"  Score de Match: {dados['padrão_selecionado']['score']:.3f}")
        
        print("\n  Candidatos considerados:")
        for i, cand in enumerate(dados['candidatos'], 1):
            print(f"    {i}. {cand['name'][:30]:30s} - Score: {cand['score']:.3f}")
            print(f"       Type: {cand['type_match']:.3f}, Segments: {cand['segment_match']:.3f}, Size: {cand['size_match']:.3f}")
        
        # Teste com guia contínua
        print("\n[4.2] Testando guia contínua (deve dar match com padrão contínuo)")
        frame_cont = self._gerar_guia_continua(400, 80, 215)
        
        is_ok, frame_viz, dados = self.vision.process_and_decide(frame_cont)
        
        print(f"\n  Resultado Final: {'✓ OK' if is_ok else '✗ NOK'}")
        print(f"  Padrão Selecionado: {dados['padrão_selecionado']['nome']}")
        print(f"  Score: {dados['padrão_selecionado']['score']:.3f}")
    
    def test_5_remocao_padrao(self):
        """TESTE 5: Remoção de padrão"""
        print("\n" + "="*70)
        print("TESTE 5: Remoção de Padrão")
        print("="*70)
        
        patterns_antes = self.vision.list_available_patterns()
        print(f"\n  Padrões antes: {len(patterns_antes)}")
        
        if patterns_antes:
            pattern_para_remover = patterns_antes[-1]
            print(f"  Removendo: {pattern_para_remover['name']} (ID: {pattern_para_remover['id']})")
            
            success, msg = self.vision.remove_pattern(pattern_para_remover['id'])
            print(f"  Resultado: {'✓' if success else '✗'} {msg}")
            
            patterns_depois = self.vision.list_available_patterns()
            print(f"  Padrões depois: {len(patterns_depois)}")
    
    def test_6_edge_cases(self):
        """TESTE 6: Casos extremos"""
        print("\n" + "="*70)
        print("TESTE 6: Casos Extremos")
        print("="*70)
        
        # Caso 1: Imagem muito escura
        print("\n[6.1] Imagem muito escura...")
        frame_escuro = self._gerar_guia_continua(400, 80, 50)
        is_ok, _, dados = self.vision.process_and_decide(frame_escuro)
        print(f"  Resultado: {'✓ OK' if is_ok else '✗ NOK'}")
        print(f"  Brilho detectado: {dados['caracteristicas'].get('brilho', 'N/A')}")
        
        # Caso 2: Imagem com defeito (segmentos incompletos)
        print("\n[6.2] Guia segmentada com defeito severo...")
        frame_defeito = self._gerar_guia_segmentada(8, 40, 400, 80, com_defeito=True)
        is_ok, _, dados = self.vision.process_and_decide(frame_defeito)
        print(f"  Resultado: {'✓ OK' if is_ok else '✗ NOK'}")
        
        if dados['análise_segmentos']:
            análise = dados['análise_segmentos']
            print(f"  Segmentos OK: {análise['percentage_ok']:.1f}%")
        
        # Caso 3: Tentativa com nenhum padrão
        print("\n[6.3] Processamento com BD vazia (após remover tudo)...")
        # Nota: Isto seria feito removendo todos os padrões
        print("  [Pulado - requer limpeza completa da BD]")
    
    # =========================================================================
    # Funções Auxiliares para Gerar Frames de Teste
    # =========================================================================
    
    def _gerar_guia_continua(self, width=400, height=80, brightness=220):
        """Gera uma imagem de guia de luz contínua"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Guia contínua (linha horizontal brilhante)
        center_y = height // 2
        cv2.rectangle(frame, (20, center_y-10), (width-20, center_y+10), 
                     (brightness, brightness, brightness), -1)
        return frame
    
    def _gerar_guia_segmentada(self, num_segments=8, segment_spacing=40, 
                              width=400, height=80, ruido=False, com_defeito=False):
        """Gera uma imagem de guia de luz segmentada"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        center_y = height // 2
        
        # Desenha segmentos
        start_x = (width - (num_segments-1) * segment_spacing) // 2
        
        for i in range(num_segments):
            x = start_x + i * segment_spacing
            
            # Se é defeito, deixa alguns segmentos mais fracos
            brightness = 100 if (com_defeito and i % 2 == 0) else 220
            
            # Desenha quadrado brilhante (segmento)
            size = 15
            cv2.rectangle(frame, (x-size, center_y-size), (x+size, center_y+size),
                         (brightness, brightness, brightness), -1)
        
        # Adiciona ruído se pedido
        if ruido:
            noise = np.random.normal(0, 10, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)
        
        return frame
    
    def executar_todos_testes(self):
        """Executa todos os testes em sequência"""
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
            import traceback
            traceback.print_exc()


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