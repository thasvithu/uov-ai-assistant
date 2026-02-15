FROM python:3.11-slim

# Install system dependencies for openai-whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY .streamlit .streamlit

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run Streamlit on port 7860
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860"]
