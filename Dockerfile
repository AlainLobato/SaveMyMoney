FROM python:3.12-slim

# Configuración inicial
WORKDIR /app
COPY . /app

# Instala las dependencias necesarias
RUN apt-get update && \
    apt-get install -y gcc g++ curl lsb-release sqlite3

# Instala las librerías de Python necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto y configura la app de Flask
EXPOSE 5000
ENV FLASK_APP=app.py

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]