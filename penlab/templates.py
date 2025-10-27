"""
Gestión de templates de Penlab.
"""
import yaml
from pathlib import Path
from rich.console import Console

from config import TEMPLATES_DIR

console = Console()

def validate_template (template_data):
    """
    Valida de forma mínima la estructura de una template cargada desde YAML.
    Devuelve (True, []) si es válida, o (False, [mensajes]) con los errores detectados.
    Reglas comprobadas (no exhaustivas):
      - template_data debe ser un dict
      - name (opcional), version (opcional), description (opcional), tags (lista/str/num opcional)
      - variables, si existe, debe ser dict
      - structure debe ser lista; cada item debe ser dict con 'dir' (str)
      - dentro de cada dir: 'subdirs' (lista) y 'files' (lista) si existen
      - cada file debe ser dict con 'name' (str), 'content' (str opcional), 'executable' (bool opcional)
      - global_files debe ser lista de file dicts (mismas comprobaciones que arriba)
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

def load_template (template_name):
    """ Carga un template desde el directorio de templates a partir de su nombre.
        Valida la estructura mínima antes de devolverla.
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