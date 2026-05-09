import cv2
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from pattern_manager import PatternDatabase, PatternMetadata
from guide_detector import GuideCharacteristicDetector, GuideCharacteristics
from pattern_matcher import SmartPatternMatcher, PatternComparisonEngine


class VisionProcessor:
    """
    Processor de visão melhorado com:
    - Sistema de múltiplos padrões
    - Detecção automática de características
    - Matching inteligente de padrões
    """
    
    def __init__(self, db_path: str = "pattern_database"):
        """
        Inicializa o processor de visão com novo sistema.
        
        Args:
            db_path: Caminho para a base de dados de padrões
        """
        # Base de dados de padrões
        self.pattern_db = PatternDatabase(db_path)
        
        # Detector de características
        self.guide_detector = GuideCharacteristicDetector(px_to_mm_ratio=0.1)
        
        # Motor de comparação
        self.comparison_engine = PatternComparisonEngine()
        
        # Parâmetros de processamento (compatível com versão anterior)
        self.scale = 0.7
        self.threshold_value = 230
        self.half_thickness = 18
        self.num_parts = 10
        
        print("[VisionProcessor] Inicializado com sistema de padrões múltiplos")
        self._print_database_stats()
    
    def _print_database_stats(self):
        """Imprime estatísticas da base de dados"""
        stats = self.pattern_db.get_stats()
        print(f"[PatternDB] Total: {stats['total_patterns']}/{stats['max_capacity']} padrões")
        print(f"[PatternDB] Contínuas: {stats['continuous']}, Segmentadas: {stats['segmented']}")
    
    # =========================================================================
    # FUNÇÕES DE GESTÃO DE PADRÕES
    # =========================================================================
    
    def add_new_standard(self, frame: np.ndarray, name: str = None, notes: str = "") -> Tuple[bool, str]:
        """
        Adiciona um novo padrão à base de dados.
        
        Detecta automaticamente as características e guarda.
        """
        if frame is None or frame.size == 0:
            return False, "Frame inválido"
        
        # Detecta características
        characteristics = self.guide_detector.analyze_guide(frame)
        
        if characteristics.confidence < 0.3:
            print(f"[Aviso] Confiança baixa na detecção: {characteristics.confidence:.2f}")
        
        # Nome automático se não fornecido
        if name is None:
            guide_type = "Continua" if characteristics.is_continuous else f"Segmentada_{characteristics.num_segments}seg"
            name = f"Padrao_{guide_type}"
        
        # Adiciona à base de dados
        success, message, pattern_id = self.pattern_db.add_pattern(
            name=name,
            image_frame=frame,
            is_continuous=characteristics.is_continuous,
            num_segments=characteristics.num_segments,
            segment_spacing_mm=characteristics.segment_spacing_mm,
            notes=notes + f" [Auto] Confiança: {characteristics.confidence:.2f}"
        )
        
        if success:
            print(f"[Visão] Novo padrão adicionado: {name} (ID: {pattern_id})")
            self._print_database_stats()
        
        return success, message
    
    def list_available_patterns(self) -> List[Dict]:
        """Lista todos os padrões disponíveis"""
        return self.pattern_db.list_patterns()
    
    def remove_pattern(self, pattern_id: int) -> Tuple[bool, str]:
        """Remove um padrão"""
        success, message = self.pattern_db.delete_pattern(pattern_id)
        if success:
            self._print_database_stats()
        return success, message
    
    # =========================================================================
    # FUNÇÕES DE ANÁLISE E COMPARAÇÃO
    # =========================================================================
    
    def analyze_guide_characteristics(self, frame: np.ndarray) -> GuideCharacteristics:
        """
        Analisa as características de uma guia de luz.
        
        Detecta automaticamente:
        - Se é contínua ou segmentada
        - Número de segmentos
        - Espaçamento
        - Dimensões
        """
        return self.guide_detector.analyze_guide(frame)
    
    def process_and_decide_v2(self, frame: np.ndarray) -> Tuple[bool, np.ndarray, Dict]:
        """
        Versão melhorada de process_and_decide.
        
        Fluxo:
        1. Detecta características da guia
        2. Processa a imagem com segmentação de zona
        3. Encontra padrões compatíveis
        4. Compara com melhor padrão
        5. Retorna resultado OK/NOK
        """
        if frame is None:
            return False, None, {"erro": "Frame inválido"}
        
        try:
            # ===== PASSO 1: Detecta características =====
            guide_characteristics = self.analyze_guide_characteristics(frame)
            
            # ===== PASSO 2: Processa segmentação de zona (compatível com v1) =====
            is_ok_segments, frame_proc, dados_zonas = self._process_zone_segmentation(frame)
            
            # ===== PASSO 3: Matching de padrões =====
            if len(self.pattern_db.patterns) == 0:
                print("[Aviso] Nenhum padrão na base de dados")
                return False, frame_proc, {
                    "erro": "Nenhum padrão configurado",
                    "caracteristicas": guide_characteristics,
                    "zonas": dados_zonas.get("zonas", [])
                }
            
            # Encontra melhores padrões
            comparison_result = self.comparison_engine.compare_with_best_patterns(
                dados_zonas,
                guide_characteristics,
                self.pattern_db.patterns
            )
            
            # ===== PASSO 4: Decisão final =====
            is_ok = comparison_result["is_ok"]
            
            # ===== PASSO 5: Prepara dados de saída =====
            dados_saida = {
                "is_ok": is_ok,
                "caracteristicas": {
                    "tipo": "Continua" if guide_characteristics.is_continuous else "Segmentada",
                    "num_segmentos": guide_characteristics.num_segments,
                    "espaçamento_mm": guide_characteristics.segment_spacing_mm,
                    "confiança_detecção": guide_characteristics.confidence,
                    "tamanho_px": (guide_characteristics.guide_length_px, guide_characteristics.guide_width_px)
                },
                "padrão_selecionado": {
                    "id": comparison_result["selected_pattern_id"],
                    "nome": comparison_result["selected_pattern_name"],
                    "score": comparison_result["pattern_match_score"]
                },
                "candidatos": comparison_result["best_matches"],
                "análise_segmentos": comparison_result["segment_analysis"],
                "zonas": dados_zonas.get("zonas", [])
            }
            
            return is_ok, frame_proc, dados_saida
            
        except Exception as e:
            print(f"[Erro Processamento] {e}")
            import traceback
            traceback.print_exc()
            erro_img = frame.copy() if frame is not None else None
            return False, erro_img, {"erro": str(e)}
    
    # =========================================================================
    # COMPATIBILIDADE COM VERSÃO ANTERIOR
    # =========================================================================
    
    def process_and_decide(self, frame) -> Tuple[bool, np.ndarray, Dict]:
        """
        Versão compatível com a interface antiga.
        
        Usa versão V2 internamente.
        """
        return self.process_and_decide_v2(frame)
    
    def _process_zone_segmentation(self, frame: np.ndarray) -> Tuple[bool, np.ndarray, Dict]:
        """
        Processa segmentação em zonas (código original adaptado).
        
        Retorna:
            (is_ok, frame_proc, dados)
        """
        if frame is None:
            return False, None, {"zonas": []}
        
        try:
            img = frame.copy()
            
            if self.scale != 1.0:
                img = cv2.resize(img, None, fx=self.scale, fy=self.scale)
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Threshold
            _, thresh = cv2.threshold(
                blur,
                self.threshold_value,
                255,
                cv2.THRESH_BINARY
            )
            
            # Limpeza
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Deteção de linha
            lines = cv2.HoughLinesP(
                thresh,
                1,
                np.pi / 180,
                threshold=80,
                minLineLength=200,
                maxLineGap=30
            )
            
            if lines is None:
                debug = img.copy()
                cv2.putText(debug, "FALHA: linha nao encontrada", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return False, debug, {"zonas": []}
            
            # Escolher a linha mais comprida
            best_line = None
            best_length = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.hypot(x2 - x1, y2 - y1)
                if length > best_length:
                    best_length = length
                    best_line = (x1, y1, x2, y2)
            
            x1, y1, x2, y2 = best_line
            
            line_img = img.copy()
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 0, 255), 3)
            
            # Retângulo alinhado
            dx = x2 - x1
            dy = y2 - y1
            length = np.hypot(dx, dy)
            
            if length == 0:
                return False, img, {"zonas": []}
            
            ux = dx / length
            uy = dy / length
            px = -uy
            py = ux
            
            half_thickness = self.half_thickness
            
            p1 = (int(x1 + px * half_thickness), int(y1 + py * half_thickness))
            p2 = (int(x2 + px * half_thickness), int(y2 + py * half_thickness))
            p3 = (int(x2 - px * half_thickness), int(y2 - py * half_thickness))
            p4 = (int(x1 - px * half_thickness), int(y1 - py * half_thickness))
            
            box = np.array([p1, p2, p3, p4], dtype=np.int32)
            
            # Máscara e segmentação
            mask = np.zeros_like(gray)
            cv2.fillConvexPoly(mask, box, 255)
            
            segmented = cv2.bitwise_and(img, img, mask=mask)
            result = img.copy()
            cv2.polylines(result, [box], True, (0, 255, 0), 3)
            
            # Divisão em zonas
            divided_img = segmented.copy()
            num_parts = self.num_parts
            zonas_info = []
            
            for i in range(1, num_parts):
                t = i / num_parts
                top_x = int((1 - t) * p1[0] + t * p2[0])
                top_y = int((1 - t) * p1[1] + t * p2[1])
                bot_x = int((1 - t) * p4[0] + t * p3[0])
                bot_y = int((1 - t) * p4[1] + t * p3[1])
                cv2.line(divided_img, (top_x, top_y), (bot_x, bot_y), (255, 0, 0), 2)
            
            for i in range(num_parts):
                t = (i + 0.5) / num_parts
                top_x = (1 - t) * p1[0] + t * p2[0]
                top_y = (1 - t) * p1[1] + t * p2[1]
                bot_x = (1 - t) * p4[0] + t * p3[0]
                bot_y = (1 - t) * p4[1] + t * p3[1]
                cx = int((top_x + bot_x) / 2)
                cy = int((top_y + bot_y) / 2)
                cv2.putText(divided_img, str(i + 1), (cx - 10, cy + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Extração e análise das zonas
            for i in range(num_parts):
                t1 = i / num_parts
                t2 = (i + 1) / num_parts
                
                top1 = (
                    int((1 - t1) * p1[0] + t1 * p2[0]),
                    int((1 - t1) * p1[1] + t1 * p2[1])
                )
                top2 = (
                    int((1 - t2) * p1[0] + t2 * p2[0]),
                    int((1 - t2) * p1[1] + t2 * p2[1])
                )
                bot2 = (
                    int((1 - t2) * p4[0] + t2 * p3[0]),
                    int((1 - t2) * p4[1] + t2 * p3[1])
                )
                bot1 = (
                    int((1 - t1) * p4[0] + t1 * p3[0]),
                    int((1 - t1) * p4[1] + t1 * p3[1])
                )
                
                zone_poly = np.array([top1, top2, bot2, bot1], dtype=np.int32)
                zone_mask = np.zeros_like(gray)
                cv2.fillConvexPoly(zone_mask, zone_poly, 255)
                
                zona_gray = gray[zone_mask == 255]
                brilho_medio = float(np.mean(zona_gray)) if zona_gray.size > 0 else 0.0
                
                zonas_info.append({
                    "zona": i + 1,
                    "brilho_medio": round(brilho_medio, 2)
                })
            
            # Frame visual de debug
            frame_proc = self._create_debug_visualization(img, thresh, line_img, result, mask, segmented, divided_img, zonas_info)
            
            return True, frame_proc, {
                "zonas": zonas_info,
                "debug_info": {
                    "intensity_mean": float(np.mean(gray)),
                    "intensity_min": float(np.min(gray)),
                    "intensity_max": float(np.max(gray)),
                    "intensity_std": float(np.std(gray))
                }
            }
            
        except Exception as e:
            print(f"[Erro Segmentação] {e}")
            return False, frame, {"zonas": []}
    
    def _create_debug_visualization(self, *images) -> np.ndarray:
        """Cria visualização de debug similar à versão anterior"""
        labels = ["Original", "Threshold", "Linha", "Retangulo", "Mascara", "Segmentada", "Divisao zonas"]
        
        viz_images = []
        for img, label in zip(images[:-1], labels):
            img_viz = self._resize_to_width(img if len(img.shape) == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), 400)
            img_viz = self._add_label(img_viz, label)
            viz_images.append(img_viz)
        
        # Último é zonas_info (lista, não imagem)
        zonas_info = images[-1]
        
        # Painel de status
        dummy = np.zeros((400, 400, 3), dtype=np.uint8)
        status_panel = self._add_label(dummy, "Status OK")
        
        viz_images.append(status_panel)
        
        # Encontra altura comum
        target_h = min(img.shape[0] for img in viz_images)
        viz_images = [self._force_height(img, target_h) for img in viz_images]
        
        # Monta grid 2x4
        top = np.hstack(viz_images[:4])
        bottom = np.hstack(viz_images[4:])
        result = np.vstack([top, bottom])
        
        return result
    
    def _resize_to_width(self, img, width=400):
        h, w = img.shape[:2]
        scale = width / w
        new_h = int(h * scale)
        return cv2.resize(img, (width, new_h))
    
    def _add_label(self, img, text):
        out = img.copy()
        cv2.putText(out, text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0), 2)
        return out
    
    def _force_height(self, im, h):
        return cv2.resize(im, (im.shape[1], h))
