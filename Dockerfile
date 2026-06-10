FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# WeasyPrintのシステム依存関係をインストール
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY dualspendcalculator/ /app/dualspendcalculator/

WORKDIR /app/dualspendcalculator
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
