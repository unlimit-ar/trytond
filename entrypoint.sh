#!/usr/bin/env bash
set -euo pipefail

ROOT="${TRYTON_ROOT:-/opt/trytond}"
MODULE_DIRS=("$ROOT/modules" "$ROOT/modules_ar")
HASH_FILE=/var/lib/tryton/.modules_hashes
FLAG_DIR=/var/lib/tryton
DB_NAME="${TRYTON_DATABASE}"
DB_HOST="${DB_HOST}"
# Prefijos opcionales separados por coma, por ejemplo: "padulles_,custom_"
MODULE_PREFIXES="${MODULE_PREFIXES:-}"

mkdir -p "$FLAG_DIR"
touch "$HASH_FILE"

get_module_hash() {
  local module_path="$1"
  if [ ! -d "$module_path" ]; then
    echo ""
    return
  fi
  find "$module_path" -type f \( -name "*.py" -o -name "*.xml" -o -name "*.po" \) -print0 \
    | xargs -0 md5sum 2>/dev/null || true \
    | sort -k2 \
    | md5sum \
    | awk '{print $1}'
}

update_hash_record() {
  local module="$1"
  local hash="$2"
  if grep -q "^${module}:" "$HASH_FILE" 2>/dev/null; then
    grep -v "^${module}:" "$HASH_FILE" > "${HASH_FILE}.tmp" && mv "${HASH_FILE}.tmp" "$HASH_FILE"
  fi
  echo "${module}:${hash}" >> "$HASH_FILE"
}

# 🔧 Quita el prefijo si coincide con alguno de los definidos
strip_prefix_if_needed() {
  local mod="$1"
  local clean="$mod"
  IFS=',' read -ra PREFIXES <<< "$MODULE_PREFIXES"
  for prefix in "${PREFIXES[@]}"; do
    prefix_trimmed=$(echo "$prefix" | xargs)
    if [[ -n "$prefix_trimmed" && "$mod" == "$prefix_trimmed"* ]]; then
      clean="${mod#$prefix_trimmed}"
      break
    fi
  done
  echo "$clean"
}

install_pytohn_packages() {
  echo "🔧 Ejecutando pip install ..."
  if [ -d "$module_path" ] && [ -f "$module_path/setup.py" -o -f "$module_path/pyproject.toml" ]; then
    echo "📦 Instalando paquete Python para $(basename "$module_path")"
    pip install "$module_path"  >/dev/null 2>&1 || echo "⚠️ Falló instalación de $(basename "$module_path")"
  fi
}

install_or_update_modules() {
  echo "🔎 Comprobando módulos en: ${MODULE_DIRS[*]}"
  for folder in "${MODULE_DIRS[@]}"; do
    listfile="$folder/modules.txt"
    if [ ! -f "$listfile" ]; then
      echo "⚠️ No existe $listfile — saltando $folder"
      continue
    fi

    while IFS= read -r module || [ -n "$module" ]; do
      module=$(echo "$module" | sed 's/^\s*//;s/\s*$//')
      [ -z "$module" ] && continue

      module_path="$folder/$module"
      echo "$module_path"
      if [ ! -d "$module_path" ]; then
        echo "⚠️ Módulo '$module' no encontrado en $folder — saltando"
        continue
      fi

      echo "Procesando módulo: $module"
      current_hash=$(get_module_hash "$module_path")
      previous_hash=$(grep "^${module}:" "$HASH_FILE" 2>/dev/null | cut -d":" -f2 || true)

      if [ -z "$current_hash" ]; then
        echo "⚠️ No se pudo calcular hash para $module — forzando actualización"
        needs_update=1
      elif [ "$current_hash" != "$previous_hash" ]; then
        echo "🔄 Cambio detectado para $module"
        needs_update=1
      else
        echo "✅ Sin cambios en $module"
        needs_update=0
      fi

      if [ "$needs_update" -eq 1 ]; then
        echo "⏳ Instalando con pip el $module_path ..."
        install_pytohn_packages "$module_path"
        # Determinar nombre real para Tryton (sin prefijo)
        real_module=$(strip_prefix_if_needed "$module")
        echo "⏳ Ejecutando trytond-admin -u $real_module -d $DB_NAME"
        trytond-admin -d "$DB_NAME" -u "$real_module" || true
        if [ -n "$current_hash" ]; then
          update_hash_record "$module" "$current_hash"
        fi
      fi

    done < "$listfile"
  done
}

if [ "${SKIP_MODULES:-0}" != "1" ]; then
  echo "🔧 Ejecutando comprobación/actualización de módulos..."
  install_or_update_modules
else
  echo "⚪ SKIP_MODULES=1 -> Saltando comprobación de módulos"
fi

exec "$@"
