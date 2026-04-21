FROM python:3.11-slim

WORKDIR /app

# Install build dependencies and TA-Lib C library
RUN apt-get update && apt-get install -y \
   build-essential \
   libpq-dev \
   wget \
   tar \
   && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
   && tar -xzf ta-lib-0.4.0-src.tar.gz \
   && cd ta-lib/ \
   && ./configure --prefix=/usr \
   && make \
   && make install \
   && cd .. \
   && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
   && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure app is in the python path
ENV PYTHONPATH=/app

# Use uvicorn directly for better Docker signal handling and logging
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
