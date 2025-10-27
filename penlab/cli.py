"""
Penlab - CLI Tool para gestión de proyectos de pentesting.
"""

import click
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich import box
import yaml
from datetime import datetime
import shutil
import re

from penlab.notes import notes as notes_cli

INVALID_FILENAME_CHARS = r'<>:"/\\|?*\0'
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

console = Console()

# Configuración de paths.
PENLAB_HOME = Path.home() / '.penlab'
TEMPLATES_DIR = PENLAB_HOME / 'templates'
CONFIG_FILE = PENLAB_HOME / 'config.yaml'

# Configuración por defecto.
DEFAULT_CONFIG = {
    'your_ip': '10.10.14.x',
    'author': os.getenv('USER', 'pentester'),
    'default_template': 'default'
}

# ------------------------- Funciones de utilidados para proyectos -------------------------

def ensure_penlab_structure ():
    """ Crea la estructura de directorios de Penlab si no existe. """
    PENLAB_HOME.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)

def load_config ():
    """ Carga la configuración de Penlab. """
    ensure_penlab_structure()

    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
    except:
        return DEFAULT_CONFIG
    
def save_config (config):
    """ Guarda la configuración de Penlab. """
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)

def load_template (template_name):
    """ Carga un template desde el directorio de templates a partir de su nombre. """
    template_path = TEMPLATES_DIR / f'{template_name}.yaml'

    if not template_path.exists():
        console.print(f'[red]✗[/red] Template "{template_name}" no encontrado')

        return None
    
    try:
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f'[red]✗[/red] Error al cargar la template: {e}')
        
        return None
    
def create_structure (base_path, structure, variables):
    """ Crea la estructura de directorios y archivos recursivamente. """
    for item in structure:
        if 'dir' in item:
            dir_path: Path = base_path / item['dir']
            dir_path.mkdir(parents=True, exist_ok=True)

            if 'subdirs' in item:
                create_structure(dir_path, item['subdirs'], variables)

            if 'files' in item:
                for file_info in item['files']:
                    create_file(dir_path, file_info, variables)

def create_file (path, file_info, variables):
    """ Crea un archivo con contenido opcional. """
    file_path = path / file_info['name']
    content = file_info.get('content', '')

    for var, value in variables.items():
       content = content.replace(f'{{{var}}}', str(value))

    with open(file_path, 'w') as f:
        f.write(content)

    if file_info.get('executable', False):
        file_path.chmod(0o755) 

@click.group(invoke_without_command=True)
@click.pass_context
def cli (ctx):
    """ Penlab - Herramienta CLI para gestión de proyectos de pentesting. """

    if ctx.invoked_subcommand is None:
        show_banner()

