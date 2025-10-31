"""
cli.py
=====================

Penlab CLI - Herramienta principal para la gestión de proyectos de pentesting.

Este módulo define el punto de entrada de la aplicación de línea de comandos (CLI) de Penlab.
Centraliza el registro de todos los subcomandos y gestiona la interfaz principal que los agrupa.

Subcomandos principales:
------------------------
- `penlab init <project_name>`  
    Inicializa un nuevo proyecto Penlab a partir de una plantilla.

- `penlab list-projects`  
    Lista los proyectos Penlab detectados en el directorio actual.

- `penlab info <project_name>`  
    Muestra información detallada de un proyecto existente.

- `penlab templates ...`  
    Permite gestionar las plantillas disponibles (listar, mostrar, importar).

- `penlab config ...`  
    Administra la configuración global de Penlab (autor, IP, etc.).

Ejemplo de uso:
------------------
    $ penlab init prueba
    $ penlab list-projects
    $ penlab info prueba
    $ penlab templates list
    $ penlab config show
"""

import click
from rich.console import Console

# Importaciones de los subcomandos.
from commands.init_cmd import init
from commands.list_cmd import list_projects
from commands.info_cmd import info
from commands.templates_cmd import templates
from commands.config_cmd import config

from ui import show_banner
from config import ensure_penlab_structure
from penlab.notes import notes as notes_cli # Pendiente de validación y habilitación # 

console = Console()

ensure_penlab_structure()

# ============================================================
# GRUPO PRINCIPAL: penlab
# ============================================================
@click.group(invoke_without_command=True)
@click.pass_context
def cli (ctx):
    """
    Penlab - Herramienta CLI para gestión de proyectos de pentesting.

    Si se ejecuta sin argumentos, muestra un banner visual junto con
    una breve guía de uso.  
    Usa `penlab --help` para listar los subcomandos disponibles.
    """
    if ctx.invoked_subcommand is None:
        show_banner()
        click.echo()
        click.echo('Usa "penlab --help" para ver los comandos disponibles.')
        ctx.exit()

# ============================================================
# REGISTRO DE COMANDOS
# ============================================================
cli.add_command(init)
cli.add_command(list_projects)
cli.add_command(info)
cli.add_command(templates)
cli.add_command(config)

# (Pendiente de habilitar: módulo de notas)
# cli.add_command(notes_cli, name='notes')

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main ():
    """
    Punto de entrada del CLI de Penlab.

    Esta función inicializa el grupo principal de comandos `cli`
    y gestiona la ejecución según los argumentos proporcionados
    por el usuario.
    """
    cli()

if __name__ == '__main__':
    main()

