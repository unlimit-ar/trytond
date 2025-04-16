#!/bin/bash

MODULES_DIR="/tmp/modules_ar"
MODULES_LIST="$MODULES_DIR/modules.txt"

# Verifica si el directorio de módulos existe
if [ -d "$MODULES_DIR" ]; then
    echo "Buscando módulos en $MODULES_DIR para instalar con pip..."

    # Verifica si el archivo modules.txt existe
    if [ -f "$MODULES_LIST" ]; then
        while IFS= read -r module || [ -n "$module" ]; do
            dir="$MODULES_DIR/$module"
            
            # Verifica si el directorio existe y contiene setup.py o pyproject.toml
            if [ -d "$dir" ]; then
                if [ -f "$dir/setup.py" ] || [ -f "$dir/pyproject.toml" ]; then
                    echo "Instalando módulo desde $dir..."
                    pip install "$dir" || echo "Error al instalar el módulo en $dir"
                else
                    echo "Saltando $dir: no contiene setup.py o pyproject.toml."
                fi
            else
                echo "El directorio $dir no existe. Saltando."
            fi
        done < "$MODULES_LIST"
    else
        echo "El archivo $MODULES_LIST no existe. No se instalarán módulos."
    fi

    echo "Instalación de módulos completada."
else
    echo "El directorio $MODULES_DIR no existe. Saltando instalación."
fi

# Ejecuta el comando original del contenedor
exec "$@"
