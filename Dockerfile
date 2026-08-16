# 1. Bajamos a Python 3.12 (Estable y recomendada para Tryton 8.0)
FROM python:3.12-slim

# 2. Instalamos dependencias del sistema necesarias para compilar librerías de Tryton
RUN apt-get update && apt-get install -y \
    nano \
    swig \
    libpq-dev \
    gcc \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecemos directorios de trabajo
WORKDIR /opt/trytond

# 4. Creamos los directorios de datos y logs ANTES de instalar nada
# Esto evita el error de trytond-stat que vimos antes
RUN mkdir -p /opt/trytond/data && chmod -R 777 /opt/trytond/data

# 5. Instalamos requerimientos
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el entrypoint y los módulos locales
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
COPY ./modules_ar ./modules_ar

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
    