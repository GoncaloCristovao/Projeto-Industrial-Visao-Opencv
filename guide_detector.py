import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass


@dataclass
class GuideCharacteristics:
    """Características detectadas de uma guia de luz"""
    is_continuous: bool              # True = contínua, False = segmentada
    num_segments: int                # Número de segmentos (0 se contínua)
    segment_positions: List[int]     # Posições em pixels dos segmentos
    segment_spacing_mm: float        # Espaçamento médio (assumindo calibração)
    guide_length_px: int             # Comprimento em pixels
    guide_width_px: int              # Altura/largura da guia
    guide_direction: str             # "horizontal" ou "vertical"
    confidence: float                # Confiança da detecção (0-1)
    debug_info: Dict                 # Informações para debug


class GuideCharacteristicDetector:
    """
    Detecta automaticamente as características de uma guia de luz:
    - Se é contínua ou segmentada
    - Número e posição de segmentos
    - Dimensões
    - Espaçamento
    """
    
    def __init__(self, px_to_mm_ratio: float = 0.1):
        """
        Args:
            px_to_mm_ratio: Razão de conversão pixels para milímetros
                          (ajustar conforme calibração da câmara)
        """
        self.px_to_mm_ratio = px_to_mm_ratio
        self.segment_min_brightness = 200    # Threshold para detecção de segmento
        self.peak_prominence_threshold = 30  # Proeminência mínima de pico
        self.min_peak_distance = 10          # Distância mínima entre picos em px
    
    def analyze_guide(self, frame: np.ndarray) -> GuideCharacteristics:
        """
        Análise completa de uma guia de luz.
        
        Retorna GuideCharacteristics com todas as informações.
        """
        if frame is None:
            return self._create_empty_characteristics()
        
        try:
            h, w = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 1. Detecta a região da guia (ROI)
            guide_roi, guide_mask, direction = self._detect_guide_roi(gray)
            
            if guide_roi is None:
                return self._create_empty_characteristics()
            
            # 2. Extrai perfil de intensidade ao longo da guia
            intensity_profile = self._extract_intensity_profile(guide_roi, direction)
            
            # 3. Detecta segmentos (picos no perfil de intensidade)
            segments, is_continuous = self._detect_segments(intensity_profile)
            
            # 4. Calcula espaçamento
            spacing_px = self._calculate_spacing(segments) if len(segments) > 1 else 0
            spacing_mm = spacing_px * self.px_to_mm_ratio
            
            # 5. Calcula dimensões
            guide_length = guide_roi.shape[1] if direction == "horizontal" else guide_roi.shape[0]
            guide_width = guide_roi.shape[0] if direction == "horizontal" else guide_roi.shape[1]
            
            # 6. Calcula confiança
            confidence = self._calculate_confidence(intensity_profile, segments, is_continuous)
            
            debug_info = {
                "roi_size": guide_roi.shape,
                "direction": direction,
                "intensity_min": float(np.min(intensity_profile)),
                "intensity_max": float(np.max(intensity_profile)),
                "intensity_mean": float(np.mean(intensity_profile)),
                "profile_std": float(np.std(intensity_profile)),
                "segments_detected": len(segments)
            }
            
            return GuideCharacteristics(
                is_continuous=is_continuous,
                num_segments=len(segments),
                segment_positions=segments,
                segment_spacing_mm=spacing_mm,
                guide_length_px=guide_length,
                guide_width_px=guide_width,
                guide_direction=direction,
                confidence=confidence,
                debug_info=debug_info
            )
            
        except Exception as e:
            print(f"[GuideDetector] Erro na análise: {e}")
            return self._create_empty_characteristics()
    
    def _detect_guide_roi(self, gray: np.ndarray) -> Tuple[Optional[np.ndarray], np.ndarray, str]:
        """
        Detecta a região de interesse (ROI) onde está a guia de luz.
        
        Retorna:
            (roi_cropped, full_mask, direction)
        """
        h, w = gray.shape[:2]
        
        # Aplica threshold para encontrar as regiões brilhantes
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Morphology para limpar a imagem
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Encontra contornos
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None, thresh, "unknown"
        
        # Encontra o contorno mais grande (assumindo que é a guia)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w_roi, h_roi = cv2.boundingRect(largest_contour)
        
        # Determina direção (horizontal se mais larga do que alta)
        direction = "horizontal" if w_roi > h_roi else "vertical"
        
        # Extrai ROI com margem
        margin = 10
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(w, x + w_roi + margin)
        y2 = min(h, y + h_roi + margin)
        
        roi = gray[y1:y2, x1:x2]
        
        # Cria máscara
        mask = np.zeros_like(gray)
        mask[y1:y2, x1:x2] = 255
        
        return roi, mask, direction
    
    def _extract_intensity_profile(self, roi: np.ndarray, direction: str) -> np.ndarray:
        """
        Extrai perfil de intensidade (brilho médio) ao longo da guia.
        
        Para guia horizontal: média de cada coluna
        Para guia vertical: média de cada linha
        """
        if direction == "horizontal":
            # Calcula média de brilho em cada coluna
            profile = np.mean(roi, axis=0)
        else:
            # Calcula média de brilho em cada linha
            profile = np.mean(roi, axis=1)
        
        # Suaviza o perfil para melhor detecção
        profile = cv2.GaussianBlur(profile.astype(np.float32), ksize=5, sigmaX=1.0)
        
        return profile
    
    def _detect_segments(self, intensity_profile: np.ndarray) -> Tuple[List[int], bool]:
        """
        Detecta segmentos no perfil de intensidade.
        
        Se houver picos bem definidos e espaçados = segmentada
        Se o perfil for relativamente plano = contínua
        
        Retorna:
            (segment_positions, is_continuous)
        """
        try:
            from scipy import signal
            
            # Encontra picos no perfil
            peaks, properties = signal.find_peaks(
                intensity_profile,
                height=self.segment_min_brightness,
                prominence=self.peak_prominence_threshold,
                distance=self.min_peak_distance
            )
            
            peaks = peaks.tolist()
            
            # Decisão: se temos picos bem espaçados = segmentada
            if len(peaks) >= 2:
                # Verifica se os picos têm espaçamento regular
                spacings = np.diff(peaks)
                spacing_consistency = float(np.std(spacings) / np.mean(spacings)) if len(spacings) > 0 else 0
                
                # Se houver menos de 20% de variação no espaçamento = segmentada
                is_continuous = spacing_consistency > 0.3
            elif len(peaks) == 1:
                # Apenas um pico = contínua
                is_continuous = True
            else:
                # Nenhum pico = contínua
                is_continuous = True
            
            return peaks, is_continuous
            
        except ImportError:
            print("[GuideDetector] scipy não disponível, usando detecção simplificada")
            return self._detect_segments_simple(intensity_profile)
    
    def _detect_segments_simple(self, intensity_profile: np.ndarray) -> Tuple[List[int], bool]:
        """
        Detecção simplificada de segmentos sem scipy.
        """
        # Calcula derivada para encontrar mudanças abruptas
        profile_norm = (intensity_profile - np.min(intensity_profile)) / (np.max(intensity_profile) - np.min(intensity_profile) + 1e-6)
        
        # Encontra locais onde a intensidade é alta
        high_intensity = np.where(profile_norm > 0.7)[0]
        
        if len(high_intensity) == 0:
            return [], True
        
        # Agrupa pixels contíguos
        peaks = []
        current_group = [high_intensity[0]]
        
        for i in range(1, len(high_intensity)):
            if high_intensity[i] - high_intensity[i-1] <= self.min_peak_distance:
                current_group.append(high_intensity[i])
            else:
                # Encontra o pico do grupo
                peak_idx = current_group[len(current_group)//2]
                peaks.append(peak_idx)
                current_group = [high_intensity[i]]
        
        if current_group:
            peak_idx = current_group[len(current_group)//2]
            peaks.append(peak_idx)
        
        # Decisão
        is_continuous = len(peaks) <= 1
        
        return peaks, is_continuous
    
    def _calculate_spacing(self, segment_positions: List[int]) -> float:
        """Calcula espaçamento médio entre segmentos"""
        if len(segment_positions) < 2:
            return 0.0
        
        spacings = np.diff(segment_positions)
        return float(np.mean(spacings))
    
    def _calculate_confidence(self, profile: np.ndarray, segments: List[int], is_continuous: bool) -> float:
        """
        Calcula confiança da detecção (0-1).
        
        Baseada em:
        - Qualidade do perfil (baixo ruído)
        - Clareza dos segmentos (se aplicável)
        - Consistência dos dados
        """
        confidence = 0.5
        
        # Fator 1: Razão sinal/ruído
        signal_power = np.max(profile) - np.mean(profile)
        noise_power = np.std(profile)
        snr = signal_power / (noise_power + 1e-6)
        snr_factor = min(1.0, snr / 50)  # Normaliza até 50
        confidence += 0.2 * snr_factor
        
        # Fator 2: Clareza de segmentos
        if not is_continuous and len(segments) > 0:
            # Verifica se os segmentos estão bem definidos
            segment_clarity = 0.0
            for peak_pos in segments:
                if 0 <= peak_pos < len(profile):
                    # Verifica se há um vale antes e depois
                    left_valley = np.min(profile[max(0, peak_pos-10):peak_pos])
                    right_valley = np.min(profile[peak_pos:min(len(profile), peak_pos+10)])
                    peak_value = profile[peak_pos]
                    
                    clarity = (peak_value - (left_valley + right_valley) / 2) / (peak_value + 1e-6)
                    segment_clarity += clarity
            
            segment_clarity /= len(segments)
            confidence += 0.3 * min(1.0, segment_clarity)
        elif is_continuous:
            confidence += 0.2  # Bonus para detecção contínua
        
        # Fator 3: Dados suficientes
        if len(profile) > 50:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _create_empty_characteristics(self) -> GuideCharacteristics:
        """Cria características vazias para erro"""
        return GuideCharacteristics(
            is_continuous=False,
            num_segments=0,
            segment_positions=[],
            segment_spacing_mm=0.0,
            guide_length_px=0,
            guide_width_px=0,
            guide_direction="unknown",
            confidence=0.0,
            debug_info={"error": "Análise falhou"}
        )
    
    def visualize_analysis(self, frame: np.ndarray, characteristics: GuideCharacteristics) -> np.ndarray:
        """
        Cria visualização da análise para debug.
        """
        if frame is None:
            return None
        
        debug_frame = frame.copy()
        h, w = debug_frame.shape[:2]
        
        # Desenha informações
        y_offset = 30
        cv2.putText(debug_frame, f"Type: {'Continua' if characteristics.is_continuous else 'Segmentada'}", 
                    (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(debug_frame, f"Segments: {characteristics.num_segments}", 
                    (10, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(debug_frame, f"Spacing: {characteristics.segment_spacing_mm:.2f}mm", 
                    (10, y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(debug_frame, f"Confidence: {characteristics.confidence:.2f}", 
                    (10, y_offset + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return debug_frame
