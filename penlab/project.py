"""
Creación y gestión de proyectos de Penlab.
"""
import os
import yaml
from pathlib import Path
from rich.console import Console
from datetime import datetime

from utils import sanitize_name, is_within_directory

console = Console()

def create_structure (base_path: Path, structure, variables):
    """ Crea la estructura de directorios y archivos recursivamente sin escapar del base_path. """
    if not isinstance(structure, (list, tuple)):
        return
    
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
            console.print(f'[red]✗[/red] Ruta inválida en template (intentando salir de {base_path}): {dir_path}')
            continue

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f'[red]✗[/red] No se pudo crear la carpeta {dir_path}: {e}')
            continue

        if 'subdirs' in item:
            create_structure(dir_path, item.get('subdirs', []), variables)

        if 'files' in item:
            for file_info in item.get('files', []):
                create_file(dir_path, file_info, variables)

def create_file (path: Path, file_info, variables):
    """ Crea un archivo con contenido opcional. """
    if not isinstance(file_info, dict):
        return
    
    raw_name = file_info.get('name')

    if not raw_name:
        return
    
    name = str(raw_name)

    for var, val in variables.items():
        name = name.replace(f'{{{var}}}', val)

    name = sanitize_name(name, replace_with='_')
    file_path = path / name

    # Verificar que el archivo final esté dentro del proyecto
    if not is_within_directory(path.parent.resolve(), file_path.resolve() if file_path.exists() else path.resolve()):
        console.print(f'[red]✗[/red] Ruta de archivo inválida: {file_path}')
        return
    
    content = file_info.get('content', '')

    for var, value in variables.items():
        content = content.replace(f'{{{var}}}', str(value))

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        console.print(f'[red]✗[/red] Error escribiendo archivo {file_path}: {e}')
        return
    
    if file_info.get('executable', False):
        try:
            if os.name == 'posix':
                file_path.chmod(0o755)
        except Exception:
            pass

def save_project_metadata (project_path: Path, variables: dict, template_name: str):
    """ Guarda un archivo .penlab.yaml con información básica del proyecto. """
    metadata = {
        'name': variables.get('project-name'),
        'template': template_name,
        'target': variables.get('target'),
        'your-ip': variables.get('your-ip'),
        'author': variables.get('author'),
        'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'path': str(project_path.resolve())
    }

    meta_path = project_path / '.penlab.yaml'

    try:
        with open(meta_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(metadata, f, allow_unicode=True)

        console.print(f'[dim]→ Metadata guardada en {meta_path}[/dim]')
    except Exception as e:
        console.print(f'[red]✗ Error guardando metadata del proyecto:[/red] {e}')