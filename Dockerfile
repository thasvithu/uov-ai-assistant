FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements (renamed from backend-requirements.txt by workflow)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "7860"]
