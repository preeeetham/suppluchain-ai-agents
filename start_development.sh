#!/bin/bash

# Supply Chain AI Agents - Development Startup Script
# This script starts both the backend API server and frontend development server

echo "🚀 Starting Supply Chain AI Agents Development Environment"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Error: Frontend dependencies not installed. Please run: cd frontend && npm install"
    exit 1
fi

echo "✅ Environment checks passed"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ Development servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "🔧 Starting Backend API Server..."
echo "   - API will be available at: http://localhost:8000"
echo "   - WebSocket will be available at: ws://localhost:8000/ws"
echo ""

# Start API server in background
source venv/bin/activate
python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API server to start
echo "⏳ Waiting for API server to start..."
sleep 5

# Check if API server is running
if ! kill -0 $API_PID 2>/dev/null; then
    echo "❌ Failed to start API server"
    exit 1
fi

echo "✅ Backend API Server started (PID: $API_PID)"
echo ""

echo "🎨 Starting Frontend Development Server..."
echo "   - Frontend will be available at: http://localhost:3000"
echo ""

# Start frontend development server in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend server to start
echo "⏳ Waiting for frontend server to start..."
sleep 10

# Check if frontend server is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Failed to start frontend server"
    cleanup
    exit 1
fi

echo "✅ Frontend Development Server started (PID: $FRONTEND_PID)"
echo ""

echo "🎉 Development Environment Ready!"
echo "============================================================"
echo "📊 Backend API:     http://localhost:8000"
echo "🌐 Frontend:        http://localhost:3000"
echo "📡 WebSocket:       ws://localhost:8000/ws"
echo "📚 API Docs:        http://localhost:8000/docs"
echo ""
echo "🔍 Available API Endpoints:"
echo "   - GET /api/agents        - Agent status and performance"
echo "   - GET /api/inventory      - Inventory data from MeTTa"
echo "   - GET /api/demand         - Demand forecasts"
echo "   - GET /api/routes         - Route optimization data"
echo "   - GET /api/suppliers      - Supplier information"
echo "   - GET /api/blockchain     - Solana blockchain data"
echo "   - GET /api/metrics        - System metrics"
echo "   - GET /api/activities     - Recent activities"
echo "   - GET /api/alerts         - System alerts"
echo ""
echo "💡 Tips:"
echo "   - The frontend will show 'Connecting...' status until the backend is ready"
echo "   - All data comes from real sources (MeTTa, Solana, AI Agents)"
echo "   - No hardcoded data is displayed"
echo "   - Press Ctrl+C to stop both servers"
echo ""
echo "🔄 Monitoring logs..."
echo "============================================================"

# Monitor both processes
while true; do
    if ! kill -0 $API_PID 2>/dev/null; then
        echo "❌ API server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    sleep 5
done
