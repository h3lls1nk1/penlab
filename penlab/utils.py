"""
Utilidades generales para Penlab.
"""
import re
from pathlib import Path

INVALID_FILENAME_REGEX = re.compile(r'[<>:"/\\|?\*\x00]')

def sanitize_name (name: str, replace_with: str = '_') -> str:
    """ Reemplaza caracteres inválidos en nombres de archivos/directorios y recorta
     espacios al inicio/final. Mantiene guiones y underscores. """
    
    if not isinstance(name, str):
        name = str(name)

    name = INVALID_FILENAME_REGEX.sub(replace_with, name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name[:255] if len(name) > 255 else name

def is_within_directory (base: Path, target: Path) -> bool:
    """ Comprueba que 'target' esté dentro de 'base' """
    try:
        base_res = base.resolve()
        target_res = target.resolve()
    except Exception:
        return False
    
    try:
        return str(target_res).startswith(str(base_res))
    except Exception:
        return False