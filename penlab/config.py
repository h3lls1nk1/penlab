"""
Gestión de configuración de Penlab.
"""
import os
import yaml
from pathlib import Path

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