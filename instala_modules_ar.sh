#!/bin/bash

# Recorre cada carpeta en /tmp/modules_ar
if [ -d /tmp/modules_ar ]; then
    echo "Buscando módulos en /tmp/modules_ar para instalar con pip..."

    for dir in /tmp/modules_ar/*/; do
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
    echo "El directorio /tmp/modules_ar no existe. Saltando instalación."
fi

# Ejecuta el comando original del contenedor
exec "$@"
