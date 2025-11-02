"""
templates.py
=====================

Funciones para la gestión de templates de Penlab.

Este módulo se encarga de cargar, validar y devolver las plantillas (`templates`)
usadas por Penlab para crear proyectos automáticamente.  
Cada template está escrita en formato **YAML** y define la estructura de carpetas,
archivos y variables necesarias para inicializar un nuevo proyecto.
"""
import yaml
from rich.console import Console

from penlab.config import TEMPLATES_DIR

console = Console()

# ============================================================
# FUNCIÓN: validate_template
# ============================================================
def validate_template (template_data):
    """
    Valida de forma mínima la estructura de una template cargada desde YAML.

    Esta función realiza comprobaciones básicas de tipo y formato sobre los
    campos principales de una plantilla para evitar errores al crear proyectos.
    Devuelve una tupla `(es_valida, lista_de_errores)`.

    Args:
        template_data (dict): Estructura YAML ya cargada en memoria.

    Returns:
        tuple:
            - (True, []) si es válida.
            - (False, [mensajes]) si hay errores detectados.

    Validaciones aplicadas:
        - El YAML raíz debe ser un `dict`.
        - `name`, `version`, `description`, `tags`: opcionales, pero con tipos válidos.
        - `variables` (opcional): debe ser `dict` si existe.
        - `structure`: debe ser una lista de objetos `dir` válidos.
        - Cada `dir` puede contener `subdirs` y `files`.
        - Cada `file` debe tener:
            - `name` obligatorio.
            - `content` opcional (string).
            - `executable` opcional (bool).
        - `global_files`: lista de archivos con la misma validación.
    """
    errors = []

    if not isinstance(template_data, dict):
        return False, ['La template debe ser un mapping/dict en el YAML (nivel superior).']
    
    # Top-level basics
    if 'name' in template_data and not isinstance(template_data['name'], (str, int, float)):
        errors.append('El campo "name" debe ser un texto (string).')

    if 'version' in template_data and not isinstance(template_data['version'], (str, int, float)):
        errors.append('El campo "version" debe ser un texto o un número.')

    if 'description' in template_data and not isinstance(template_data['description'], str):
        errors.append('El campo "description" debe ser un texto (string).')

    if 'tags' in template_data:
        tags = template_data['tags']

        if not isinstance(tags, (list, tuple, str, int, float)):
            errors.append('el campo "tags" debe ser una lista de strings o un string/number suelto.')
        elif isinstance(tags, (list, tuple)):
            for i, t in enumerate(tags):
                if not isinstance(t, (str, int, float)):
                    errors.append(f'Tag en posición {i} no es un texto/num válido.')
    
    if 'variables' in template_data and not isinstance(template_data['variables'], dict):
        errors.append('El campo "variables" debe ser un mapping/dict (clave: valor).')

    if 'structure' in template_data:
        structure = template_data['structure']

        if not isinstance(structure, (list, tuple)):
            errors.append('El campo "structure" debe ser una lista.')
        else:
            for idx, item in enumerate(structure):
                if not isinstance(item, dict):
                    errors.append(f'structure[{idx}] debe ser un mapping/dict.')
                    continue

                if 'dir' not in item:
                    errors.append(f'structure[{idx}] falta la clave "dir".')
                else:
                    if not isinstance(item['dir'], (str, int, float)):
                        errors.append(f'structure[{idx}].dir debe ser un texto.')
                
                if 'subdirs' in item and not isinstance(item['subdirs'], (list, tuple)):
                    errors.append(f'structure[{idx}].subdirs debe ser una lista.')

                if 'files' in item:
                    if not isinstance(item['files'], (list, tuple)):
                        errors.append(f'structure[{idx}].files debe ser una lista.')
                    else:
                        for j, f in enumerate(item['files']):
                            if not isinstance(f, dict):
                                errors.append(f'structure[{idx}].files[{j}] debe ser un mapping/dict.')
                                continue
                            if 'name' not in f:
                                errors.append(f'structure[{idx}].files[{j}] falta "name"')
                            else:
                                if not isinstance(f['name'], (str, int, float)):
                                    errors.append(f"structure[{idx}].files[{j}].name debe ser texto.")
                            if 'content' in f and not isinstance(f['content'], str):
                                errors.append(f"structure[{idx}].files[{j}].content debe ser texto.")
                            if 'executable' in f and not isinstance(f['executable'], bool):
                                errors.append(f"structure[{idx}].files[{j}].executable debe ser booleano (true/false).")

    if 'global_files' in template_data:
        gf = template_data['global_files']

        if not isinstance(gf, (list, tuple)):
            errors.append('El campo "global_files" debe ser una lista.')
        else:
            for i, f in enumerate(gf):
                if not isinstance(f, dict):
                    errors.append(f'global_files[{i}] debe ser una mapping/dict.')
                    continue
                if 'name' not in f:
                    errors.append(f'global_files[{i}] falta "name"')
                else:
                    if not isinstance(f['name'], (str, int, float)):
                        errors.append(f'global_files[{i}].name debe ser texto.')
                
                if 'content' in f and not isinstance(f['content'], str):
                    errors.append(f"global_files[{i}].content debe ser texto.")
                if 'executable' in f and not isinstance(f['executable'], bool):
                    errors.append(f"global_files[{i}].executable debe ser booleano (true/false).")

    if errors:
        return False, errors
    
    return True, []

# ============================================================
# FUNCIÓN: load_template
# ============================================================
def load_template (template_name):
    """
    Carga y valida una plantilla YAML desde el directorio de templates de Penlab.

    La función busca un archivo con extensión `.yaml` dentro del directorio
    configurado (`TEMPLATES_DIR`).  
    Si existe, se parsea y valida mediante `validate_template()` antes de
    devolverlo al llamante.

    Args:
        template_name (str): Nombre del template (sin extensión `.yaml`).

    Returns:
        dict | None: El contenido de la plantilla si es válida, o `None` en caso de error.

    Flujo de ejecución:
        1. Construye la ruta `TEMPLATES_DIR / "{template_name}.yaml"`.
        2. Intenta abrir y parsear el YAML.
        3. Llama a `validate_template()` para comprobar su validez.
        4. Si hay errores, los muestra en consola Rich.
    """
    template_path = TEMPLATES_DIR / f'{template_name}.yaml'

    if not template_path.exists():
        console.print(f'[red]✗[/red] Template "{template_name}" no encontrado')
        return None

    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}

        valid, errors = validate_template(data)
        if not valid:
            console.print(f'[red]✗[/red] La template "{template_name}" está mal formada. Errores:')
            for err in errors:
                console.print(f'  - {err}')
            return None

        return data

    except yaml.YAMLError as ye:
        console.print(f'[red]✗[/red] Error de parsing YAML en "{template_name}": {ye}')
        return None
    except Exception as e:
        console.print(f'[red]✗[/red] Error al cargar la template: {e}')
        return None