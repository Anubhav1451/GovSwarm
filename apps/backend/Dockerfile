FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies using python -m pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# Add Python global binaries pathway to system PATH
ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"

# Copy application files
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command for API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