def show_banner ():
    """ Muestra el banner principal de Penlab. """
    banner = Text()
    banner.append("╔═══════════════════════════════════════════════════════════╗\n", style="cyan bold")
    banner.append("║                                                           ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██████╗ ███████╗███╗   ██╗██╗      █████╗ ██████╗", style="red bold")
    banner.append("    ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██╔══██╗██╔════╝████╗  ██║██║     ██╔══██╗██╔══██╗", style="red bold")
    banner.append("   ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██████╔╝█████╗  ██╔██╗ ██║██║     ███████║██████╔╝", style="red bold")
    banner.append("   ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██╔═══╝ ██╔══╝  ██║╚██╗██║██║     ██╔══██║██╔══██╗", style="red bold")
    banner.append("   ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██║     ███████╗██║ ╚████║███████╗██║  ██║██████╔╝", style="red bold")
    banner.append("   ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═════╝", style="red bold")
    banner.append("    ║\n", style="cyan bold")
    banner.append("║                                                           ║\n", style="cyan bold")
    banner.append("║            ", style="cyan bold")
    banner.append("Pentesting Project Management Tool", style="yellow bold")
    banner.append("             ║\n", style="cyan bold")
    banner.append("║                      ", style="cyan bold")
    banner.append("v1.0.0", style="green")
    banner.append("                               ║\n", style="cyan bold")
    banner.append("║                                                           ║\n", style="cyan bold")
    banner.append("╚═══════════════════════════════════════════════════════════╝", style="cyan bold")
    
    console.print(banner)
    console.print()

    # Tabla de comandos principales.
    table = Table(title='Comandos disponibles', box=box.ROUNDED, show_header=True, header_style='bold magenta')
    table.add_column('Comando', style='cyan', width=40)
    table.add_column('Descripción', style='white')

    table.add_row(
        'penlab init <proyecto>',
        'Crea un nuevo proyecto de pentesting'
    )

    table.add_row(
        'penlab templates list',
        'Lista de las templates disponibles'
    )

    table.add_row(
        'penlab templates show <nombre>',
        'Muestra detalles de una template'
    )

    table.add_row(
        'penlab templates import <archivo>',
        'Importa un template desde un archivo YAML'
    )

    table.add_row(
        'penlab config',
        'Muestra la configuración actual'
    )

    table.add_row(
        'penlab set-config <key> <value>',
        'Establece un valor de configuración con el método clave valor'
    )

    console.print(table)
    console.print()

    # Tips
    console.print(Panel.fit(
        '[yellow] Tip:[/yellow] Usa [cyan]penlab init mi-proyecto --template htb --target 10.10.10.50[/cyan] para comenzar \n'
        '[yellow] Docs:[/yellow] https://github.com/hellsinki/penlab',
        title='[green]Getting Started[/green]',
        border_style='green'
    ))

# Comandos
@cli.command()
@click.argument('project_name')
@click.option('--template', '-t', default='default', help='Template a utilizar')
@click.option('--target', help='IP o dominio del target')
@click.option('--your-ip', help='Tu IP de atacante')
@click.option('--force', is_flag=True, help='Forzar la sobrescritura si existe (con precación)')
def init (project_name, template, target, your_ip):
    """ Inicializa un nuevo proyecto con la estructura de directorios indicada en la template (default) """
    console.print(f'\n[cyan] Inicializando proyecto: [/cyan] [bold]{project_name}[/bold]')
    console.print(f'[cyan] Template:[/cyan] {template}\n')

    config = load_config()

    # Cargar la template seleccionada ('default' por defecto).
    template_data = load_template(template)

    if not template_data:
        return

    # Se cran los directorios del proyecto.
    project_path = Path(project_name)

    template_defaults = template_data.get('variables', {}) or {}

    def resolve_var (key, cli_value=None, template_defaults=template_defaults, config=config, fallback=''):
        # 1) Valor pasado por CLI explícitamente (no None)
        if cli_value is not None:
            return cli_value
        
        # 2) Valor en la plantilla (template defaults)
        if key in template_defaults:
            return template_defaults[key]
        
        # 3) Valor en la configuración global
        if key in config:
            return config[key]
        
        # 4) Fallback hardcoded
        return fallback

    variables = {
        'project-name': project_name,
        'target': resolve_var('target', cli_value=target, fallback='TARGET_IP'),
        'your-ip': resolve_var('your-ip', cli_value=your_ip, fallback=config.get('your-ip', '10.10.x,x')),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'author': resolve_var('author', cli_value=None, fallback=config.get('author', 'pentester'))
    }

    for k, v in list(variables.items()):
        if v is None:
            variables[k] = ''
        else:
            variables[k] = str(v)

    if project_path.exists():
        console.print(f'[red]✗[/red] El directorio "{project_name}" ya existe')
        return 
    
    project_path.mkdir()

    with console.status('[bold green] Creando estructura...') as status:
        create_structure(project_path, template_data.get('structure', []), variables)

        for file_info in template_data.get('global_files', []):
            create_file(project_path, file_info, variables)

    console.print(f'\n[green]✓[/green] Proyecto creado exitosamente en: [cyan]{project_path.absolute()}[/cyan]')

    tree = Tree(f'[bold blue] {project_name}[/bold blue]')
    build_tree(tree, project_path)
    console.print()
    console.print(tree)

    console.print(f'\n[yellow]->[/yellow] cd {project_name}')
    console.print(f'[yellow]->[/yellow] cat README.md\n')

