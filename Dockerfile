# Autor AS

# Basis-Image
FROM jupyter/pyspark-notebook

# Setze das Arbeitsverzeichnis im Container
WORKDIR /home/jovyan/work

# Kopiere alle Dateien im aktuellen Verzeichnis zum Arbeitsverzeichnis im Container
COPY . .

# Führe pip install durch, falls du eine requirements.txt hast
RUN pip install --no-cache-dir -r requirements.txt
