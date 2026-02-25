#!/bin/bash
set -e

# Configuration 
S3_BUCKET="s3://hotel-retention-artifacts"

echo "==========================================="
echo "🏨 Initializing Hotel Retention Container"
echo "==========================================="

# 1. Download ML Model from S3 if it doesn't exist
if [ ! -f "/app/models/model.joblib" ]; then
    echo "⬇️ Downloading ML Model from S3..."
    mkdir -p /app/models
    # We download the model.joblib. Adjust path if it's named churn_model.joblib.
    aws s3 cp ${S3_BUCKET}/model/model.joblib /app/models/model.joblib || echo "⚠️ Warning: Failed to download model.joblib"
else
    echo "✅ ML Model already exists locally."
fi

# 2. Download Vector Store from S3 if it doesn't exist
if [ ! -d "/app/vectorstore/chroma_db" ]; then
    echo "⬇️ Downloading ChromaDB Vector Store from S3..."
    mkdir -p /app/vectorstore
    aws s3 sync ${S3_BUCKET}/vectorstore/chroma_db /app/vectorstore/chroma_db || echo "⚠️ Warning: Failed to sync chroma_db"
else
    echo "✅ Vector Store already exists locally."
fi

# 3. Seed Database 
echo "🌱 Seeding the SQLite database..."
if [ -f "seed_database.py" ]; then
    python seed_database.py || echo "⚠️ seed_database.py failed or not found, continuing."
else
    echo "⚠️ seed_database.py not found, skipping."
fi

echo "🚀 Starting Services..."

# 4. Start the Flask backend in the background
echo "Starting Flask Server (Backend)..."
python main.py &

# 5. Start the Streamlit frontend in the foreground
echo "Starting Streamlit App (Frontend)..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
