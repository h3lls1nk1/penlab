"""
config.py
=====================

Agrupa funciones y constantes de configuración de la herramienta Penlab.

"""
import os
import yaml
from pathlib import Path

# Configuración de paths.
PENLAB_HOME = Path.home() / '.penlab'
TEMPLATES_DIR = PENLAB_HOME / 'templates'
CONFIG_FILE = PENLAB_HOME / 'config.yaml'
DEFAULT_TEMPLATE_FILE = TEMPLATES_DIR / "default.yaml"

# Configuración por defecto de los proyectos. 
DEFAULT_CONFIG = {
    'your_ip': '10.10.14.x',
    'author': os.getenv('USER', 'pentester'),
    'default_template': 'default'
}

def ensure_penlab_structure ():
    """
    Asegura que los directorios básicos y el archivo de configuración global
    de Penlab esten creados. Si no lo están, los crea.
    """
    PENLAB_HOME.mkdir(exist_ok=True)
    TEMPLATES_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)

    if not DEFAULT_TEMPLATE_FILE.exists(): 
        default_template = {
            "name": "default",
            "version": "1.0",
            "author": "Penlab",
            "description": "Plantilla por defecto para Penlab",
            "tags": ["default", "pentest"],
            "variables": {
                "target": "IP del objetivo",
                "your-ip": "Tu IP de atacante"
            },
            "structure": [
                {
                    "dir": "recon",
                    "files": [
                        {
                            "name": "notes.md",
                            "content": "# Reconnaissance - {target}\nDate: {date}\n"
                        }
                    ]
                }
            ],
            "global_files": [
                {
                    "name": "README.md",
                    "content": "# {project-name}\nTarget: {target}\n"
                }
            ]
        }   

        with open(DEFAULT_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            yaml.safe_dump(default_template, f, sort_keys=False, allow_unicode=True)
        

def load_config ():
    """ 
    Se asegura de que toda la estructura básica de directorios y archivos esté
    creada y luego carga la configuración del archivo definido en `CONFIG_FILE`.
    En caso de que algo falle, devuelve la configuración por defecto. 
    """
    ensure_penlab_structure()

    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f) or DEFAULT_CONFIG
    except:
        return DEFAULT_CONFIG
    
def save_config (config):
    """
    Guarda la configuración pasada como argumento en el archivo de configuración
    global de Penlab.

    Args:
        config (str): Configuración a guardar globalmente.
    """
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f)