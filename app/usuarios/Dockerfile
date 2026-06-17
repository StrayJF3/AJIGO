# IMAGEN BASE OFICIAL DE PYTHON S-SLIM
FROM python:3.10-slim

# EVITA QUE PYTHON ESCRIBA ARCHIVOS PYC EN EL DISCO Y HABILITA UN BUFFER DE LOGS RAPIDO
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# INSTALA DEPENDENCIAS DEL SISTEMA Y AGREGA EL REPOSITORIO DE CONTROLADORES DE MICROSOFT
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    unixodbc \
    unixodbc-dev \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc \
    && rm -rf /var/lib/apt/lists/*

# CREA Y ESTABLECE EL DIRECTORIO DE TRABAJO
WORKDIR /app

# COPIA E INSTALA LOS REQUERIMIENTOS DEL ARCHIVO
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPIA EL RESTO DEL CODIGO AL CONTENEDOR
COPY . .

# EXPONE EL PUERTO CORRESPONDIENTE
EXPOSE 8000

# EJECUTA LA APLICACION UTILIZANDO UVICORN
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
