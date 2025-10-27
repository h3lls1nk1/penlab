"""
Penlab - CLI Tool para gestión de proyectos de pentesting.
"""

import click
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box
import yaml
from datetime import datetime
import shutil

from utils import sanitize_name, is_within_directory
from config import ensure_penlab_structure, load_config, save_config, TEMPLATES_DIR, CONFIG_FILE
from templates import load_template, validate_template
from project import create_file, create_structure
from ui import show_banner, build_tree

from penlab.notes import notes as notes_cli

console = Console()

INVALID_FILENAME_CHARS = r'<>:"/\\|?*\0'

def simulate_structure(base_path: Path, structure, variables, indent=0):
    """ Simula la creación de estructura para el modo dry-run """
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
    
@click.group(invoke_without_command=True)
@click.pass_context
def cli (ctx):
    """ Penlab - Herramienta CLI para gestión de proyectos de pentesting. """

    if ctx.invoked_subcommand is None:
        show_banner()



# ========================================= COMANDOS =========================================
# 
# COMANDO INIT 
@cli.command()
@click.argument('project_name')
@click.option('--template', '-t', default='default', help='Template a utilizar')
@click.option('--target', help='IP o dominio del target')
@click.option('--your-ip', help='Tu IP de atacante')
@click.option('--force', is_flag=True, help='Forzar la sobrescritura si existe (con precación)')
@click.option('--dry-run', is_flag=True, help='Simula la creación sin escribir archivos')
@click.option('--yes', is_flag=True, help='Responde "sí" a todas las confirmaciones')
def init (project_name, template, target, your_ip, force, dry_run, yes):
    """ Inicializa un nuevo proyecto con la estructura de directorios indicada en la template (default) """
    if dry_run:
        console.print('[yellow]⚠[/yellow] Modo DRY-RUN activado: no se crearán archivos reales\n')

    console.print(f'\n[cyan] Inicializando proyecto: [/cyan] [bold]{project_name}[/bold]')
    console.print(f'[cyan] Template:[/cyan] {template}\n')

    config = load_config()

    # Cargar la template seleccionada ('default' por defecto).
    template_data = load_template(template)

    if not template_data:
        return

    template_defaults = template_data.get('variables', {}) or {}

    def resolve_var (key, cli_value=None, fallback=''):
        # 1) Valor pasado por CLI explícitamente (no None)
        if cli_value not in (None, ''):
            return cli_value
        
        # 2) Valor en la plantilla (template defaults)
        if key in template_defaults and template_defaults[key] not in (None, ''):
            return template_defaults[key]
        
        # 3) Valor en la configuración global
        if key in config and config[key] not in (None, ''):
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
        variables[k] = '' if v is None else str(v)

    # project_name no puede ser absolut ni contener traversal
    # Sanitizamos el nombre base para crear la carpeta (no se permite si contiene / or \)
    if os.path.isabs(project_name):
        console.print(f'[red] Nombre de proyecto inválido: no uses rutas absolutas.[/red]')
        return
    
    if any(p in project_name for p in ('..', '/', '\\')):
        console.print(f'[red] Nombre de proyecto inválido: no uses ../ ni separadores de ruta.[/red]')
        return
    
    project_name_safe = sanitize_name(project_name, replace_with='-')
    project_path = (Path.cwd() / project_name_safe).resolve()
    cwd = Path.cwd().resolve()

    # Re-check
    if not is_within_directory(cwd, project_path):
        console.print(f'[red] Nombre de proyecto inválido: intento de crear fuera del directorio actual[/red]')
        return

    if project_path.exists():
        if dry_run:
            console.print(f'[yellow]ℹ[/yellow] DRY-RUN: El directorio ya existe y sería eliminado con --force')
        elif not force:
            console.print(f'[red]✗[/red] El directorio "{project_name}" ya existe')
            return 
        else:
            # Pedir confirmación si no se usa --yes
            if not yes:
                console.print(f'[yellow]⚠ ADVERTENCIA:[/yellow] Esto eliminará el directorio existente: {project_path}')
                confirm = click.confirm('¿Estás seguro de continuar?', default=False)
                if not confirm:
                    console.print('[yellow]Operación cancelada[/yellow]')
                    return
            
            try:
                shutil.rmtree(project_path)
                console.print(f'[yellow]✓[/yellow] Directorio existente eliminado')
            except Exception as e:
                console.print(f'[red]✗[/red] No se pudo eliminar el directorio existente: {e}')
                return
    
    # Crear estructura
    if dry_run:
        console.print(f'\n[yellow]DRY-RUN:[/yellow] Se crearían los siguientes elementos:\n')
        simulate_structure(project_path, template_data.get('structure', []), variables)
        
        global_files = template_data.get('global_files', [])
        if global_files:
            console.print(f'\n[cyan]📄 Archivos globales:[/cyan]')
            for file_info in global_files:
                if isinstance(file_info, dict) and 'name' in file_info:
                    file_name = str(file_info['name'])
                    for var, val in variables.items():
                        file_name = file_name.replace(f'{{{var}}}', val)
                    console.print(f'  • {project_path / sanitize_name(file_name, "_")}')
        
        console.print(f'\n[green]✓[/green] DRY-RUN completado. No se han creado archivos.')
        return
    
    # Creación real
    # Crear el directorio raíz
    try:
        project_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f'[red] Error al crear el directorio del proyecto: [/red] {e}')
        return 

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

# COMANDO TEMPLATES
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
        with open(file_path, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f) or {}

        valid, errors = validate_template(template_data)

        if not valid:
            console.print(f'[red]✗[/red] La template "{file_path}" no es válida. Errores:')

            for err in errors:
                console.print(f'  - {err}')

            return

        template_name = template_data.get('name', Path(file_path).stem)
        dest_path = TEMPLATES_DIR / f'{template_name}.yaml'

        shutil.copy(file_path, dest_path)

        console.print(f'\n[green]✓[/green] Template "{template_name}" importado correctamente')
        console.print(f'[dim]Ubicación: {dest_path}[/dim]\n')

    except Exception as e:
        console.print(f'\n[red]✗[/red] Error al importar la template: {e}\n')

# COMANDO CONFIG
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

# REGISTRO DE COMANDOS
cli.add_command(notes_cli, name='notes')

if __name__ == '__main__':
    cli()

