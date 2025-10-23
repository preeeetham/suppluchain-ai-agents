FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Solana CLI
RUN sh -c "$(curl -sSfL https://release.solana.com/v1.18.4/install)" && \
    export PATH="/root/.local/share/solana/install/active_release/bin:$PATH" && \
    echo 'export PATH="/root/.local/share/solana/install/active_release/bin:$PATH"' >> ~/.bashrc

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir uagents>=0.4.0
RUN pip install --no-cache-dir pandas>=1.5.0
RUN pip install --no-cache-dir numpy>=1.21.0
RUN pip install --no-cache-dir requests>=2.28.0
RUN pip install --no-cache-dir python-dotenv>=0.19.0
RUN pip install --no-cache-dir pytest>=7.0.0
RUN pip install --no-cache-dir solana>=0.30.0
RUN pip install --no-cache-dir solders>=0.20.0
RUN pip install --no-cache-dir base58>=2.1.0

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p blockchain_data/nfts blockchain_data/payments

# Set environment variables
ENV PYTHONPATH=/app
ENV SOLANA_RPC_URL=http://localhost:8899

# Expose ports
EXPOSE 8001 8002 8003 8004

# Default command
CMD ["python", "system_integration_test.py"]
