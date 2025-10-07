""" Archivo del proyecto para configurar la instalación del paquete """

from  setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='penlab',
    version='1.0.0',
    author='h3lls1nk1',
    author_email='h3lls1nk1@gmail.com',
    description='CLI tool para gestión de proyectos de pentesting y ciberseguridad',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/h3lls1nk1/penlab',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'rich>=13.0.0',
        'PyYAML>=6.0',
        'jinja2>=3.0.0',
    ],
    entry_points={
        'console_scripts': [
            'penlab=penlab.cli:cli',
        ],
    },
    include_package_data=True,
    package_data={
        'penlab': ['templates/*.yaml'],
    },
)