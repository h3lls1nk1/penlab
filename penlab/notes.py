"""
Sistema de gestión de notas para Penlab - NO FUNCIONAL
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import click

console = Console()

@dataclass
class Note:
    """ Representa una nota """
    id: int
    content: str
    timestamp: str
    tags: List[str]
    author: str

    def to_dict (self):
        return asdict(self)
    
class ProjectNotFound (Exception):
    """ Excepción cuando no se encuentra un proyecto Penlab """
    pass

def find_project_root (start_path: Path = None) -> Optional[Path]:
    """ Busca el directorio raíz del proyecto Penlab. Lo hace subiendo
        recursivamente sobre los directorios hasta encontrar .penlab.yaml
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.absolute()

    while current != current.parent:
        penlab_file = current / '.penlab.yaml'

        if penlab_file.exists():
            return current
        
        current = current.parent

    return None

def get_project_info (project_root: Path) -> Dict:
    """ Lee la información del proyecto en el archivo .penlab.yaml """
    import yaml

    penlab_file = project_root / '.penlab.yaml'

    if not penlab_file.exists():
        return {
            'name': project_root.name,
            'target': 'unknown',
            'created': datetime.now().isoformat()
        }
    
    try:
        with open(penlab_file, 'r') as f:
            return yaml.safe_load(f)
    except:
        return {
            'name': project_root.name
        }
    
def get_notes_file (project_root: Path) -> Path:
    """ Obtiene la ruta del archivo de notas del proyecto. """
    penlab_dir = project_root / '.penlab'
    penlab_dir.mkdir(exist_ok=True)

    return penlab_dir / 'notes.json'

def load_notes (notes_file: Path) -> List[Note]:
    """ Carga las notas desde el archivo JSON """
    if not notes_file.exists():
        return []
    
    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            return [Note(**note) for note in data]
    except Exception as e:
        console.print(f'[red]Error al cargar notas: [/red] {e}')
        
        return []
    
def save_notes (notes_file: Path, notes: List[Note]):
    """ Guarda las notas en el archivo JSON """
    try:
        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump([note.to_dict() for note in notes], f, indent=4, ensure_ascii=False)
    except Exception as e:
        console.print(f'[red]Error al guardar notas: [/red] {e}')

def add_note (project_root: Path, content: str, tags: List[str], author: str):
    notes_file = get_notes_file(project_root)
    notes = load_notes(notes_file)
    new_id = max([note.id for note in notes], default=0) + 1
    note = Note(id=new_id, content=content, tags=tags, author=author, timestamp=datetime.now().isoformat)
    notes.append(note)
    save_notes(notes_file, notes)

    console.print(f'[green]Nota {new_id} añadida correctamente. [/green]')

def list_notes (project_root: Path):
    notes_file = get_notes_file(project_root)
    notes = load_notes(notes_file)

    if not notes:
        console.print('[yellow]No hay notas aún para este proyecto.[/yellow]')
        return
    
    table = Table(title="Notas del proyecto", box=box.SIMPLE_HEAVY)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Fecha", style="green", width=20)
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Contenido", style="white", max_width=60, overflow="fold")
    for note in notes:
        table.add_row(str(note.id), note.timestamp.split("T")[0], ", ".join(note.tags), note.content[:120])
    console.print(table)

def view_note (project_root: Path, note_id: int):
    notes_file = get_notes_file(project_root)
    notes = load_notes(notes_file)
    for note in notes:
        if note.id == note_id:
            panel = Panel.fit(
                f"[bold cyan]Autor:[/bold cyan] {note.author}\n"
                f"[bold cyan]Fecha:[/bold cyan] {note.timestamp}\n"
                f"[bold cyan]Tags:[/bold cyan] {', '.join(note.tags)}\n\n"
                f"[white]{note.content}[/white]",
                title=f"Nota #{note.id}",
                border_style="magenta"
            )
            console.print(panel)
            return
    console.print(f"[red]✗[/red] No se encontró la nota con ID {note_id}.")

def delete_note(project_root: Path, note_id: int):
    notes_file = get_notes_file(project_root)
    notes = load_notes(notes_file)
    new_notes = [n for n in notes if n.id != note_id]
    if len(new_notes) == len(notes):
        console.print(f"[red]✗[/red] No se encontró la nota con ID {note_id}.")
        return
    save_notes(notes_file, new_notes)
    console.print(f"[green]✓[/green] Nota #{note_id} eliminada correctamente.")

def search_notes(project_root: Path, keyword: str):
    notes_file = get_notes_file(project_root)
    notes = load_notes(notes_file)
    results = [n for n in notes if keyword.lower() in n.content.lower() or any(keyword.lower() in t.lower() for t in n.tags)]
    if not results:
        console.print(f"[yellow]No se encontraron notas que contengan '{keyword}'.[/yellow]")
        return
    table = Table(title=f"Resultados para '{keyword}'", box=box.SIMPLE)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Fecha", style="green", width=20)
    table.add_column("Tags", style="yellow", width=20)
    table.add_column("Contenido", style="white", max_width=60, overflow="fold")
    for note in results:
        table.add_row(str(note.id), note.timestamp.split("T")[0], ", ".join(note.tags), note.content[:120])
    console.print(table)

@click.group()
def notes():
    """Gestión de notas del proyecto actual"""
    pass

@notes.command("add")
@click.argument("content")
@click.option("--tags", "-t", multiple=True, help="Etiquetas asociadas a la nota")
@click.option("--author", "-a", default=os.getenv("USER", "pentester"), help="Autor de la nota")
def cli_add(content, tags, author):
    project_root = find_project_root()
    if not project_root:
        raise ProjectNotFound("No se encontró un proyecto Penlab en este directorio o sus padres.")
    add_note(project_root, content, list(tags), author)

@notes.command("list")
def cli_list():
    project_root = find_project_root()
    if not project_root:
        raise ProjectNotFound("No se encontró un proyecto Penlab en este directorio o sus padres.")
    list_notes(project_root)

@notes.command("view")
@click.argument("note_id", type=int)
def cli_view(note_id):
    project_root = find_project_root()
    if not project_root:
        raise ProjectNotFound("No se encontró un proyecto Penlab en este directorio o sus padres.")
    view_note(project_root, note_id)

@notes.command("delete")
@click.argument("note_id", type=int)
def cli_delete(note_id):
    project_root = find_project_root()
    if not project_root:
        raise ProjectNotFound("No se encontró un proyecto Penlab en este directorio o sus padres.")
    delete_note(project_root, note_id)

@notes.command("search")
@click.argument("keyword")
def cli_search(keyword):
    project_root = find_project_root()
    if not project_root:
        raise ProjectNotFound("No se encontró un proyecto Penlab en este directorio o sus padres.")
    search_notes(project_root, keyword)
    

