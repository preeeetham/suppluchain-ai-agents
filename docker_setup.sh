#!/bin/bash

echo "🐳 DOCKER SETUP FOR SUPPLY CHAIN AI AGENTS"
echo "=========================================="

# Create necessary directories
mkdir -p blockchain_data/nfts blockchain_data/payments solana-config

# Build and start the Docker containers
echo "🔨 Building Docker containers..."
docker-compose build

echo "🚀 Starting Solana validator..."
docker-compose up -d solana-validator

# Wait for Solana validator to be ready
echo "⏳ Waiting for Solana validator to be ready..."
sleep 10

# Check if Solana validator is running
echo "🔍 Checking Solana validator status..."
docker-compose exec solana-validator solana cluster-version

echo "✅ Solana validator is ready!"
echo "🔗 RPC URL: http://localhost:8899"
echo "📊 Metrics URL: http://localhost:9900"

# Start the supply chain application
echo "🤖 Starting Supply Chain AI Agents..."
docker-compose up -d supply-chain-app

# Wait for agents to start
echo "⏳ Waiting for AI agents to initialize..."
sleep 15

# Run the large-scale simulation
echo "🚀 Running large-scale simulation..."
docker-compose run --rm supply-chain-simulator python large_scale_simulation.py

echo "✅ Docker setup complete!"
echo "📊 Check logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
