import cv2
import os
import numpy as np
from typing import Dict, List, Optional, Tuple

# Importa os teus novos módulos de inteligência V2
from pattern_manager import PatternDatabase, PatternMetadata
from guide_detector import GuideCharacteristicDetector, GuideCharacteristics
from pattern_matcher import SmartPatternMatcher, PatternComparisonEngine


class VisionProcessor:
    """
    Processor de visão central:
    Orquestra o sistema de múltiplos padrões e a análise matemática CIE.
    """
    
    def __init__(self, db_path: str = "pattern_database"):
        # Inicializa as componentes inteligentes
        self.pattern_db = PatternDatabase(db_path)
        self.guide_detector = GuideCharacteristicDetector(px_to_mm_ratio=0.1)
        self.comparison_engine = PatternComparisonEngine()
        
        # Parâmetros mecânicos e de limiar (Herdados da versão original)
        self.scale = 0.7
        self.threshold_value = 230
        self.half_thickness = 18
        self.num_parts = 10
        
        print("[Vision] Módulo de Visão (Multi-Padrões & CIExyY) inicializado.")
    
    # =========================================================================
    # GESTÃO DE PADRÕES (Chamado pelo main.py no comando "PADRAO")
    # =========================================================================
    def add_new_standard(self, frame: np.ndarray, name: str = None, notes: str = "") -> Tuple[bool, str]:
        if frame is None or frame.size == 0:
            return False, "Frame inválido"
        
        characteristics = self.guide_detector.analyze_guide(frame)
        
        if name is None:
            guide_type = "Continua" if characteristics.is_continuous else f"Segmentada_{characteristics.num_segments}seg"
            name = f"Padrao_{guide_type}"
        
        success, message, pattern_id = self.pattern_db.add_pattern(
            name=name,
            image_frame=frame,
            is_continuous=characteristics.is_continuous,
            num_segments=characteristics.num_segments,
            segment_spacing_mm=characteristics.segment_spacing_mm,
            notes=notes
        )
        
        return success, message

    # =========================================================================
    # PROCESSAMENTO E DECISÃO (Chamado pelo main.py no AUTO e PROCESSAR)
    # =========================================================================
    def process_and_decide(self, frame: np.ndarray) -> Tuple[bool, np.ndarray, Dict]:
        if frame is None:
            return False, None, {"erro": "Frame inválido"}
        
        try:
            # 1. Deteta as características base (Contínua/Segmentada)
            guide_characteristics = self.guide_detector.analyze_guide(frame)
            
            # 2. Faz a segmentação de zonas e os cálculos rigorosos CIE e de Brilho
            is_ok_linhas, frame_proc, dados_zonas = self._process_zone_segmentation(frame)
            
            # 3. Se a BD estiver vazia, falha graciosamente
            if len(self.pattern_db.patterns) == 0:
                print("[Aviso] Nenhum padrão na base de dados!")
                return False, frame_proc, dados_zonas
            
            # 4. Motor Inteligente descobre qual dos 12 padrões usar
            comparison_result = self.comparison_engine.compare_with_best_patterns(
                dados_zonas,
                guide_characteristics,
                self.pattern_db.patterns
            )
            
            # Decisão Final Inteligente (Substitui o critério rígido antigo)
            is_ok = comparison_result["is_ok"]
            
            # Empacota TUDO no dicionário de dados
            dados_saida = {
                "is_ok": is_ok,
                "zonas": dados_zonas.get("zonas", []),
                "padrão_selecionado": comparison_result.get("selected_pattern_name", "Desconhecido")
            }
            
            return is_ok, frame_proc, dados_saida
            
        except Exception as e:
            print(f"[Erro Processamento] {e}")
            erro_img = frame.copy() if frame is not None else None
            return False, erro_img, {"erro": str(e)}

    # =========================================================================
    # MATEMÁTICA INTERNA (Cortes, BGR -> XYZ -> xyY)
    # =========================================================================
    def _process_zone_segmentation(self, frame: np.ndarray) -> Tuple[bool, np.ndarray, Dict]:
        if frame is None:
            return False, None, {"zonas": []}
        
        try:
            img = frame.copy()
            if self.scale != 1.0:
                img = cv2.resize(img, None, fx=self.scale, fy=self.scale)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            _, thresh = cv2.threshold(blur, self.threshold_value, 255, cv2.THRESH_BINARY)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold=80, minLineLength=200, maxLineGap=30)
            
            if lines is None:
                return False, img, {"zonas": []}
            
            best_line = None
            best_length = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.hypot(x2 - x1, y2 - y1)
                if length > best_length:
                    best_length = length
                    best_line = (x1, y1, x2, y2)
            
            x1, y1, x2, y2 = best_line
            dx, dy = x2 - x1, y2 - y1
            length = np.hypot(dx, dy)
            if length == 0: return False, img, {"zonas": []}
            
            ux, uy = dx / length, dy / length
            px, py = -uy, ux
            
            p1 = (int(x1 + px * self.half_thickness), int(y1 + py * self.half_thickness))
            p2 = (int(x2 + px * self.half_thickness), int(y2 + py * self.half_thickness))
            p3 = (int(x2 - px * self.half_thickness), int(y2 - py * self.half_thickness))
            p4 = (int(x1 - px * self.half_thickness), int(y1 - py * self.half_thickness))
            box = np.array([p1, p2, p3, p4], dtype=np.int32)
            
            mask = np.zeros_like(gray)
            cv2.fillConvexPoly(mask, box, 255)
            segmented = cv2.bitwise_and(img, img, mask=mask)
            
            divided_img = segmented.copy()
            zonas_info = []
            
            # Análise Zona a Zona
            for i in range(self.num_parts):
                t1 = i / self.num_parts
                t2 = (i + 1) / self.num_parts
                
                top1 = (int((1 - t1) * p1[0] + t1 * p2[0]), int((1 - t1) * p1[1] + t1 * p2[1]))
                top2 = (int((1 - t2) * p1[0] + t2 * p2[0]), int((1 - t2) * p1[1] + t2 * p2[1]))
                bot2 = (int((1 - t2) * p4[0] + t2 * p3[0]), int((1 - t2) * p4[1] + t2 * p3[1]))
                bot1 = (int((1 - t1) * p4[0] + t1 * p3[0]), int((1 - t1) * p4[1] + t1 * p3[1]))
                
                zone_poly = np.array([top1, top2, bot2, bot1], dtype=np.int32)
                zone_mask = np.zeros_like(gray)
                cv2.fillConvexPoly(zone_mask, zone_poly, 255)
                
                # CÁLCULOS MATEMÁTICOS DE BRILHO
                zona_gray = gray[zone_mask == 255]
                brilho_medio = float(np.mean(zona_gray)) if zona_gray.size > 0 else 0.0
                
                # CÁLCULOS MATEMÁTICOS CIExyY (Cor)
                x_cie, y_cie = 0.333, 0.333 # Valores brancos por defeito
                
                if zona_gray.size > 0:
                    # Extrai BGR médio (apenas dentro da máscara, ignora o fundo preto)
                    mean_bgr = cv2.mean(img, mask=zone_mask)[:3]
                    
                    # Converte de BGR para XYZ via OpenCV
                    pixel_bgr = np.uint8([[[mean_bgr[0], mean_bgr[1], mean_bgr[2]]]])
                    pixel_xyz = cv2.cvtColor(pixel_bgr, cv2.COLOR_BGR2XYZ)[0][0]
                    
                    X_val = float(pixel_xyz[0])
                    Y_cie_val = float(pixel_xyz[1])
                    Z_val = float(pixel_xyz[2])
                    
                    soma = X_val + Y_cie_val + Z_val
                    if soma > 0:
                        x_cie = X_val / soma
                        y_cie = Y_cie_val / soma
                
                zonas_info.append({
                    "zona": i + 1,
                    "brilho_medio": round(brilho_medio, 2),
                    "x_cie": x_cie,
                    "y_cie": y_cie,
                    "xp_cie": 0.333,  # Tolerância provisória do padrão
                    "yp_cie": 0.333,
                    "lump_padrao": brilho_medio # Mantém igual provisoriamente até match completo 
                })
            
            # Frame Visual (Debug simplificado)
            return True, img, {"zonas": zonas_info}
            
        except Exception as e:
            print(f"[Erro Segmentação] {e}")
            return False, frame, {"zonas": []}