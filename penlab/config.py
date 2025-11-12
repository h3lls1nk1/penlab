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
HTB_TEMPLATE_FILE = TEMPLATES_DIR / "htb.yaml"


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

    # --- Plantilla 'default' ---
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
            
    # --- Plantilla 'htb' ---
    if not HTB_TEMPLATE_FILE.exists():
        htb_template = {
            "name": "htb",
            "version": "1.0",
            "author": "Penlab",
            "description": "Template optimizada para maquinas de tipo Hack The Box (HTB).",
            "tags": ["htb", "ctf", "pentest", "web", "network"],
            "variables": {
                "project-name": "Nombre del proyecto (usado en archivos y rutas)",
                "target": "IP o hostname del objetivo (ej: 10.10.10.10)",
                "your-ip": "Tu IP atacante / VPN (ej: 10.10.14.2)",
                "date": "Fecha de creación (se sustituye automáticamente)",
                "author": "Autor del proyecto"
            },
            "structure": [
                {
                    "dir": "reconnaissance",
                    "files": [
                        {
                            "name": "README.md",
                            "content": "# Recon - {project-name}\n**Target:** {target}\n**Fecha:** {date}\n**Autor:** {author}\n\n## Notas de recon\n- Puertos abiertos:\n- Servicios detectados:\n- Observaciones iniciales:"
                        },
                        {
                            "name": "notes.md",
                            "content": "# Notes - {project-name}\n- Objetivo: {target}\n- Estado inicial: pendiente"
                        }
                    ],
                    "subdirs": [
                        {
                            "dir": "scans",
                            "files": [
                                {
                                    "name": "{target}_nmap_initial.txt",
                                    "content": "# Nmap inicial - {target}\n# Ejecutado: {date}\n# Escaneo por defecto (tcp)"
                                },
                                {
                                    "name": "{target}_nmap_full.xml",
                                    "content": ""
                                }
                            ]
                        },
                        {
                            "dir": "enum",
                            "files": [
                                {
                                    "name": "web_enum.md",
                                    "content": "# Web enumeration\n- fuzzer:\n- endpoints:"
                                }
                            ]
                        }
                    ]
                },
                {
                    "dir": "exploitation",
                    "files": [
                        {
                            "name": "payloads",
                            "content": ""
                        },
                        {
                            "name": "notes_exploit.md",
                            "content": "# Exploit notes - {project-name}\n- Vector:\n- POC:"
                        }
                    ],
                    "subdirs": [
                        {
                            "dir": "scripts",
                            "files": [
                                {
                                    "name": "scan_http.sh",
                                    "content": "#!/usr/bin/env bash\n# Scan básico HTTP para {target}\n"
                                               "echo \"Escaneando {target}...\"\n"
                                               "nmap -sV -p- --min-rate 1000 {target} -oA scans/{target}_http",
                                    "executable": True
                                }
                            ]
                        }
                    ]
                },
                {
                    "dir": "post-exploitation",
                    "files": [
                        {
                            "name": "priv-esc.md",
                            "content": "# Privilege Escalation - {project-name}\n- Técnicas probadas:\n- Resultado:"
                        },
                        {
                            "name": "persistence.md",
                            "content": "# Persistence notes"
                        }
                    ]
                },
                {
                    "dir": "reports",
                    "files": [
                        {
                            "name": "README.md",
                            "content": "# Reportes - {project-name}\nGenera aquí resúmenes y entregables."
                        },
                        {
                            "name": "draft_report.md",
                            "content": "# Borrador de informe - {project-name}\n## Resumen ejecutivo\n## Hallazgos"
                        }
                    ]
                },
                {
                    "dir": "tools",
                    "files": [
                        {
                            "name": "README.md",
                            "content": "# Tools\nGuarda scripts y herramientas útiles aquí."
                        }
                    ]
                },
                {
                    "dir": "misc",
                    "files": [
                        {
                            "name": "journal.md",
                            "content": "# Diario de pentesting - {project-name}\nFecha | Acción | Resultado\n"
                        }
                    ]
                }
            ],
            "global_files": [
                {
                    "name": "README.md",
                    "content": "# {project-name}\nProyecto HTB generado con Penlab.\n- Target: {target}\n- Autor: {author}\n- Fecha: {date}\n"
                },
                {
                    "name": ".gitignore",
                    "content": "# Node / Python / general\n__pycache__/\n*.pyc\n*.log\nscans/\n*.xml\n*.nmap\n.env\n"
                },
                {
                    "name": "LICENSE",
                    "content": "MIT License\nCopyright (c) {author}\n"
                },
                {
                    "name": "notes.md",
                    "content": "# Central notes\nUsa este archivo para apuntes rápidos.\n"
                }
            ]
        }
        
        with open(HTB_TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            yaml.safe_dump(htb_template, f, sort_keys=False, allow_unicode=True)


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