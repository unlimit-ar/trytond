#!/usr/bin/env bash
# helper: update or append module:hash in HASH_FILE
update_hash_record() {
local module="$1"
local hash="$2"
# remove old line if exists
if grep -q "^${module}:" "$HASH_FILE" 2>/dev/null; then
grep -v "^${module}:" "$HASH_FILE" > "${HASH_FILE}.tmp" && mv "${HASH_FILE}.tmp" "$HASH_FILE"
fi
echo "${module}:${hash}" >> "$HASH_FILE"
}


# Install or update modules based on modulos.txt lists
install_or_update_modules() {
echo "🔎 Comprobando módulos en: ${MODULE_DIRS[*]}"


for folder in "${MODULE_DIRS[@]}"; do
listfile="$folder/modulos.txt"
if [ ! -f "$listfile" ]; then
echo "⚠️ No existe $listfile — saltando $folder"
continue
fi


while IFS= read -r module || [ -n "$module" ]; do
# trim whitespace
module=$(echo "$module" | sed 's/^\s*//;s/\s*$//')
[ -z "$module" ] && continue


module_path="$folder/$module"
if [ ! -d "$module_path" ]; then
echo "⚠️ Módulo '$module' no encontrado en $folder — saltando"
continue
fi


echo "---\nProcesando módulo: $module"
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
echo "⏳ Ejecutando trytond-admin -u $module"
# trytond-admin must be available in PATH (imagen base). We pass DB connection via env or conf.
# Use trytond-admin with connection from /etc/trytond.conf or envs. If your conf relies on envs, fine.
trytond-admin -c /etc/trytond.conf -d "$DB_NAME" -u "$module" || true
# update hash file
if [ -n "$current_hash" ]; then
update_hash_record "$module" "$current_hash"
fi
fi


done < "$listfile"
done
}


# Only run module-check once per container start; if you want to skip when not needed
# you can gate this behind an env var, e.g. SKIP_MODULES=1
if [ "${SKIP_MODULES:-0}" != "1" ]; then
echo "🔧 Ejecutando comprobación/actualización de módulos..."
install_or_update_modules
else
echo "⚪ SKIP_MODULES=1 -> Saltando comprobación de módulos"
fi


# Finally exec the incoming command (trytond, trytond --cron, --worker, etc.)
exec "$@"