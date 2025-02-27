#!/bin/bash

# Recorre cada carpeta en /temp/modules
if [ -d /tmp/modules ]; then
    echo "Buscando módulos en /tmp/modules para instalar con pip..."

    for dir in /tmp/modules/*/; do
        # Verifica si el directorio contiene un setup.py o equivalente
        if [ -f "$dir/setup.py" ] || [ -f "$dir/pyproject.toml" ]; then
            echo "Instalando módulo desde $dir..."
            pip install "$dir" || echo "Error al instalar el módulo en $dir"
        else
            echo "Saltando $dir: no contiene setup.py o pyproject.toml."
        fi
    done

    echo "Instalación de módulos completada."
else
    echo "El directorio /tmp/modules no existe. Saltando instalación."
fi

# Ejecuta el comando original del contenedor
exec "$@"
