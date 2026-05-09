import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from guide_detector import GuideCharacteristics


@dataclass
class MatchScore:
    """Score de compatibilidade entre um padrão e a guia analisada"""
    pattern_id: int
    pattern_name: str
    total_score: float              # Score total (0-1)
    type_match: float               # Compatibilidade de tipo (contínua vs segmentada)
    segment_match: float            # Compatibilidade de número de segmentos
    spacing_match: float            # Compatibilidade de espaçamento
    size_match: float               # Compatibilidade de dimensões
    brightness_match: float         # Compatibilidade de brilho
    color_match: float              # Compatibilidade de cor
    is_eligible: bool               # Se é elegível para comparação
    rejection_reason: str           # Motivo se não é elegível


class SmartPatternMatcher:
    """
    Motor de matching inteligente que:
    1. Filtra padrões compatíveis baseado em características
    2. Calcula scores de similaridade
    3. Reduz número de padrões a comparar
    """
    
    def __init__(self):
        # Tolerâncias e thresholds
        self.type_mismatch_penalty = 0.3        # Penalidade por tipo diferente
        self.segment_tolerance = 1              # Tolerância em número de segmentos
        self.spacing_tolerance_mm = 0.5         # Tolerância em espaçamento (mm)
        self.size_tolerance_percent = 15        # Tolerância em tamanho (%)
        self.brightness_tolerance = 30          # Tolerância em brilho (0-255)
        self.color_tolerance_lab = 10           # Tolerância em cor LAB
        
        # Pesos para cada factor (somam 1.0)
        self.weights = {
            "type": 0.20,
            "segments": 0.25,
            "spacing": 0.15,
            "size": 0.15,
            "brightness": 0.15,
            "color": 0.10
        }
    
    def find_matching_patterns(self,
                              guide_characteristics: GuideCharacteristics,
                              available_patterns: Dict[int, 'PatternMetadata']) -> List[MatchScore]:
        """
        Encontra padrões compatíveis e calcula scores.
        
        Args:
            guide_characteristics: Características da guia a analisar
            available_patterns: Dicionário de padrões disponíveis (id -> metadata)
        
        Returns:
            Lista de MatchScore ordenada por score descendente
        """
        match_scores = []
        
        for pattern_id, pattern_meta in available_patterns.items():
            score = self._calculate_match_score(guide_characteristics, pattern_meta)
            match_scores.append(score)
        
        # Ordena por score descendente
        match_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return match_scores
    
    def get_best_matches(self,
                        match_scores: List[MatchScore],
                        num_candidates: int = 3,
                        min_score: float = 0.5) -> List[MatchScore]:
        """
        Retorna os melhores matches que são elegíveis.
        
        Args:
            match_scores: Lista de scores já ordenada
            num_candidates: Número máximo de candidatos a retornar
            min_score: Score mínimo para ser considerado elegível
        
        Returns:
            Lista de best matches (até num_candidates)
        """
        eligible = [m for m in match_scores if m.is_eligible and m.total_score >= min_score]
        return eligible[:num_candidates]
    
    def _calculate_match_score(self,
                              guide_chars: GuideCharacteristics,
                              pattern_meta: 'PatternMetadata') -> MatchScore:
        """
        Calcula score detalhado de compatibilidade.
        """
        pattern_id = pattern_meta.pattern_id
        pattern_name = pattern_meta.name
        
        # 1. Type match
        type_match = self._calculate_type_match(guide_chars.is_continuous, pattern_meta.is_continuous)
        
        # 2. Segment match
        segment_match = self._calculate_segment_match(
            guide_chars.num_segments,
            pattern_meta.num_segments
        )
        
        # 3. Spacing match
        spacing_match = self._calculate_spacing_match(
            guide_chars.segment_spacing_mm,
            pattern_meta.segment_spacing_mm,
            guide_chars.num_segments,
            pattern_meta.num_segments
        )
        
        # 4. Size match
        size_match = self._calculate_size_match(
            guide_chars.guide_length_px,
            guide_chars.guide_width_px,
            pattern_meta.light_guide_length_px,
            pattern_meta.light_guide_width_px
        )
        
        # 5. Brightness match (usando perfil)
        brightness_match = self._calculate_brightness_profile_match(
            guide_chars.debug_info.get("intensity_mean", 127),
            np.mean(pattern_meta.brightness_profile) if pattern_meta.brightness_profile else 127
        )
        
        # 6. Color match
        color_match = self._calculate_color_match(
            guide_chars,
            pattern_meta.color_profile
        )
        
        # Calcula score total com pesos
        total_score = (
            type_match * self.weights["type"] +
            segment_match * self.weights["segments"] +
            spacing_match * self.weights["spacing"] +
            size_match * self.weights["size"] +
            brightness_match * self.weights["brightness"] +
            color_match * self.weights["color"]
        )
        
        # Determina elegibilidade
        is_eligible, rejection_reason = self._determine_eligibility(
            type_match,
            segment_match,
            spacing_match,
            size_match,
            guide_chars,
            pattern_meta
        )
        
        return MatchScore(
            pattern_id=pattern_id,
            pattern_name=pattern_name,
            total_score=float(total_score),
            type_match=float(type_match),
            segment_match=float(segment_match),
            spacing_match=float(spacing_match),
            size_match=float(size_match),
            brightness_match=float(brightness_match),
            color_match=float(color_match),
            is_eligible=is_eligible,
            rejection_reason=rejection_reason
        )
    
    def _calculate_type_match(self, is_continuous_guide: bool, is_continuous_pattern: bool) -> float:
        """Compatibilidade de tipo: 1.0 se iguais, penalizado se diferentes"""
        if is_continuous_guide == is_continuous_pattern:
            return 1.0
        else:
            return max(0.0, 1.0 - self.type_mismatch_penalty)
    
    def _calculate_segment_match(self, guide_segments: int, pattern_segments: int) -> float:
        """
        Compatibilidade de número de segmentos.
        
        Para guias contínuas: tolerance automática
        Para segmentadas: deve corresponder dentro de tolerance
        """
        if guide_segments == 0 and pattern_segments == 0:
            # Ambas contínuas
            return 1.0
        
        if guide_segments == 0 or pattern_segments == 0:
            # Uma é contínua, outra não
            return 0.2
        
        # Ambas segmentadas: calcula diferença
        diff = abs(guide_segments - pattern_segments)
        
        if diff == 0:
            return 1.0
        elif diff <= self.segment_tolerance:
            return 1.0 - (diff / self.segment_tolerance) * 0.5
        else:
            return 0.0
    
    def _calculate_spacing_match(self,
                                guide_spacing: float,
                                pattern_spacing: float,
                                guide_segments: int,
                                pattern_segments: int) -> float:
        """
        Compatibilidade de espaçamento entre segmentos.
        
        Só é relevante para guias segmentadas.
        """
        # Se alguma for contínua, spacing não é relevante
        if guide_segments <= 1 or pattern_segments <= 1:
            return 1.0
        
        if guide_spacing == 0 or pattern_spacing == 0:
            return 0.5
        
        # Calcula erro percentual
        error = abs(guide_spacing - pattern_spacing) / max(guide_spacing, pattern_spacing, 1e-6)
        
        if error <= (self.spacing_tolerance_mm / max(guide_spacing, pattern_spacing, 1)):
            return 1.0
        else:
            return max(0.0, 1.0 - error)
    
    def _calculate_size_match(self,
                             guide_length: int,
                             guide_width: int,
                             pattern_length: int,
                             pattern_width: int) -> float:
        """
        Compatibilidade de dimensões.
        
        Calcula erro percentual e aplica tolerância.
        """
        if guide_length == 0 or pattern_length == 0:
            return 0.5
        
        # Calcula erro percentual
        length_error = abs(guide_length - pattern_length) / pattern_length * 100
        width_error = abs(guide_width - pattern_width) / pattern_width * 100
        avg_error = (length_error + width_error) / 2
        
        if avg_error <= self.size_tolerance_percent:
            return 1.0 - (avg_error / self.size_tolerance_percent) * 0.3
        else:
            # Penaliza fortemente tamanhos muito diferentes
            return max(0.0, 1.0 - (avg_error / 50))
    
    def _calculate_brightness_profile_match(self, guide_brightness: float, pattern_brightness: float) -> float:
        """Compatibilidade de brilho médio"""
        if guide_brightness == 0 or pattern_brightness == 0:
            return 0.5
        
        difference = abs(guide_brightness - pattern_brightness)
        
        if difference <= self.brightness_tolerance:
            return 1.0 - (difference / self.brightness_tolerance) * 0.2
        else:
            return max(0.0, 1.0 - (difference / 255))
    
    def _calculate_color_match(self, guide_chars: GuideCharacteristics, pattern_color: Dict) -> float:
        """
        Compatibilidade de cor (LAB).
        
        Nota: Idealmente extrairia cor da guia também, por enquanto usa aproximação.
        """
        # Simplificação: assume que a cor é similar se o brilho é similar
        # Numa implementação real, extrairia os valores LAB da guia
        return 0.8
    
    def _determine_eligibility(self,
                              type_match: float,
                              segment_match: float,
                              spacing_match: float,
                              size_match: float,
                              guide_chars: GuideCharacteristics,
                              pattern_meta: 'PatternMetadata') -> Tuple[bool, str]:
        """
        Determina se um padrão é elegível para comparação.
        
        Critérios hard:
        - Type match mínimo
        - Segment match mínimo
        - Size match razoável
        """
        
        # Verifica se padrão é válido
        if not pattern_meta.is_valid:
            return False, "Padrão inválido"
        
        # Tipo deve ser compatível (pelo menos 50% match)
        if type_match < 0.5:
            return False, "Tipo de guia incompatível"
        
        # Número de segmentos deve ser compatível
        if segment_match < 0.4:
            return False, f"Segmentos incompatíveis: guia={guide_chars.num_segments}, padrão={pattern_meta.num_segments}"
        
        # Tamanho deve ser razoável (pelo menos 40% match)
        if size_match < 0.4:
            return False, "Dimensões muito diferentes"
        
        # Se confiança da detecção for muito baixa, relaxa critérios
        if guide_chars.confidence < 0.5:
            return True, ""
        
        # Criterios relaxados atendidos
        return True, ""


