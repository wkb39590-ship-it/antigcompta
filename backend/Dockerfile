



# FROM python:3.11-slim

# WORKDIR /app

# # Installer Tesseract + langues + poppler (pdf2image) + libs OpenCV headless
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     tesseract-ocr-fra \
#     tesseract-ocr-eng \
#     poppler-utils \
#     libgl1 \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt /app/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . /app

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]









# FROM python:3.11-slim

# WORKDIR /app

# # Installer Tesseract + langue française + poppler pour pdf2image
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     tesseract-ocr-fra \
#     poppler-utils \
#     && rm -rf /var/lib/apt/lists/*
    

# COPY requirements.txt /app/requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . /app

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]









FROM python:3.11-slim

WORKDIR /app

# Dépendances système :
# - poppler-utils : pdf2image (pdftoppm)
# - tesseract + lang fr : OCR
# - libgl1 + libglib2.0-0 : souvent nécessaires pour opencv / pillow
# - gcc + build-essential (optionnel) : utile si une lib compile (peut être retiré si inutile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Installer les deps Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le code
COPY . /app

# IMPORTANT:
# Ne mets PAS --reload en prod. En dev OK, mais ça peut masquer des crashs.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