def build_tree (tree, path, max_depth = 3, current_depth = 0):
    """ Construye un árbol visual de la estructura de directorios """
    if current_depth >= max_depth:
        return 
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items[:20]:
            if item.is_dir():
                branch = tree.add(f'[blue] {item.name}[/blue]')
                build_tree(branch, item, max_depth, current_depth + 1)
            else:
                icon = '📄' if item.suffix in ['.md', '.txt'] else '📜'
                tree.add(f'[white]{icon} {item.name}[/white]')
    except PermissionError:
        pass

# Comandos de templates
@cli.group()
def templates ():
    """ Gestión de templates"""
    pass

@templates.command(name='list')
def list_templates ():
    """ Comando para listar todas las tempaltes disponibles """
    ensure_penlab_structure()

    console.print('\n[cyan]Templates disponibles[/cyan]')
    
    template_files = list(TEMPLATES_DIR.glob('*.yaml'))

    if not template_files:
        console.print('[yellow] No hay templates instalados [/yellow]')
        console.print('[dim]Usa "penlab templates import <archivo>" para añadir templates[/dim]\n')
        return 
    
    table = Table(box=box.SIMPLE, show_header=True, header_style='bold magenta')
    table.add_column('Nombre', style='cyan')
    table.add_column('Versión', style='green')
    table.add_column('Descripción', style='white', max_width=50)
    table.add_column('Tags', style='yellow')

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

@templates.command(name='show')
@click.argument('template_name')
def show_template (template_name):
    """ Muestra detalles de una template seleccionada """
    template_data = load_template(template_name)

    if not template_data:
        return
    
    console.print()
    console.print(Panel.fit(
        f'[bold cyan]{template_data.get("name", template_name)}[/bold cyan]\n'
        f'[dim]Versión {template_data.get("version", 1.0)} | por {template_data.get("author", "Desconocido")}[/dim]\n\n'
        f'{template_data.get("description", "Sin descripción")}\n\n'
        f'[yellow]Tags:[/yellow] {", ".join(template_data.get("tags", []))}',
        title='[green] Template info[/green]',
        border_style='cyan'
    ))

    if 'variables' in template_data:
        console.print('\n[cyan]Variables disponibles:[/cyan]')

        for var, desc in template_data['variables'].items():
            console.print(f' [yellow]• {{{var}}}[/yellow]: {desc}')

    console.print()

@templates.command(name='import')
@click.argument('file_path', type=click.Path(exists=True))
def import_template (file_path):
    """ Importa una template desde un archivo YAML """
    ensure_penlab_structure()

    try:
        with open(file_path, 'r') as f:
            template_data = yaml.safe_load(f)

        template_name = template_data.get('name', Path(file_path).stem)
        dest_path = TEMPLATES_DIR / f'{template_name}.yaml'

        shutil.copy(file_path, dest_path)

        console.print(f'\n[green]✓[/green] Template "{template_name}" importado correctamente')
        console.print(f'[dim]Ubicación: {dest_path}[/dim]\n')

    except Exception as e:
        console.print(f'\n[red]✗[/red] Error al importar la template: {e}\n')

@cli.command()
def config ():
    """ Muestra la configuración actual """
    config_data = load_config()

    console.print()
    
    table = Table(title='Configuración de Penlab', box=box.ROUNDED)
    table.add_column('Clave', style='cyan')
    table.add_column('Valor', style='yellow')

    for key, value in config_data.items():
        table.add_row(key, str(value))

    console.print(table)
    console.print(f'\n[dim]Archivo de configuración: {CONFIG_FILE}[/dim]\n')

@cli.command(name='set-config')
@click.argument('key')
@click.argument('value')
def set_config (key, value):
    """ Establece un valor de configuración a partir del par clave-valor """
    config_data = load_config()
    config_data[key] = value
    save_config(config_data)

    console.print(f'\n[green]✓[/green] Configuración actualizada: [cyan]{key}[/cyan] = [yellow]{value}[/yellow]\n')


cli.add_command(notes_cli, name='notes')


if __name__ == '__main__':
    cli()

