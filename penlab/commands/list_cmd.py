"""
list_cmd.py
=====================

Muestra en formato tabular todos los proyectos Penlab detectados en el directorio actual.

El comando busca subdirectorios que contengan el archivo `.penlab.yaml` —el archivo de metadatos 
generado por `penlab init`— y extrae de él la información básica del proyecto, como 
nombre, plantilla usada, target, fecha de creación y ruta.

Comandos
- `penlab list-projects`: Lista todos los proyectos Penlab del directorio actual.

Ejemplo de uso:
------------------
    $ penlab list-projects

"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
import yaml

from penlab.ui_theme import THEME

console = Console()

# ============================================================
# COMANDO: LIST-PROJECTS (listar proyectos Penlab)
# ============================================================
@click.command(name='list-projects')
def list_projects():
    """
    Lista todos los proyectos Penlab en el directorio actual.

    Este comando escanea los subdirectorios del directorio actual en busca
    de proyectos Penlab válidos (aquellos que contienen un archivo `.penlab.yaml`).
    Luego muestra la información resumida de cada uno en una tabla formateada.
    Si no se encuentra ningún proyecto, se muestra un mensaje informativo.

    Ejemplo:
        $ penlab list-projects
    """
    cwd = Path.cwd()
    projects = []

    for path in cwd.iterdir():
        if path.is_dir() and (path / '.penlab.yaml').exists():
            try:
                with open(path / '.penlab.yaml', 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}

                if not isinstance(data, dict):
                    data = {}

                projects.append({
                    'name': data.get('name', path.name),
                    'template': data.get('template', 'N/A'),
                    'target': data.get('target', '-'),
                    'created': data.get('created', '-'),
                    'path': str(path)
                })

            except yaml.YAMLError as e:
                console.print(
                    f'[{THEME["warning"]}]⚠ Advertencia: Error al leer {path.name}/.penlab.yaml'
                    f'[/{THEME["warning"]}]'
                )
                projects.append({
                    'name': path.name,
                    'template': 'N/A',
                    'target': '-',
                    'created': '-',
                    'path': str(path)
                })
            except Exception as e:
                console.print(
                    f'[{THEME["dim"]}]⚠ No se pudo leer {path.name}/.penlab.yaml: {e}'
                    f'[/{THEME["dim"]}]'
                )
                continue

    if not projects:
        console.print(f'[{THEME["warning"]}]No se encontraron proyectos Penlab en este directorio.')
        return

    table = Table(
        box=box.SIMPLE, 
        show_header=True, 
        header_style=f'bold {THEME["secondary"]}'
    )
    table.add_column('Proyecto', style=THEME['secondary'])
    table.add_column('Template', style=THEME['success'])
    table.add_column('Target', style=THEME['warning'])
    table.add_column('Creado', style=THEME['info'])
    table.add_column('Ruta', style=THEME['dim'])

    for p in projects:
        table.add_row(p['name'], p['template'], p['target'], p['created'], p['path'])

    console.print()
    console.print(table)