"""
ui.py
=====================

Funciones de interfaz visual y presentación de la CLI de Penlab.

Este módulo contiene funciones relacionadas con la **interfaz visual** en la terminal,
utilizando la librería `Rich` para mostrar banners, tablas y estructuras de directorios
de forma legible y atractiva.
"""

from rich.console import Console
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich import box

from ui_theme import THEME

console = Console()

# ============================================================
# FUNCIÓN: show_banner
# ============================================================
def show_banner ():
    """
    Muestra el banner principal de Penlab y la tabla de comandos disponibles.

    El banner está diseñado con arte ASCII en color rojo/cian y presenta:
    - El título y versión de Penlab.
    - Una tabla con los comandos más utilizados.
    - Un panel inferior con tips y enlace a la documentación.

    Se utiliza la librería `Rich` para colores, tablas y paneles.
    """
    banner = Text()
    banner.append("╔═══════════════════════════════════════════════════════════╗\n", style="cyan bold")
    banner.append("║                                                           ║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██████╗ ███████╗███╗   ██╗██╗      █████╗ ██████╗       ", style="red bold")
    banner.append("║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██╔══██╗██╔════╝████╗  ██║██║     ██╔══██╗██╔══██╗      ", style="red bold")
    banner.append("║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██████╔╝█████╗  ██╔██╗ ██║██║     ███████║██████╔╝      ", style="red bold")
    banner.append("║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██╔═══╝ ██╔══╝  ██║╚██╗██║██║     ██╔══██║██╔══██╗      ", style="red bold")
    banner.append("║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("██║     ███████╗██║ ╚████║███████╗██║  ██║██████╔╝      ", style="red bold")
    banner.append("║\n", style="cyan bold")
    banner.append("║   ", style="cyan bold")
    banner.append("╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═════╝       ", style="red bold")
    banner.append("║\n", style="cyan bold")
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

    # ===================== Tabla de comandos =====================
    table = Table(
        title=f'[{THEME["primary"]}]Comandos disponibles[/{THEME['primary']}]', 
        box=box.ROUNDED, 
        show_header=True, 
        header_style=f'bold {THEME["primary"]}'
    )
    
    table.add_column('Comando', style=THEME['secondary'], width=40)
    table.add_column('Descripción', style=THEME['info'])

    table.add_row(
        'penlab init <proyecto>',
        'Crea un nuevo proyecto de pentesting'
    )

    table.add_row(
        'penlab list-projects',
        'Lista de los proyectos Penlab del directorio actual'
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
        'penlab config show',
        'Muestra todas las entradas de configuración de Penlab'
    )

    table.add_row(
        'penlab config set <key> <value>',
        'Establece un nuevo valor para una entrada de configuración'
    )

    console.print(table)
    console.print()

    # ===================== Panel con tips =====================
    console.print(
        Panel.fit(
            f"[{THEME['warning']}]Tip:[/{THEME['warning']}] "
            f"Usa [{THEME['primary']}]penlab init mi-proyecto --template htb --target 10.10.10.50[/{THEME['primary']}] para comenzar\n"
            f"[{THEME['warning']}]Docs:[/{THEME['warning']}] https://github.com/hellsinki/penlab",
            title=f"[{THEME['primary']}]Getting Started[/{THEME['primary']}]",
            border_style=THEME['primary']
        )
    )

# ============================================================
# FUNCIÓN: build_tree
# ============================================================
def build_tree (tree, path, max_depth = 3, current_depth = 0):
    """
    Construye recursivamente un árbol visual con la estructura de directorios.

    Utiliza la clase `Tree` de Rich para representar carpetas (en azul)
    y archivos (con iconos 📄 o 📜). Limita la profundidad para evitar
    árboles muy extensos o lentos de renderizar.

    Args:
        tree (Tree): Nodo raíz o subárbol sobre el que se agregan elementos.
        path (Path): Directorio base a recorrer.
        max_depth (int, opcional): Profundidad máxima de recursión. Por defecto 3.
        current_depth (int, opcional): Nivel actual de profundidad interna.

    Notas:
        - Solo muestra los primeros 20 elementos por directorio.
        - Ignora errores de permisos (PermissionError).
    """
    if current_depth >= max_depth:
        return 
    
    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items[:20]:
            if item.is_dir():
                branch = tree.add(f"[{THEME['secondary']}]📁 {item.name}[/{THEME['secondary']}]")
                build_tree(branch, item, max_depth, current_depth + 1)
            else:
                icon = '📄' if item.suffix in ['.md', '.txt'] else '📜'
                tree.add(f"[{THEME['info']}]{icon} {item.name}[/{THEME['info']}]")
    except PermissionError:
        # Ignorar directorios sin permisos de lectura
        pass