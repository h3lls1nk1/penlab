"""
Funciones de interfaz de usuario para Penlab.
"""
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

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