class PatternComparisonEngine:
    """
    Motor de comparação que:
    1. Seleciona melhores padrões
    2. Compara a guia com cada padrão
    3. Gera resultados OK/NOK
    """
    
    def __init__(self):
        self.matcher = SmartPatternMatcher()
        self.segment_mismatch_threshold = 0.7  # Se < 70% segmentos OK, então NOK
        self.brightness_drop_threshold = 3.5   # Se queda > 3.5, então NOK
    
    def compare_with_best_patterns(self,
                                   guide_data: Dict,
                                   guide_characteristics: GuideCharacteristics,
                                   available_patterns: Dict) -> Dict:
        """
        Executa comparação com os melhores padrões.
        
        Retorna resultado consolidado.
        """
        # Encontra padrões compatíveis
        match_scores = self.matcher.find_matching_patterns(guide_characteristics, available_patterns)
        best_matches = self.matcher.get_best_matches(match_scores, num_candidates=3, min_score=0.5)
        
        if not best_matches:
            return {
                "is_ok": False,
                "error": "Nenhum padrão compatível encontrado",
                "match_scores": match_scores,
                "best_matches": []
            }
        
        # Compara com o melhor padrão
        best_pattern = best_matches[0]
        
        # Análise de segmentos (se aplicável)
        segment_analysis = None
        if not guide_characteristics.is_continuous:
            segment_analysis = self._analyze_segment_quality(guide_data)
        
        # Decisão final
        is_ok = self._make_final_decision(
            guide_characteristics,
            best_pattern,
            guide_data,
            segment_analysis
        )
        
        return {
            "is_ok": is_ok,
            "selected_pattern_id": best_pattern.pattern_id,
            "selected_pattern_name": best_pattern.pattern_name,
            "pattern_match_score": best_pattern.total_score,
            "best_matches": [
                {
                    "pattern_id": m.pattern_id,
                    "name": m.pattern_name,
                    "score": m.total_score,
                    "type_match": m.type_match,
                    "segment_match": m.segment_match,
                    "spacing_match": m.spacing_match,
                    "size_match": m.size_match
                }
                for m in best_matches
            ],
            "all_match_scores": match_scores,
            "segment_analysis": segment_analysis,
            "guide_characteristics": {
                "is_continuous": guide_characteristics.is_continuous,
                "num_segments": guide_characteristics.num_segments,
                "spacing_mm": guide_characteristics.segment_spacing_mm,
                "length_px": guide_characteristics.guide_length_px,
                "confidence": guide_characteristics.confidence
            }
        }
    
    def _analyze_segment_quality(self, guide_data: Dict) -> Dict:
        """
        Analisa qualidade dos segmentos.
        
        Verifica:
        - Número de segmentos com brilho inadequado
        - Variação de brilho entre segmentos
        - Segmentos não detectados
        """
        zonas = guide_data.get("zonas", [])
        
        if not zonas:
            return None
        
        brilhos = [z.get("brilho_medio", 0) for z in zonas]
        brilhos = [b for b in brilhos if b > 0]
        
        if not brilhos:
            return None
        
        brilho_medio = np.mean(brilhos)
        brilho_min = np.min(brilhos)
        brilho_max = np.max(brilhos)
        
        # Conta segmentos OK (> 70% da média)
        segmentos_ok = sum(1 for b in brilhos if b >= 0.7 * brilho_medio)
        percentagem_ok = segmentos_ok / len(brilhos) * 100 if brilhos else 0
        
        return {
            "total_segments": len(zonas),
            "segments_ok": segmentos_ok,
            "percentage_ok": percentagem_ok,
            "brightness_mean": float(brilho_medio),
            "brightness_min": float(brilho_min),
            "brightness_max": float(brilho_max),
            "brightness_variation": float(brilho_max - brilho_min)
        }
    
    def _make_final_decision(self,
                            guide_chars: GuideCharacteristics,
                            best_match: MatchScore,
                            guide_data: Dict,
                            segment_analysis: Optional[Dict]) -> bool:
        """
        Toma decisão final OK/NOK baseada em:
        1. Score do padrão
        2. Análise de segmentos
        3. Critérios de confiança
        """
        
        # Se match score for muito baixo, NOK
        if best_match.total_score < 0.4:
            return False
        
        # Se é guia contínua, critérios diferentes
        if guide_chars.is_continuous:
            # Para contínua: principalmente verifica brilho uniforme
            brightness_mean = guide_data.get("debug_info", {}).get("intensity_mean", 127)
            # Se brilho médio for muito baixo, NOK
            return brightness_mean >= 50
        
        # Para segmentada: analisa qualidade dos segmentos
        if segment_analysis:
            # Se menos de 80% dos segmentos tiverem brilho adequado
            if segment_analysis["percentage_ok"] < 80:
                return False
            
            # Se houver queda excessiva de luz
            if segment_analysis["brightness_variation"] > self.brightness_drop_threshold * segment_analysis["brightness_mean"]:
                return False
        
        return True
