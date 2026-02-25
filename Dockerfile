FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (AWS CLI for S3 downloads + SQLite)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    sqlite3 \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip ./aws \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# (models, vectorstore, and .db files are excluded via .dockerignore)
COPY . .

# Expose ports for Flask (5000) and Streamlit (8501)
EXPOSE 5000
EXPOSE 8501

# Make the startup script executable
RUN chmod +x start.sh

# Run the startup script to download artifacts, seed DB, and launch API & UI
CMD ["./start.sh"]
