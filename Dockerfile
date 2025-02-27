# Usa una imagen base de Python
FROM python:3.12


# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y nano && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Configura el entrypoint del contenedor
ENTRYPOINT ["/entrypoint.sh"]