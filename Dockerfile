# Imagen base de Python
FROM python:3.12-slim

# Carpeta de trabajo
WORKDIR /app

# Copia y instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto
COPY . .

# Puerto que usará Cloud Run
ENV PORT 8080

# Comando para ejecutar la app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
