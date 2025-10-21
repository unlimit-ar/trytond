# Usa una imagen base de Python
FROM python:3.12

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .

RUN apt-get update && apt-get install -y nano swig && apt-get clean

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./modules /tmp/modules
COPY ./modules_ar /tmp/modules_ar
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]