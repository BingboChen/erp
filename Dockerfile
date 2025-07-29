# erp/Dockerfile

# Utilizza l'immagine base Python 3.12 slim
FROM python:3.12-slim 

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Installa le dipendenze di sistema necessarie
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    python3-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia il requirements.txt e installa le dipendenze Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice della tua applicazione
COPY . /app/

# Espone la porta su cui l'applicazione ascolterà
EXPOSE $PORT

# Definisce il comando che verrà eseguito all'avvio del container
CMD ["gunicorn", "maxfactory.wsgi:application", "--log-file", "-"]