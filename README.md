# 🛡️ Penlab

**Penlab** es una herramienta de línea de comandos desarrollada en **Python** para gestionar y documentar proyectos de **pentesting** de forma organizada, rápida y personalizable.

Automatiza la creación de estructuras de directorios, archivos, notas y configuraciones específicas para cada tipo de proyecto, utilizando **templates YAML** completamente adaptables.

---

## 🚀 Características principales

- ⚙️ **Automatización completa** de la estructura inicial de un proyecto de pentesting.
- 🧩 **Templates YAML personalizables**, que definen directorios, archivos, contenido predefinido y variables dinámicas.
- 🗂️ **Gestión visual y ordenada** en consola mediante la librería [`Rich`](https://github.com/Textualize/rich).
- 🧠 **Enfoque en la documentación**: fomenta mantener registros claros y estructurados de cada evaluación.
- 🔄 **Configuración persistente**, que guarda tus preferencias y rutas de trabajo.
- 🐍 **CLI simple y modular**, desarrollada con [`Click`](https://click.palletsprojects.com/).

---

## 🔽 Instalación

> Requisitos previos:
> - Python 3.9 o superior  
> - pip instalado  
> - Git (opcional, si clonas el repositorio)


### Opción 1 — Instalar desde PyPI (recomendada)

```bash
pip install penlab
```

### Opción 2 — Instalar localmente

```bash
git clone https://github.com/h3lls1nk1/penlab.git
cd penlab
pip install -r requirements.txt
pip install .
```

## 📁 Carpeta de Templates

Nada más instalar la aplicación se crearán varios archivos de configuración en la raíz de tu usuario.
Esto incluye la carpeta **`templates/`**.

Las rutas por defecto suelen ser algo así:

```bash
# Windows
C:\Users\usuario\.penlab\templates

# Linux
/home/usuario/.penlab/templates

# macOS
/Users/usuario/.penlab/templates
```

Puedes añadir tus plantillas YAML a esta carpeta de dos formas:
- Manualmente, mediante comandos o *drag & drop*.
- Con el siguiente comando:
```bash
  penlab templates import ruta/a/tu-plantilla.yaml
```

## 🧩 Cómo funcionan las Templates en Penlab

Las **templates** son el corazón de Penlab.  
Definen **cómo se crea la estructura de un proyecto de pentesting**: carpetas, archivos, contenido y variables dinámicas.

Cada template está escrita en **YAML**, lo que la hace fácil de leer, editar y compartir.  
Cuando ejecutas un comando como:

```bash
penlab init htb-Blue --template htb --target 10.10.10.40
```

Penlab busca el archivo htb.yaml (dentro de tu carpeta de plantillas), lo interpreta, sustituye las variables ({{target}}, {{project_name}}, etc.) y genera automáticamente todo el árbol de directorios con sus archivos.

## 📄 Estructura básica de una template

Una template YAML se divide en metadatos y una estructura (structure) que define carpetas y archivos.

```bash
# htb.yaml
name: htb
version: 1.0
author: Penlab
description: >
  Template optimizada para maquinas de tipo Hack The Box (HTB).
tags:
  - htb
  - ctf
  - pentest
  - web
  - network

# Variables que pueden usarse en nombres y contenidos ({project-name}, {target}, etc.)
variables:
  project-name: "Nombre del proyecto (usado en archivos y rutas)"
  target: "IP o hostname del objetivo (ej: 10.10.10.10)"
  your-ip: "Tu IP atacante / VPN (ej: 10.10.14.2)"
  date: "Fecha de creación (se sustituye automáticamente)"
  author: "Autor del proyecto"

# Estructura del proyecto (dirs, subdirs y archivos)
structure:
  - dir: reconnaissance
    files:
      - name: README.md
        content: |
          # Recon - {project-name}
          **Target:** {target}
          **Fecha:** {date}
          **Autor:** {author}

          ## Notas de recon
          - Puertos abiertos:
          - Servicios detectados:
          - Observaciones iniciales:
      - name: notes.md
        content: |
          # Notes - {project-name}
          - Objetivo: {target}
          - Estado inicial: pendiente
    subdirs:
      - dir: scans
        files:
          - name: "{target}_nmap_initial.txt"
            content: |
              # Nmap inicial - {target}
              # Ejecutado: {date}
              # Escaneo por defecto (tcp)
          - name: "{target}_nmap_full.xml"
            content: ""
      - dir: enum
        files:
          - name: web_enum.md
            content: |
              # Web enumeration
              - fuzzer:
              - endpoints:
  - dir: exploitation
    files:
      - name: payloads
        content: ""
      - name: notes_exploit.md
        content: |
          # Exploit notes - {project-name}
          - Vector:
          - POC:
    subdirs:
      - dir: scripts
        files:
          - name: scan_http.sh
            content: |
              #!/usr/bin/env bash
              # Scan básico HTTP para {target}
              echo "Escaneando {target}..."
              nmap -sV -p- --min-rate 1000 {target} -oA scans/{target}_http
            executable: true
  - dir: post-exploitation
    files:
      - name: priv-esc.md
        content: |
          # Privilege Escalation - {project-name}
          - Técnicas probadas:
          - Resultado:
      - name: persistence.md
        content: |
          # Persistence notes
  - dir: reports
    files:
      - name: README.md
        content: |
          # Reportes - {project-name}
          Genera aquí resúmenes y entregables.
      - name: draft_report.md
        content: |
          # Borrador de informe - {project-name}
          ## Resumen ejecutivo
          ## Hallazgos
  - dir: tools
    files:
      - name: README.md
        content: |
          # Tools
          Guarda scripts y herramientas útiles aquí.
  - dir: misc
    files:
      - name: journal.md
        content: |
          # Diario de pentesting - {project-name}
          Fecha | Acción | Resultado

# Archivos globales que se copian al root del proyecto
global_files:
  - name: README.md
    content: |
      # {project-name}
      Proyecto HTB generado con Penlab.
      - Target: {target}
      - Autor: {author}
      - Fecha: {date}

  - name: .gitignore
    content: |
      # Node / Python / general
      __pycache__/
      *.pyc
      *.log
      scans/
      *.xml
      *.nmap
      .env

  - name: LICENSE
    content: |
      MIT License
      Copyright (c) {author}

  - name: notes.md
    content: |
      # Central notes
      Usa este archivo para apuntes rápidos.

# Fin del template

```