import cv2
import os
import numpy as np
from typing import Dict, List, Optional, Tuple

# Importa os módulos de inteligência V2
from pattern_manager import PatternDatabase, PatternMetadata
from guide_detector import GuideCharacteristicDetector, GuideCharacteristics
from pattern_matcher import SmartPatternMatcher, PatternComparisonEngine


class VisionProcessor:
    """
    Processor de visão central dinâmico:
    Orquestra múltiplos padrões e análise de zonas variável (N segmentos).
    """
    
    def __init__(self, db_path: str = "pattern_database"):
        # Inicializa as componentes inteligentes
        self.pattern_db = PatternDatabase(db_path)
        self.guide_detector = GuideCharacteristicDetector(px_to_mm_ratio=0.1)
        self.comparison_engine = PatternComparisonEngine()
        
        # Parâmetros mecânicos base
        self.scale = 0.7
        self.threshold_value = 180
        self.half_thickness = 18
        
        print("[Vision] Sistema Dinâmico (N-Segmentos) inicializado.")
    
    # =========================================================================
    # GESTÃO DE PADRÕES
    # =========================================================================
    def add_new_standard(self, frame: np.ndarray, pattern_id: int, name: str = None, notes: str = "") -> Tuple[bool, str]:
        if frame is None or frame.size == 0:
            return False, "Frame inválido"
            
        print(f"[Vision] A adicionar padrão {name} ao slot {pattern_id}...")
        
        guide_chars = self.guide_detector.detect(frame)
        if guide_chars.confidence < 0.3:
            return False, "Guia não detetada ou má qualidade"
            
        # Cria metadados com o ID correto
        metadata = PatternMetadata(
            pattern_id=pattern_id,  
            name=name if name else f"Guia_{pattern_id}",
            file_path="", 
            is_continuous=guide_chars.is_continuous,
            num_segments=guide_chars.num_segments,
            segment_spacing_mm=guide_chars.segment_spacing_mm,
            light_guide_length_px=guide_chars.guide_length_px,
            light_guide_width_px=guide_chars.guide_width_px,
            timestamp="", hash="", brightness_profile=[],
            color_profile={"L":0, "a":0, "b":0},
            is_valid=True, notes=notes, zone_profiles=[]
        )
        
        # Guarda na BD usando a inteligência do manager
        self.pattern_db.add_pattern(metadata, frame)
        return True, f"Padrão gravado com sucesso na Posição {pattern_id}."

    # =========================================================================
    # PROCESSAMENTO E ORQUESTRAÇÃO
    # =========================================================================
    def process_and_decide(self, frame: np.ndarray) -> Tuple[bool, np.ndarray, Dict]:
        if frame is None:
            return False, None, {"erro": "Frame inválido"}
        
        try:
            # 1. Deteta características físicas (Contínua/Segmentada e N de segmentos)
            guide_characteristics = self.guide_detector.analyze_guide(frame)
            
            # 2. Faz a segmentação DINÂMICA baseada nos dentes detetados ou no comprimento
            sucesso_seg, frame_proc, dados_zonas = self._process_zone_segmentation(frame, guide_characteristics)
            
            # 3. Se a BD estiver vazia, devolve os dados para a HMI mas sem padrão
            if len(self.pattern_db.patterns) == 0:
                print("[Aviso] Base de Dados vazia!")
                return False, frame_proc, dados_zonas
            
            # 4. Motor Inteligente identifica qual o Padrão da BD corresponde a esta peça
            comparison_result = self.comparison_engine.compare_with_best_patterns(
                dados_zonas,
                guide_characteristics,
                self.pattern_db.patterns
            )
            
            # Injetar os valores exatos do Padrão para o PLC!
            id_selecionado = comparison_result.get("selected_pattern_id", 0)
            if id_selecionado in self.pattern_db.patterns:
                padrao_metadata = self.pattern_db.patterns[id_selecionado]
                perfis_padrao = padrao_metadata.zone_profiles
                
                # Se o padrão tiver as zonas gravadas, substitui os valores provisórios 0.333
                if perfis_padrao and len(perfis_padrao) == len(dados_zonas["zonas"]):
                    for i, zona_atual in enumerate(dados_zonas["zonas"]):
                        zona_padrao = perfis_padrao[i]
                        zona_atual["xp_cie"] = zona_padrao.get("x_cie", 0.333)  
                        zona_atual["yp_cie"] = zona_padrao.get("y_cie", 0.333)  
                        zona_atual["lump_padrao"] = zona_padrao.get("brilho_medio", 200.0)  

            # Empacota os dados para o Main enviar ao PLC e à HMI
            dados_saida = {
                "zonas": dados_zonas.get("zonas", []),
                "padrão_selecionado": {
                    "id": comparison_result.get("selected_pattern_id", 0),
                    "nome": comparison_result.get("selected_pattern_name", "Desconhecido")
                }
            }
            
            # Nota: O is_ok interno do Python é calculado, mas o Main usará o do PLC
            is_ok_python = comparison_result.get("is_ok", False)
            
            return is_ok_python, frame_proc, dados_saida
            
        except Exception as e:
            print(f"[Erro Processamento] {e}")
            return False, frame, {"erro": str(e)}

    # =========================================================================
    # MATEMÁTICA DE CORTE DINÂMICA (Apoia mais de 30 segmentos)
    # =========================================================================
    def _process_zone_segmentation(self, frame: np.ndarray, guide_chars: GuideCharacteristics) -> Tuple[bool, np.ndarray, Dict]:
        if frame is None:
            return False, None, {"zonas": []}
        
        try:
            img = frame.copy()
            if self.scale != 1.0:
                img = cv2.resize(img, None, fx=self.scale, fy=self.scale)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, self.threshold_value, 255, cv2.THRESH_BINARY)
            
            # Deteção de linha para alinhamento
            lines = cv2.HoughLinesP(thresh, 1, np.pi/180, 80, minLineLength=200, maxLineGap=30)
            if lines is None: return False, img, {"zonas": []}
            
            best_line = max(lines, key=lambda l: np.hypot(l[0][2]-l[0][0], l[0][3]-l[0][1]))[0]
            x1, y1, x2, y2 = best_line
            dx, dy = x2 - x1, y2 - y1
            length = np.hypot(dx, dy)
            ux, uy = dx/length, dy/length
            px, py = -uy, ux
            
            # Coordenadas do retângulo de inspeção
            p1 = (int(x1 + px*self.half_thickness), int(y1 + py*self.half_thickness))
            p2 = (int(x2 + px*self.half_thickness), int(y2 + py*self.half_thickness))
            p3 = (int(x2 - px*self.half_thickness), int(y2 - py*self.half_thickness))
            p4 = (int(x1 - px*self.half_thickness), int(y1 - py*self.half_thickness))
            
            # =================================================================
            # LÓGICA DE FATIAMENTO ELÁSTICO (SOLUÇÃO PARA >30 SEGMENTOS)
            # =================================================================
            if guide_chars is not None and not guide_chars.is_continuous and guide_chars.num_segments > 0:
                # Caso Segmentada: Usa o número real de dentes (ex: 35)
                partes_dinamicas = guide_chars.num_segments
            else:
                # Caso Contínua: Divide o comprimento por fatias fixas (ex: a cada 30px)
                # Isto evita que defeitos pequenos sejam "escondidos" por fatias grandes
                comprimento_total = guide_chars.guide_length_px if guide_chars else length
                tamanho_fatia_px = 30 
                partes_dinamicas = max(4, int(comprimento_total // tamanho_fatia_px))
            
            zonas_info = []
            mask_total = np.zeros_like(gray)
            
            # Ciclo de processamento zona a zona
            for i in range(partes_dinamicas):
                t1, t2 = i / partes_dinamicas, (i + 1) / partes_dinamicas
                
                # Interpolação para encontrar os 4 cantos de cada fatia
                top1 = (int((1-t1)*p1[0] + t1*p2[0]), int((1-t1)*p1[1] + t1*p2[1]))
                top2 = (int((1-t2)*p1[0] + t2*p2[0]), int((1-t2)*p1[1] + t2*p2[1]))
                bot2 = (int((1-t2)*p4[0] + t2*p3[0]), int((1-t2)*p4[1] + t2*p3[1]))
                bot1 = (int((1-t1)*p4[0] + t1*p3[0]), int((1-t1)*p4[1] + t1*p3[1]))
                
                zone_poly = np.array([top1, top2, bot2, bot1], dtype=np.int32)
                zone_mask = np.zeros_like(gray)
                cv2.fillConvexPoly(zone_mask, zone_poly, 255)
                
                # Cálculos CIExyY
                zona_gray = gray[zone_mask == 255]
                brilho = float(np.mean(zona_gray)) if zona_gray.size > 0 else 0.0
                
                x_cie, y_cie = 0.333, 0.333
                if zona_gray.size > 0:
                    mean_bgr = cv2.mean(img, mask=zone_mask)[:3]
                    pixel_xyz = cv2.cvtColor(np.uint8([[mean_bgr]]), cv2.COLOR_BGR2XYZ)[0][0]
                    soma = sum(pixel_xyz)
                    if soma > 0:
                        x_cie, y_cie = pixel_xyz[0]/soma, pixel_xyz[1]/soma

                zonas_info.append({
                    "zona": i + 1,
                    "brilho_medio": round(brilho, 2),
                    "x_cie": x_cie, "y_cie": y_cie,
                    "xp_cie": 0.333, "yp_cie": 0.333, "lump_padrao": 200.0
                })
                
                # Visualização de debug
                cv2.polylines(img, [zone_poly], True, (255, 0, 0), 1)

            return True, img, {"zonas": zonas_info}
            
        except Exception as e:
            print(f"[Erro Segmentação] {e}")
            return False, frame, {"zonas": []}