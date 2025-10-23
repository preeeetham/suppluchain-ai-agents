# Frontend Setup Guide

## 🎨 Supply Chain AI Agents Frontend

This guide will help you set up and run the Next.js frontend for the Supply Chain AI Agents system.

## 📋 Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend API server running (see main README)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# From project root directory
./start_development.sh
```

This script will:
- Start the backend API server
- Start the frontend development server
- Show you all available endpoints
- Monitor both servers

### Option 2: Manual Setup

#### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

#### 2. Start Backend API Server

```bash
# From project root
source venv/bin/activate
python3 -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Start Frontend Development Server

```bash
# In a new terminal, from frontend directory
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

## 📊 Available Pages

The frontend includes the following pages:

1. **Dashboard** (`/`) - Main overview with real-time metrics
2. **Agents** (`/agents`) - AI agent status and performance
3. **Inventory** (`/inventory`) - Real-time inventory management
4. **Demand** (`/demand`) - Demand forecasting and trends
5. **Routes** (`/routes`) - Route optimization and logistics
6. **Suppliers** (`/suppliers`) - Supplier management and coordination
7. **Blockchain** (`/blockchain`) - Solana blockchain transactions
8. **Analytics** (`/analytics`) - Advanced analytics and insights
9. **Knowledge Graph** (`/knowledge-graph`) - MeTTa knowledge graph visualization
10. **Simulation** (`/simulation`) - System simulation and testing
11. **Alerts** (`/alerts`) - System alerts and notifications
12. **Settings** (`/settings`) - System configuration

## 🔧 API Integration

### Real Data Sources

The frontend connects to real data sources:

- **MeTTa Knowledge Graphs**: Inventory, demand, routes, suppliers
- **Solana Blockchain**: Transactions, wallet balances, network status
- **AI Agents**: Real-time status, performance metrics, activities
- **No Hardcoded Data**: All data is dynamic and real-time

### API Endpoints

| Endpoint | Description | Data Source |
|----------|-------------|-------------|
| `/api/agents` | Agent status and performance | AI Agents |
| `/api/inventory` | Inventory data | MeTTa Knowledge Graph |
| `/api/demand` | Demand forecasts | MeTTa Knowledge Graph |
| `/api/routes` | Route optimization | MeTTa Knowledge Graph |
| `/api/suppliers` | Supplier information | MeTTa Knowledge Graph |
| `/api/blockchain` | Blockchain transactions | Solana Network |
| `/api/metrics` | System metrics | All Sources |
| `/api/activities` | Recent activities | AI Agents |
| `/api/alerts` | System alerts | All Sources |

## 🔄 Real-Time Updates

The frontend uses WebSocket connections for real-time updates:

- **Live Agent Status**: Real-time agent performance updates
- **Dynamic Metrics**: Live system metrics and KPIs
- **Real-Time Alerts**: Instant notification of system events
- **Live Data**: All data updates automatically without page refresh

## 🛠️ Development

### Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── page.tsx           # Dashboard (main page)
│   ├── agents/            # Agent management pages
│   ├── inventory/         # Inventory management
│   ├── demand/            # Demand forecasting
│   ├── routes/            # Route optimization
│   ├── suppliers/         # Supplier management
│   ├── blockchain/        # Blockchain integration
│   ├── analytics/         # Analytics dashboard
│   ├── knowledge-graph/   # Knowledge graph visualization
│   ├── simulation/        # System simulation
│   ├── alerts/            # System alerts
│   └── settings/          # System settings
├── components/            # Reusable UI components
├── hooks/                 # Custom React hooks
├── lib/                   # API client and utilities
└── styles/                # Global styles
```

### Key Components

- **API Client** (`lib/api.ts`): Handles all backend communication
- **Live Data Hooks** (`hooks/use-live-data.ts`): Real-time data management
- **WebSocket Client** (`lib/api.ts`): Real-time updates
- **Dashboard Components**: Real-time metrics and charts

### Error Handling

The frontend gracefully handles connection issues:

- **Fallback Data**: Shows "Connecting..." status when backend is unavailable
- **Automatic Retry**: WebSocket connections retry automatically
- **Graceful Degradation**: Frontend works even without backend connection
- **User Feedback**: Clear status messages for connection state

## 🧪 Testing

### Run Frontend Tests

```bash
cd frontend
npm run test
```

### Run Integration Tests

```bash
# From project root
python3 test_fullstack_integration.py
```

### Manual Testing

1. **Start Backend**: Ensure API server is running
2. **Start Frontend**: Run `npm run dev`
3. **Check Data**: Verify all data is real (not hardcoded)
4. **Test Real-Time**: Check WebSocket updates work
5. **Test Offline**: Stop backend and verify graceful handling

## 🚨 Troubleshooting

### Common Issues

#### 1. "Failed to fetch" Errors
- **Cause**: Backend API server not running
- **Solution**: Start the API server first
- **Check**: Visit http://localhost:8000/docs

#### 2. WebSocket Connection Errors
- **Cause**: WebSocket server not available
- **Solution**: Ensure backend is running on port 8000
- **Check**: WebSocket should connect to ws://localhost:8000/ws

#### 3. Frontend Shows "Connecting..." Status
- **Cause**: Backend not responding
- **Solution**: Check API server logs
- **Check**: Verify all dependencies are installed

#### 4. Build Errors
- **Cause**: Missing dependencies or TypeScript errors
- **Solution**: Run `npm install` and check for TypeScript errors
- **Check**: Ensure Node.js version is 18+

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export DEBUG=true
npm run dev
```

## 📈 Performance

### Optimization Features

- **Static Generation**: Pages are pre-rendered for better performance
- **Real-Time Updates**: Only updates changed data
- **Efficient Re-renders**: React hooks minimize unnecessary updates
- **WebSocket Optimization**: Smart reconnection and error handling

### Monitoring

- **Real-Time Metrics**: Live system performance
- **Connection Status**: WebSocket and API connection health
- **Error Tracking**: Automatic error reporting and recovery

## 🔒 Security

### Security Features

- **CORS Protection**: Proper cross-origin request handling
- **Input Validation**: All API inputs are validated
- **Error Handling**: Secure error messages without sensitive data
- **WebSocket Security**: Secure WebSocket connections

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Next.js Documentation**: https://nextjs.org/docs
- **React Hooks**: https://reactjs.org/docs/hooks-intro.html
- **WebSocket API**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

## 🎯 Success Criteria

✅ **Frontend builds successfully**  
✅ **All pages load without errors**  
✅ **Real-time data updates work**  
✅ **No hardcoded data displayed**  
✅ **WebSocket connections are stable**  
✅ **Graceful error handling**  
✅ **Responsive design works**  
✅ **All API endpoints connected**  

## 🚀 Production Deployment

For production deployment:

1. **Build Frontend**: `npm run build`
2. **Start Backend**: Use production WSGI server
3. **Configure Environment**: Set production API URLs
4. **Enable HTTPS**: For secure WebSocket connections
5. **Monitor Performance**: Use production monitoring tools

---

**🎉 Your Supply Chain AI Agents frontend is now ready!**

The frontend provides a complete interface for managing your autonomous supply chain agents with real-time data from MeTTa knowledge graphs, Solana blockchain, and AI agent performance metrics.
