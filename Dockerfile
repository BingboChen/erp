# erp/Dockerfile

# Utilizza un'immagine base Python pulita e stabile.
# `python:3.13-slim-buster` è una buona scelta per le app web.
FROM python:3.13-slim-buster

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Installa le dipendenze di sistema necessarie
# (libpq-dev per psycopg2, build-essential/python3-dev per compilazioni, zlib1g-dev per libz.so.1)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    python3-dev \
    zlib1g-dev \
    # Pulisci la cache apt per ridurre la dimensione dell'immagine Docker
    && rm -rf /var/lib/apt/lists/*

# Copia il requirements.txt e installa le dipendenze Python
# Facendo questo in un passo separato, Docker può fare caching di questo layer
# se il requirements.txt non cambia, velocizzando i build futuri.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice della tua applicazione
COPY . /app/

# Espone la porta su cui l'applicazione ascolterà
# Railway inietta la porta dinamica in $PORT
EXPOSE $PORT

# Definisce il comando che verrà eseguito all'avvio del container
# Questo sostituisce il tuo Procfile
CMD ["gunicorn", "maxfactory.wsgi:application", "--log-file", "-"]