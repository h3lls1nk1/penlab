"""
init_cmd.py
=====================

Inicializa un nuevo proyecto Penlab a partir de una plantilla (template).

El comando genera la estructura de carpetas, archivos base y metadatos del proyecto.
Además, permite realizar una simulación de creación (modo `--dry-run`) o sobrescribir
un proyecto existente con confirmación manual o automática.

Comandos:
- `penlab init <project_name>`: Crea un nuevo proyecto con la estructura definida por la template.

Ejemplo de uso:
------------------
    $ penlab init prueba
    $ penlab init pentest01 -t web --target 10.10.10.5 --your-ip 10.10.14.2
    $ penlab init redteam --dry-run
"""

import os
import shutil
import click
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.rule import Rule

from penlab.config import load_config
from penlab.templates import load_template
from penlab.utils import sanitize_name, is_within_directory, simulate_structure
from penlab.project import save_project_metadata, create_structure, create_file
from penlab.ui import build_tree
from penlab.ui_theme import THEME

console = Console()

# ============================================================
# COMANDO: INIT (crear nuevo proyecto Penlab)
# ============================================================
@click.command()
@click.argument('project_name')
@click.option('--template', '-t', default='default', help='Template a utilizar')
@click.option('--target', help='IP o dominio del target')
@click.option('--your-ip', help='Tu IP atacante')
@click.option('--force', is_flag=True, help='Forzar sobrescritura si existe')
@click.option('--dry-run', is_flag=True, help='Simula la creación sin escribir archivos')
@click.option('--yes', '-y', is_flag=True, help='Responde "sí" automáticamente')
def init(project_name, template, target, your_ip, force, dry_run, yes):
    """
    Inicializa un nuevo proyecto Penlab con la estructura de una template.

    Crea una nueva carpeta de proyecto y genera la estructura de directorios,
    archivos y metadatos a partir de la plantilla especificada.

    Si el proyecto ya existe, se puede sobrescribir con la opción `--force`.
    También puede ejecutarse en modo de simulación (`--dry-run`) para ver qué se crearía
    sin modificar el sistema de archivos.

    Args:
        project_name (str): Nombre del nuevo proyecto a crear.
        template (str, opcional): Nombre de la plantilla a usar (por defecto, `default`).
        target (str, opcional): IP o dominio del objetivo.
        your_ip (str, opcional): IP del atacante.
        force (bool): Si se pasa, permite sobrescribir proyectos existentes.
        dry_run (bool): Si se pasa, simula la creación sin escribir archivos reales.
        yes (bool): Si se pasa, acepta automáticamente confirmaciones al sobrescribir.

    Ejemplo:
        $ penlab init prueba
        $ penlab init web01 -t web --target 10.10.10.10 --your-ip 10.10.14.5
        $ penlab init demo --dry-run
    """    
    # Encabezado visual de inicio.
    console.print(Rule(f'[bold {THEME["accent"]}] ⚔ PENLAB INIT [/bold {THEME["accent"]}]'))
    console.print()

    if dry_run:
        console.print(f'[{THEME["warning"]}][{THEME["text"]}] Modo DRY-RUN activado: no se crearán archivos reales. [/{THEME["text"]}]')

    # Panel inicial con resumen del nuevo proyecto.
    console.print(
        Panel.fit(
            f'[{THEME["text"]}]Proyecto:[/{THEME["text"]}] [bold {THEME["accent"]}]{project_name}[/bold {THEME["accent"]}]\n'
            f'[{THEME["text"]}]Template:[/{THEME["text"]}] [{THEME["secondary"]}]{template}[/{THEME["secondary"]}]',
            border_style=THEME['border'],
            title=f'[bold {THEME["accent"]}]Inicialización[/bold {THEME["accent"]}]',
            subtitle=f'[{THEME["dim"]}]Penlab Hub [/{THEME["dim"]}]',
        )
    )

    # ============================================================
    # Carga de configuración y plantilla base
    # ============================================================
    config = load_config()
    template_data = load_template(template)

    if not template_data:
        console.print(f'[{THEME["error"]}]✗[{THEME["text"]}] No se pudo cargar la template.[/{THEME["text"]}]')
        return

    template_defaults = template_data.get('variables', {}) or {}

    def resolve_var(key, cli_value=None, fallback=''):
        if cli_value not in (None, ''):
            return cli_value
        if key in template_defaults and template_defaults[key] not in (None, ''):
            return template_defaults[key]
        if key in config and config[key] not in (None, ''):
            return config[key]
        return fallback

    variables = {
        'project-name': project_name,
        'target': resolve_var('target', cli_value=target, fallback='TARGET_IP'),
        'your-ip': resolve_var('your-ip', cli_value=your_ip, fallback=config.get('your-ip', '10.10.x.x')),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'author': resolve_var('author', fallback=config.get('author', 'pentester')),
    }

    # ============================================================
    # Validaciones de entrada
    # ============================================================
    if os.path.isabs(project_name) or any(p in project_name for p in ('..', '/', '\\')):
        console.print(f'[{THEME["error"]}]✗[{THEME["text"]}] Nombre de proyecto inválido.[/{THEME["text"]}]')
        return

    project_name_safe = sanitize_name(project_name, replace_with='-')
    project_path = (Path.cwd() / project_name_safe).resolve()
    cwd = Path.cwd().resolve()

    if not is_within_directory(cwd, project_path):
        console.print(f'[{THEME["error"]}]✗[{THEME["text"]}] Nombre inválido: intenta crear fuera del directorio actual.')
        return

    # ============================================================
    # Manejo de proyectos existentes
    # ============================================================
    if project_path.exists():
        if dry_run:
            console.print(f'[{THEME["warning"]}][/{THEME["warning"]}] [{THEME["dim"]}]DRY-RUN: El directorio ya existe y sería eliminado con --force[/{THEME["dim"]}]')
        elif not force:
            console.print(f'[{THEME["error"]}]✗[/{THEME["error"]}] El directorio [{THEME["secondary"]}]{project_name}[/{THEME["secondary"]}] ya existe.')
            return
        else:
            if not yes:
                console.print(
                    Panel.fit(
                        f'[{THEME["warning"]}]⚠ Esto eliminará el directorio existente:[/{THEME["warning"]}]\\n[{THEME["dim"]}] {project_path} [/{THEME["dim"]}]',
                        title=f'[bold {THEME["primary"]}]Confirmación requerida[/{THEME["primary"]}]',
                        border_style=THEME['warning'],
                    )
                )
                if not click.confirm('¿Deseas continuar?', default=False):
                    console.print(f'[{THEME["warning"]}]Operación cancelada.[/{THEME["warning"]}]')
                    return
            try:
                shutil.rmtree(project_path)
                console.print(f'[{THEME["error"]}][/{THEME["error"]}] [{THEME["success"]}]Directorio existente eliminado.[/{THEME["success"]}]')
            except Exception as e:
                console.print(f'[{THEME["error"]}]✗ Error al eliminar directorio existente:[/{THEME["error"]}] {e}')
                return

    # ============================================================
    # Simulación (modo DRY-RUN)
    # ============================================================
    if dry_run:
        console.print(Rule(f'[bold {THEME["primary"]}]Simulación de estructura[/bold {THEME["primary"]}]', style=THEME['border']))
        simulate_structure(project_path, template_data.get('structure', []), variables)

        global_files = template_data.get('global_files', [])
        if global_files:
            console.print(f'\n[{THEME["secondary"]}]📄 Archivos globales:[/{THEME["secondary"]}]')
            for file_info in global_files:
                if isinstance(file_info, dict) and 'name' in file_info:
                    file_name = str(file_info['name'])
                    for var, val in variables.items():
                        file_name = file_name.replace(f'{{{var}}}', val)
                    console.print(f'  [{THEME["dim"]}]•[/{THEME["dim"]}] {project_path / sanitize_name(file_name, "_")}')

        console.print(f'\n[{THEME["success"]}]✓ DRY-RUN completado. No se han creado archivos.[/{THEME["success"]}]')
        return

    # ============================================================
    # Creación real del proyecto
    # ============================================================
    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f'[{THEME["error"]}]✗ Error al crear directorio del proyecto:[/{THEME["error"]}] {e}')
        return

    with console.status(f'[bold {THEME["primary"]}] Creando estructura...[/bold {THEME["primary"]}]', spinner="dots"):
        create_structure(project_path, template_data.get('structure', []), variables)
        for file_info in template_data.get('global_files', []):
            create_file(project_path, file_info, variables)

    # ============================================================
    # Mensaje de finalización
    # ============================================================
    console.print()
    console.print(
        Panel.fit(
            f'[{THEME["success"]}]✓ Proyecto creado exitosamente[/{THEME["success"]}]\n'
            f'[{THEME["text"]}]Ubicación:[/{THEME["text"]}] [{THEME["secondary"]}]{project_path}[/{THEME["secondary"]}]',
            title=f'[bold {THEME["accent"]}]Finalizado[/bold {THEME["accent"]}]',
            border_style=THEME["border"],
        )
    )

    # ============================================================
    # Árbol visual del proyecto y metadatos
    # ============================================================
    console.print()
    tree = Tree(f'[bold {THEME["accent"]}]{project_name}[/bold {THEME["accent"]}]', guide_style=THEME['dim'])
    build_tree(tree, project_path)
    console.print(tree)

    
    console.print()
    console.print(f'[{THEME["secondary"]}]->[/{THEME["secondary"]}] cd [bold {THEME["accent"]}]{project_name}[/bold {THEME["accent"]}]')
    console.print(f'[{THEME["secondary"]}]->[/{THEME["secondary"]}] cat README.md\n')
    
    save_project_metadata(project_path, variables, template)
