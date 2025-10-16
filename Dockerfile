FROM python:3.10-slim

WORKDIR /app

# Install build tools and Rust (needed for building some wheels like rpds-py)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   build-essential \
	   rustc \
	   cargo \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY smithery.yaml .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
