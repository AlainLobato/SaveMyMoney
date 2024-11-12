FROM python:3.12-slim

# Configuración inicial
WORKDIR /app
COPY . /app

# Instala las dependencias necesarias y el controlador ODBC
RUN apt-get update && \
    apt-get install -y unixodbc-dev gcc g++ curl lsb-release wget dpkg

RUN wget https://packages.microsoft.com/ubuntu/22.04/prod/pool/main/m/msodbcsql17/msodbcsql17_17.10.6.1-1_amd64.deb && \
    dpkg -i msodbcsql17_17.10.6.1-1_amd64.deb && \
    apt-get install -y -f && \
    apt-get clear

# Instala las librerías de Python necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto y configura la app de Flask
EXPOSE 5000
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0"]
