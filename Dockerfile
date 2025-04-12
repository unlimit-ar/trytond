# Usa una imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .

RUN apt-get update && apt-get install -y nano swig && apt-get clean

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY instala_modules.sh .
RUN chmod +x instala_modules.sh

COPY instala_modules_ar.sh .
RUN chmod +x instala_modules_ar.sh

COPY ./modules /tmp/modules
COPY ./modules_ar /tmp/modules_ar

RUN ./instala_modules.sh
RUN ./instala_modules_ar.sh

COPY ./ejecutables/gunicorn.conf.py .
COPY ./ejecutables/trytond-app.py .

# CMD [ "trytond" ]
# CMD [ "gunicorn", "trytond-app", "-c", "gunicorn.conf.py" ]