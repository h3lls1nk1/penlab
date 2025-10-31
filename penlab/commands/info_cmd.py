"""
info_cmd.py
=====================

Define comandos relacionados con la obtención y visualización
de información detallada sobre proyectos Penlab.

Comandos:
- `penlab info <project-name>`: Muestra la información del proyecto.

Busca el archivo de metadatos `.penlab.yaml` en el directorio del proyecto
especificado. Si el archivo existe, muestra la información del proyecto en 
un panel formateado.

Ejemplo de uso:
------------------
    $ penlab info project1
"""

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import yaml

from ui_theme import THEME

console = Console()

# ============================================================
# COMANDO: INFO (mostrar información de un proyecto)
# ============================================================
@click.command()
@click.argument('project_name')
def info(project_name):
    """
    Muestra información detallada de un proyecto Penlab.

    Este comando busca el archivo `.penlab.yaml` dentro del directorio del proyecto
    especificado y muestra sus datos formateados en un panel visual.

    Si el archivo de metadatos no existe, el comando notifica al usuario.

    Args:
        project_name (str): Nombre o ruta del proyecto cuyo archivo `.penlab.yaml`
        contiene la metadata.

    Ejemplo:
        $ penlab info prueba
    """
    project_path = Path(project_name).resolve()
    meta_path = project_path / '.penlab.yaml'

    if not meta_path.exists():
        console.print(f'[{THEME["error"]}]✗[{THEME["dim"]}] No se encontró metadata en {meta_path}[/{THEME["dim"]}]')
        return

    with open(meta_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}

    panel_content = (
        f"[bold {THEME["secondary"]}]Proyecto:[/bold {THEME["secondary"]}] {data.get('name')}\n"
        f"[bold {THEME["secondary"]}]Template:[/bold {THEME["secondary"]}] {data.get('template')}\n"
        f"[bold {THEME["secondary"]}]Target:[/bold {THEME["secondary"]}] {data.get('target')}\n"
        f"[bold {THEME["secondary"]}]Tu IP:[/bold {THEME["secondary"]}] {data.get('your-ip')}\n"
        f"[bold {THEME["secondary"]}]Autor:[/bold {THEME["secondary"]}] {data.get('author')}\n"
        f"[bold {THEME["secondary"]}]Creado:[/bold {THEME["secondary"]}] {data.get('created')}\n"
        f"[bold {THEME["secondary"]}]Ruta:[/bold {THEME["secondary"]}] {data.get('path')}\n"
    )

    console.print()
    console.print(Panel(
        panel_content, 
        title=f"[{THEME["primary"]}]Información del Proyecto[/{THEME["primary"]}]", 
        border_style=THEME['border']
    ))