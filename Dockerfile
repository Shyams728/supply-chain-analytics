FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# libgomp1 is needed for XGBoost/LightGBM
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run instructions
ENTRYPOINT ["streamlit", "run", "dashboards/1_📊_Overview.py", "--server.port=8501", "--server.address=0.0.0.0"]
