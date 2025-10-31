"""
config_cmd.py
=====================

Define comandos relacionados con la gestión de la configuración global de Penlab.

Comandos:
- `penlab config`: Muestra la configuración actual.
- `penlab set-config <clave> <valor>`: Modifica o añade una clave-valor en la configuración.

Interactúan con el archivo de configuración global
definido en `CONFIG_FILE`.

Ejemplo de uso:
------------------
    $ penlab config
    $ penlab set-config author 'John Doe'
"""

import click
from rich.console import Console
from rich.table import Table
from rich import box

from ui_theme import THEME
from config import load_config, save_config, CONFIG_FILE

console = Console()


# ============================================================
# GRUPO: CONFIG
# ============================================================
@click.group()
def config():
    """
    Gestiona la configuración global de Penlab.
    """
    pass

# ============================================================
# COMANDO: CONFIG (mostrar configuración)
# ============================================================
@config.command(name='show')
def show_config ():
    """ 
    Muestra la configuración actual del entorno Penlab.

    Lee el archivo de configuración global (por defecto `~/.penlab/config.yaml`)
    y presenta las claves y valores almacenados en una tabla visual.

    Ejemplo:
        $ penlab config show
    """
    config_data = load_config()

    console.print()
    
    table = Table(
        title=f'[{THEME["primary"]}]Configuración de Penlab[/{THEME["primary"]}]', 
        box=box.ROUNDED,
        border_style=THEME['border'],
        header_style=f'bold {THEME["primary"]}'
    )
    table.add_column('Clave', style=THEME['secondary'], no_wrap=True)
    table.add_column('Valor', style=THEME['info'])

    for key, value in config_data.items():
        table.add_row(key, str(value))

    console.print(table)
    console.print(f'\n[{THEME["dim"]}]Archivo de configuración: {CONFIG_FILE}[/{THEME["dim"]}]\n')

# ============================================================
# COMANDO: SET-CONFIG (establecer valores)
# ============================================================
@config.command(name='set')
@click.argument('key')
@click.argument('value')
def set_config (key, value):
    """ 
    Establece un valor de configuración a partir del par clave-valor.

    Permite modificar o añadir una entrada en el archivo de configuración de Penlab
    mediante un par clave-valor.

    Args:
        key (str): Clave de configuración (por ejemplo, 'author').
        value (str): Valor asociado a la clave (por ejemplo, 'John Doe'). 
    
    Ejemplo:
        $ penlab config set author 'John Doe'
        $ penlab config set your-ip '10.10.10.10'
    """
    config_data = load_config()
    config_data[key] = value
    save_config(config_data)

    console.print(
        f'\n[{THEME["success"]}]✓[{THEME["info"]}] Configuración actualizada:[/{THEME["info"]}]'
        f'[{THEME["secondary"]}]"{key}"[/{THEME["secondary"]}] = '
        f'[{THEME["warning"]}]"{value}"[/{THEME["warning"]}]\n'
    )
