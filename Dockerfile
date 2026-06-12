FROM python:3.12-slim

# System dependencies required by WeasyPrint (Pango, Cairo, GDK-Pixbuf, fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Runtime data directories (also created by config.py, but ensure they exist)
RUN mkdir -p uploads/images output

EXPOSE 8000

# No --reload in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
