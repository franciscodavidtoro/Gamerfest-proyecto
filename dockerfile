# Imagen base con Python 3.12
FROM python:3.12-slim

# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Fuerza que los mensajes de Python se muestren directamente (sin buffer)
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para wheel, psycopg2, etc.
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto
COPY . /app/

# Instala las dependencias de Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

#Vamos a la carpeta del proyecto
WORKDIR /app/GestorTutorias

# migra la la base de datos
RUN python manage.py makemigrations \
    && python manage.py makemigrations Sistema \
    && python manage.py migrate


# Expone el puerto del servidor de desarrollo de Django
EXPOSE 8000

# Comando para aplicar migraciones y levantar el servidor
CMD ["sh", "-c", " python manage.py runserver 0.0.0.0:8000"]
