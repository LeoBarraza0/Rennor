FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para paquetes científicos y lectura de excel
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   gcc \
	   g++ \
	   libpq-dev \
	   curl \
	   ca-certificates \
	   libatlas-base-dev \
	   libjpeg-dev \
	   zlib1g-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copiar requerimientos y código
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Puerto expuesto (por si en un futuro se añade una API)
EXPOSE 8000

# Comando por defecto (el script es interactivo; en desarrollo montaremos volumenes)
CMD ["python", "rnn_humedad.py"]
