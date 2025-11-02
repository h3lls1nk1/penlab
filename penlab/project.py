"""
project.py
=====================

Funciones para la creación y gestión de proyectos Penlab.

Este módulo contiene las funciones encargadas de:
- Generar la estructura de directorios y archivos de un proyecto a partir de una *template*.
- Crear archivos individuales reemplazando variables dinámicas.
- Guardar la metadata del proyecto en el archivo `.penlab.yaml`.

Estas funciones son utilizadas principalmente por el comando:
    `penlab init <project-name>`
"""
import os
import yaml
from pathlib import Path
from rich.console import Console
from datetime import datetime

from penlab.utils import sanitize_name, is_within_directory

console = Console()

# ============================================================
# FUNCIÓN: create_structure
# ============================================================
def create_structure (base_path: Path, structure, variables):
    """
    Crea la estructura de directorios y archivos de un proyecto Penlab.

    Recorre recursivamente la estructura definida en la plantilla YAML
    y genera los directorios y archivos correspondientes.  
    Evita que las rutas escapen del directorio base del proyecto.

    Args:
        base_path (Path): Ruta raíz del proyecto.
        structure (list): Lista de diccionarios con la definición de carpetas.
        variables (dict): Variables dinámicas (por ejemplo, {project-name}, {author}).

    Ejemplo:
        structure = [
            {
                "dir": "recon",
                "files": [{"name": "notes.md"}],
                "subdirs": [{"dir": "scans"}]
            }
        ]
    """
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

# ============================================================
# FUNCIÓN: create_file
# ============================================================
def create_file (path: Path, file_info, variables):
    """
    Crea un archivo en la ruta indicada y escribe contenido dinámico opcional.

    Args:
        path (Path): Directorio donde se creará el archivo.
        file_info (dict): Información del archivo (nombre, contenido, permisos).
        variables (dict): Variables que serán sustituidas en nombre y contenido.
    """
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

# ============================================================
# FUNCIÓN: save_project_metadata
# ============================================================
def save_project_metadata (project_path: Path, variables: dict, template_name: str):
    """
    Guarda la metadata básica del proyecto en `.penlab.yaml`.

    Este archivo almacena la información esencial del proyecto:
    nombre, plantilla usada, IPs, autor, fecha de creación y ruta.

    Args:
        project_path (Path): Ruta del proyecto.
        variables (dict): Variables del proyecto (nombre, autor, etc.).
        template_name (str): Nombre de la plantilla utilizada.
    """
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