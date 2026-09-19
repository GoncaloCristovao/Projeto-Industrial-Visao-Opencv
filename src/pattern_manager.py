import platform
import cv2
import numpy as np
import os
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple


@dataclass
class PatternMetadata:
    """Metadados de um padrão de guia de luz"""
    pattern_id: int                    # ID único (1-12)
    name: str                          # Nome descritivo
    file_path: str                     # Caminho do ficheiro
    is_continuous: bool                # True = luz contínua, False = segmentada
    num_segments: int                  # Número de segmentos (0 se contínua)
    segment_spacing_mm: float          # Distância entre segmentos em mm
    light_guide_length_px: int         # Comprimento da guia em pixels
    light_guide_width_px: int          # Largura da guia em pixels
    timestamp: str                     # Data de criação
    hash: str                          # Hash do ficheiro para validação
    brightness_profile: List[float]    # Perfil médio de brilho ao longo da guia
    color_profile: Dict[str, float]    # Perfil de cor (X, Y CIE médios)
    is_valid: bool                     # Se o padrão é válido
    notes: str                         # Notas adicionais
    zone_profiles: List[Dict] = None

class PatternDatabase:
    """Gestor de base de dados de padrões de guias de luz"""
    
    def __init__(self, db_path: str = "pattern_database"):
        # 1. DETETAR O AMBIENTE DE TRABALHO (DESKTOP) DINAMICAMENTE
        sistema = platform.system()
        home_dir = Path.home()
        
        if sistema == "Windows":
            # No Windows, o Desktop pode estar na pasta padrão ou gerido pelo OneDrive
            desktop_padrao = home_dir / "Desktop"
            desktop_onedrive = home_dir / "OneDrive" / "Desktop"
            
            if desktop_onedrive.exists():
                desktop_dir = desktop_onedrive
            else:
                desktop_dir = desktop_padrao
        else:
            # Em Linux (Raspberry Pi / Raspbian OS), o caminho é habitualmente /home/pi/Desktop
            # Nota: Se o sistema estiver em Português, a pasta pode chamar-se "Ambiente de Trabalho"
            desktop_pt = home_dir / "Ambiente de Trabalho"
            desktop_en = home_dir / "Desktop"
            
            if desktop_pt.exists():
                desktop_dir = desktop_pt
            else:
                desktop_dir = desktop_en

        # 2. CONFIGURAR A PASTA DA BASE DE DADOS NO DESKTOP
        # Isto criará uma pasta chamada "pattern_database" no Ambiente de Trabalho
        self.db_path = desktop_dir / db_path
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Cria a subpasta para as imagens dos padrões dentro do desktop
        self.patterns_dir = self.db_path / "patterns"
        self.patterns_dir.mkdir(exist_ok=True)
        
        # O ficheiro metadata.json ficará guardado nesta pasta no teu Desktop
        self.metadata_file = self.db_path / "metadata.json"
        
        # Log no terminal para saberes exatamente onde o ficheiro foi parar
        print(f"[PatternDB] Base de dados configurada em: {self.metadata_file}")
        
        # Configurações originais do teu código
        self.max_patterns = 12
        self.patterns: Dict[int, PatternMetadata] = {}
        
        # Carrega os dados existentes
        self._load_metadata()
    
    def _load_metadata(self):
        """Carrega metadados do disco"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pid, meta_dict in data.items():
                        self.patterns[int(pid)] = PatternMetadata(**meta_dict)
                print(f"[PatternDB] {len(self.patterns)} padrões carregados.")
            except Exception as e:
                print(f"[PatternDB] Erro ao carregar metadados: {e}")
    
    def _save_metadata(self):
        """Guarda metadados no disco"""
        try:
            data = {str(pid): asdict(meta) for pid, meta in self.patterns.items()}
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[PatternDB] Erro ao guardar metadados: {e}")
    
    def _compute_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA256 do ficheiro"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
    
    def add_pattern(self, 
                   name: str,
                   image_frame: np.ndarray,
                   is_continuous: bool,
                   num_segments: int = 0,
                   segment_spacing_mm: float = 0.0,
                   notes: str = "",
                   zone_profiles: List[Dict] = None,
                   guide_length_px: int = 0,
                   guide_width_px: int = 0) -> Tuple[bool, str, int]:
        """Adiciona um novo padrão à base de dados com as dimensões reais cortadas."""
        if len(self.patterns) >= self.max_patterns:
            return False, f"Limite de {self.max_patterns} padrões atingido", -1
        
        pattern_id = None
        for i in range(1, self.max_patterns + 1):
            if i not in self.patterns:
                pattern_id = i
                break
        
        if pattern_id is None:
            return False, "Sem espaço disponível na base de dados", -1
        
        try:
            h, w = image_frame.shape[:2]
            # CORREÇÃO: Usa as dimensões reais da guia cortada (se enviadas pelo vision.py)
            final_length = guide_length_px if guide_length_px > 0 else w
            final_width = guide_width_px if guide_width_px > 0 else h
            
            brightness_profile = self._calculate_brightness_profile(image_frame)
            color_profile = self._calculate_color_profile(image_frame)
            
            file_path = str(self.patterns_dir / f"pattern_{pattern_id:02d}_{name}.jpg")
            cv2.imwrite(file_path, image_frame)
            file_hash = self._compute_file_hash(file_path)
            
            from datetime import datetime
            timestamp = datetime.now().isoformat()
            
            metadata = PatternMetadata(
                pattern_id=pattern_id,
                name=name,
                file_path=file_path,
                is_continuous=is_continuous,
                num_segments=num_segments,
                segment_spacing_mm=segment_spacing_mm,
                light_guide_length_px=final_length,  # Foi corrigido
                light_guide_width_px=final_width,    # Foi corrigido
                timestamp=timestamp,
                hash=file_hash,
                brightness_profile=brightness_profile,
                color_profile=color_profile,
                is_valid=True,
                notes=notes,
                zone_profiles=zone_profiles 
            )
            
            self.patterns[pattern_id] = metadata
            self._save_metadata()
            return True, f"Padrão '{name}' adicionado (ID: {pattern_id})", pattern_id
            
        except Exception as e:
            return False, f"Erro ao adicionar padrão: {e}", -1
    
    def get_pattern(self, pattern_id: int) -> Optional[Tuple[np.ndarray, PatternMetadata]]:
        """Carrega um padrão da base de dados"""
        if pattern_id not in self.patterns:
            return None
        
        metadata = self.patterns[pattern_id]
        try:
            image = cv2.imread(metadata.file_path)
            if image is None:
                print(f"[PatternDB] Aviso: Não foi possível carregar a imagem do padrão {pattern_id}")
                return None
            return image, metadata
        except Exception as e:
            print(f"[PatternDB] Erro ao carregar padrão {pattern_id}: {e}")
            return None
    
    def list_patterns(self) -> List[Dict]:
        """Lista todos os padrões com informações resumidas"""
        result = []
        for pid in sorted(self.patterns.keys()):
            meta = self.patterns[pid]
            result.append({
                "id": pid,
                "name": meta.name,
                "type": "Contínua" if meta.is_continuous else "Segmentada",
                "segments": meta.num_segments,
                "width": meta.light_guide_length_px,
                "height": meta.light_guide_width_px,
                "spacing": meta.segment_spacing_mm,
                "valid": meta.is_valid
            })
        return result
    
    def delete_pattern(self, pattern_id: int) -> Tuple[bool, str]:
        """Remove um padrão da base de dados"""
        if pattern_id not in self.patterns:
            return False, f"Padrão {pattern_id} não encontrado"
        
        try:
            metadata = self.patterns[pattern_id]
            if os.path.exists(metadata.file_path):
                os.remove(metadata.file_path)
            del self.patterns[pattern_id]
            self._save_metadata()
            return True, f"Padrão {pattern_id} removido com sucesso"
        except Exception as e:
            return False, f"Erro ao remover padrão: {e}"
    
    def _calculate_brightness_profile(self, image: np.ndarray, num_samples: int = 20) -> List[float]:
        """
        Calcula perfil de brilho ao longo da guia.
        Divide a guia em 20 secções e calcula brilho médio em cada uma.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape[:2]
        
        profile = []
        section_width = w // num_samples
        
        for i in range(num_samples):
            start = i * section_width
            end = start + section_width if i < num_samples - 1 else w
            section = gray[:, start:end]
            brightness = float(np.mean(section))
            profile.append(brightness)
        
        return profile
    
    def _calculate_color_profile(self, image: np.ndarray) -> Dict[str, float]:
        """
        Calcula perfil de cor (valores CIE L*a*b* médios).
        Simplificado para media geral da imagem.
        """
        # Converte para LAB para análise de cor mais robusta
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_mean, a_mean, b_mean = cv2.mean(lab)[:3]
        
        return {
            "L": float(l_mean),
            "a": float(a_mean),
            "b": float(b_mean)
        }
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da base de dados"""
        continuous_count = sum(1 for m in self.patterns.values() if m.is_continuous)
        segmented_count = sum(1 for m in self.patterns.values() if not m.is_continuous)
        
        return {
            "total_patterns": len(self.patterns),
            "continuous": continuous_count,
            "segmented": segmented_count,
            "max_capacity": self.max_patterns,
            "used_slots": len(self.patterns),
            "available_slots": self.max_patterns - len(self.patterns)
        }
