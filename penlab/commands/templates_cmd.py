"""
templates_cmd.py
=====================

Agrupa los comandos relacionados con la gestión de templates en Penlab.

Las *templates* definen la estructura base de los proyectos de pentesting, incluyendo
carpetas, archivos y variables personalizables. Este módulo permite listar, visualizar
e importar dichas plantillas para su reutilización.

Comandos:
- `penlab templates list`: Lista todas las plantillas instaladas localmente.
- `penlab templates show <template_name>`: Muestra la información detallada de una 
    plantilla específica (nombre, versión, autor, etc.).
- `penlab templates import <file_path>`: Importa una nueva plantilla desde un archivo YAML válido.

Ejemplo de uso:
------------------
    $ penlab templates list
    $ penlab templates show default
    $ penlab templates import ./templates/webpentest.yaml
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
import yaml
import shutil

from penlab.config import ensure_penlab_structure, TEMPLATES_DIR
from penlab.templates import load_template, validate_template
from penlab.ui_theme import THEME

console = Console()

# ============================================================
# GRUPO: templates (gestión de plantillas)
# ============================================================
@click.group()
def templates ():
    """ Gestión de templates"""
    pass

# ============================================================
# COMANDO: LIST (listar templates disponibles)
# ============================================================
@templates.command(name='list')
def list_templates ():
    """
    Lista todas las plantillas (*templates*) disponibles en el entorno Penlab.

    Este comando muestra en una tabla las plantillas instaladas localmente, ubicadas
    en el directorio configurado en `TEMPLATES_DIR`.  
    Cada fila de la tabla incluye el nombre, versión, descripción y etiquetas de la plantilla.

    Si no se encuentra ninguna plantilla instalada, se muestra una advertencia junto con
    la sugerencia de importar una nueva mediante `penlab templates import <archivo>`.

    Ejemplo:
        $ penlab templates list
    """
    ensure_penlab_structure()

    console.print(f'\n[{THEME["secondary"]}]Templates disponibles[/{THEME["secondary"]}]')
    
    template_files = list(TEMPLATES_DIR.glob('*.yaml'))

    if not template_files:
        console.print(f'[{THEME["warning"]}] No hay templates instalados [/{THEME["warning"]}]')
        console.print(f'[{THEME["dim"]}]Usa "penlab templates import <archivo>" para añadir templates[/{THEME["dim"]}]\n')
        return 
    
    table = Table(
        box=box.SIMPLE, 
        show_header=True, 
        header_style=f'bold {THEME["accent"]}'
    )
    table.add_column('Nombre', style=THEME['secondary'])
    table.add_column('Versión', style=THEME['success'])
    table.add_column('Descripción', style=THEME['info'], max_width=50)
    table.add_column('Tags', style=THEME['warning'])

    for template_file in template_files:
        try:
            with open(template_file, 'r') as f:
                data = yaml.safe_load(f) or {}

                name = str(data.get('name', template_file.stem))
                version = str(data.get('version', '1.0'))
                description = str(data.get('description', 'Sin descripción'))

                tags_data = data.get('tags', [])

                if isinstance(tags_data, (list, tuple)):
                    tags = ', '.join(map(str, tags_data))
                elif isinstance(tags_data, (str, int, float)):
                    tags = str(tags_data)
                else:
                    tags = ''

                table.add_row(name, version, description, tags)
        except:
            table.add_row(template_file.stem, '?', 'Error al cargar', '')

    console.print(table)
    console.print()

# ============================================================
# COMANDO: SHOW (mostrar detalles de una template)
# ============================================================
@templates.command(name='show')
@click.argument('template_name')
def show_template (template_name):
    """
    Muestra la información detallada de una plantilla específica.

    Este comando carga la plantilla indicada por su nombre (sin extensión `.yaml`)
    y muestra sus metadatos: nombre, versión, autor, descripción, etiquetas y variables.

    También lista las variables disponibles dentro de la plantilla, indicando su nombre
    y descripción correspondiente.

    Args:
        template_name (str): Nombre de la plantilla a mostrar.

    Ejemplo:
        $ penlab templates show default
    """
    template_data = load_template(template_name)

    if not template_data:
        return
    
    console.print()
    console.print(Panel.fit(
        f'[bold {THEME["secondary"]}]{template_data.get("name", template_name)}[/bold {THEME["secondary"]}]\n'
        f'[{THEME["dim"]}]Versión {template_data.get("version", 1.0)} | por {template_data.get("author", "Desconocido")}[/{THEME["dim"]}]\n\n'
        f'{template_data.get("description", "Sin descripción")}\n\n'
        f'[{THEME["warning"]}]Tags:[/{THEME["warning"]}] {", ".join(template_data.get("tags", []))}',
        title=f'[{THEME["success"]}] Template info[/{THEME["success"]}]',
        border_style=THEME["border"]
    ))

    if 'variables' in template_data:
        console.print(f'\n[{THEME["secondary"]}]Variables disponibles:[/{THEME["secondary"]}]')
 
        for var, desc in template_data['variables'].items():
            console.print(f' [{THEME["warning"]}]• {{{var}}}[/{THEME["warning"]}]: {desc}')

    console.print()

# ============================================================
# COMANDO: IMPORT (importar nueva template YAML)
# ============================================================
@templates.command(name='import')
@click.argument('file_path', type=click.Path(exists=True))
def import_template (file_path):
    """
    Importa una nueva plantilla (*template*) desde un archivo YAML.

    Este comando valida el archivo YAML proporcionado para verificar
    que cumple con la estructura esperada.  
    Si es válida, se copia al directorio de plantillas definido en `TEMPLATES_DIR`.

    Args:
        file_path (str): Ruta del archivo YAML a importar.

    Ejemplo:
        $ penlab templates import ./templates/redteam.yaml
    """
    ensure_penlab_structure()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f) or {}

        valid, errors = validate_template(template_data)

        if not valid:
            console.print(f'[{THEME["error"]}]✗ La template "{file_path}" no es válida. [{THEME["error"]}] Errores:')

            for err in errors:
                console.print(f'  - {err}')

            return

        template_name = template_data.get('name', Path(file_path).stem)
        dest_path = TEMPLATES_DIR / f'{template_name}.yaml'

        shutil.copy(file_path, dest_path)

        console.print(f'\n[{THEME["success"]}]✓[/{THEME["success"]}] Template "{template_name}" importado correctamente')
        console.print(f'[{THEME["dim"]}]Ubicación: {dest_path}[/{THEME["dim"]}]\n')

    except Exception as e:
        console.print(f'\n[{THEME["error"]}]✗[/{THEME["error"]}] Error al importar la template: {e}\n')