"""
utils.py
=====================

Funciones de utilidades generales para Penlab.

Este módulo agrupa funciones auxiliares utilizadas por el núcleo del framework,
especialmente para validación de rutas, limpieza de nombres de archivo y
simulación visual de estructuras de proyecto (modo `--dry-run`).
"""
import re
from pathlib import Path
from rich.console import Console

console = Console()

INVALID_FILENAME_REGEX = re.compile(r'[<>:"/\\|?\*\x00]')

# ============================================================
# FUNCIÓN: sanitize_name
# ============================================================
def sanitize_name (name: str, replace_with: str = '_') -> str:
    """
    Limpia un nombre de archivo o directorio reemplazando caracteres inválidos.

    Esta función garantiza que los nombres sean válidos en sistemas de archivos
    modernos (Windows, Linux, macOS), reemplazando caracteres prohibidos
    (`<>:"/\\|?*`) por un carácter seguro.

    Args:
        name (str): Nombre a sanitizar.
        replace_with (str): Carácter de reemplazo para los inválidos. Por defecto "_".

    Returns:
        str: Nombre limpio y seguro para usar en el sistema de archivos.
    """    
    if not isinstance(name, str):
        name = str(name)

    name = INVALID_FILENAME_REGEX.sub(replace_with, name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name[:255] if len(name) > 255 else name

# ============================================================
# FUNCIÓN: is_within_directory
# ============================================================
def is_within_directory (base: Path, target: Path) -> bool:
    """
    Comprueba que una ruta objetivo (`target`) esté dentro del directorio base (`base`).

    Previene accesos fuera de la carpeta del proyecto (ataques de path traversal)
    y garantiza que las rutas generadas sean seguras.

    Args:
        base (Path): Directorio raíz permitido.
        target (Path): Ruta que se desea validar.

    Returns:
        bool: True si `target` se encuentra dentro de `base`, False en caso contrario.
    """
    try:
        base_res = base.resolve()
        target_res = target.resolve()
    except Exception:
        return False
    
    try:
        return str(target_res).startswith(str(base_res))
    except Exception:
        return False
    
# ============================================================
# FUNCIÓN: simulate_structure
# ============================================================
def simulate_structure(base_path: Path, structure, variables, indent=0):
    """
    Simula visualmente la creación de una estructura de directorios y archivos.

    Esta función **no crea archivos**, solo imprime una vista jerárquica de cómo
    quedaría la estructura del proyecto (modo `--dry-run`), aplicando variables
    dinámicas (por ejemplo `{target}` o `{project}`).

    Args:
        base_path (Path): Ruta base del proyecto.
        structure (list): Lista de diccionarios que describen carpetas y archivos.
        variables (dict): Variables dinámicas a reemplazar dentro de los nombres.
        indent (int, opcional): Nivel de indentación visual (solo para recursión interna).
    """
    if not isinstance(structure, (list, tuple)):
        return
    
    prefix = "  " * indent
    
    for item in structure:
        if not isinstance(item, dict):
            continue
        
        raw_dir = item.get('dir')
        if not raw_dir:
            continue

        dir_name = str(raw_dir)
        for var, val in variables.items():
            dir_name = dir_name.replace(f'{{{var}}}', val)

        dir_name = sanitize_name(dir_name, replace_with='-')
        dir_path = base_path / dir_name

        if not is_within_directory(base_path, dir_path):
            console.print(f'{prefix}[red]✗ INVÁLIDO:[/red] {dir_path}')
            continue

        console.print(f'{prefix}[blue]📁 {dir_name}/[/blue]')

        # Archivos en este directorio
        if 'files' in item:
            for file_info in item.get('files', []):
                if isinstance(file_info, dict) and 'name' in file_info:
                    file_name = str(file_info['name'])
                    for var, val in variables.items():
                        file_name = file_name.replace(f'{{{var}}}', val)
                    file_name = sanitize_name(file_name, replace_with='_')
                    executable = ' [green](executable)[/green]' if file_info.get('executable') else ''
                    console.print(f'{prefix}  📄 {file_name}{executable}')

        # Subdirectorios
        if 'subdirs' in item:
            simulate_structure(dir_path, item.get('subdirs', []), variables, indent + 1)