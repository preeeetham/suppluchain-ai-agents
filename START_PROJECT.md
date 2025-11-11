# 🚀 Supply Chain AI Agents - Project Startup Guide

Complete guide for starting the project with no confusion.

---

## 📋 Prerequisites

- Python 3.13+ installed
- Node.js 18+ and npm installed
- Solana CLI installed
- Docker Desktop installed (optional)

---

## 🎯 Quick Start (Recommended Method)

### Step 1: Start Solana Validator (Terminal 1)
**IMPORTANT: Keep this terminal open - blockchain runs here**

**Recommended Method (Clean Start):**
```bash
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000
```

**Why this method:**
- `rm -rf test-ledger` - Cleans old ledger data (prevents memory issues)
- `--reset` - Starts fresh blockchain state
- `--limit-ledger-size 50000000` - Limits ledger size to prevent system kills

**Expected Output:**
```
Identity: EzbBDuixghcJNvQEDeEPEM9xkgoMwbuumgnruw6NQxxL
JSON RPC URL: http://127.0.0.1:8899
WebSocket PubSub URL: ws://127.0.0.1:8900
⠁ 00:00:16 | Processed Slot: 13003 | ...
```

**If validator gets killed:**
- Old ledger data may be too large (macOS kills processes using too much memory)
- Always use: `rm -rf test-ledger` before starting
- The `--limit-ledger-size 50000000` flag helps prevent this

### Step 2: Start Backend API (Terminal 2)

```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
python3 api_server.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verify:** Open http://localhost:8000/docs

### Step 3: Start AI Agents (Terminal 3)

```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate

# Start all agents in background
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 &
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 &
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 &
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &

echo "✅ All agents started"
```

### Step 4: Start Frontend (Terminal 4)

```bash
cd /Users/preet/Developer/supplychain-ai-agents/frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
```

**Verify:** Open http://localhost:3000

---

## ✅ Verify Everything is Running

```bash
# Check all services
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend running" || echo "❌ Backend down"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend down"
solana cluster-version --url http://localhost:8899 && echo "✅ Validator running" || echo "❌ Validator down"
ps aux | grep "agent.py" | grep -v grep | wc -l | awk '{print "✅ "$1" agents running"}'
```

---

## 🐳 Alternative: Docker Method (Not Recommended - Has Issues)

**Current Issue:** uagents library requires Python 3.8-3.10, Docker uses Python 3.11

If you want to try Docker anyway:

```bash
cd /Users/preet/Developer/supplychain-ai-agents

# Start services (blockchain runs on host terminal)
docker-compose up -d backend-api supply-chain-agents

# Check logs
docker logs supply-chain-backend
docker logs supply-chain-agents
```

---

## 🛑 Stop All Services

### Stop Terminal Services:
```bash
cd /Users/preet/Developer/supplychain-ai-agents

# Stop all processes
pkill -f "solana-test-validator"
pkill -f "api_server"
pkill -f "agent.py"
pkill -f "next dev"

# Or kill by port
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8899 | xargs kill -9  # Validator
```

### Stop Docker Services (if using Docker):
```bash
docker-compose down
```

---

## 📊 Port Allocation

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 3000 | http://localhost:3000 |
| Solana Validator | 8899 | http://localhost:8899 |
| Solana WebSocket | 8900 | ws://localhost:8900 |
| Inventory Agent | 8001 | Internal |
| Demand Agent | 8002 | Internal |
| Route Agent | 8003 | Internal |
| Supplier Agent | 8004 | Internal |

---

## 💰 Funding Wallets (IMPORTANT!)

**Before testing blockchain features, wallets need SOL:**

### Automatic Funding (On Backend Startup):
The backend automatically funds wallets on first startup if they have 0 SOL:
- Main wallet: 100 SOL
- Warehouse wallets: 20 SOL each
- Supplier wallets: 20 SOL each

### Manual Funding (If Needed):
```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
python3 << 'EOF'
from solana_blockchain_integration import SolanaBlockchainIntegration

blockchain = SolanaBlockchainIntegration()

# Fund specific wallets
blockchain.auto_fund_wallets(
    min_balance=1.0,
    funding_amounts={
        "main_wallet": 100.0,
        "warehouse_001": 20.0,
        "warehouse_002": 20.0,
        "warehouse_003": 20.0,
        "supplier_001": 20.0,
        "supplier_002": 20.0,
    }
)
print("✅ Wallets funded!")
EOF
```

### Check Wallet Balances:
```bash
# Via API
curl http://localhost:8000/api/blockchain | python3 -m json.tool | grep -A 5 "wallet_summary"

# Via Frontend
# Open http://localhost:3000/blockchain
# Check "Wallet Summary" section
```

---

## 🧪 Testing All Blockchain Features

### Step 1: Verify System is Running
```bash
# Check all services
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend" || echo "❌ Backend"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend" || echo "❌ Frontend"
solana cluster-version --url http://localhost:8899 && echo "✅ Validator" || echo "❌ Validator"
```

### Step 2: Test via Backend API
```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate

# Test all blockchain features
python3 test_all_blockchain_features.py
```

**Expected Output:**
- ✅ Wallet creation
- ✅ Wallet balance queries
- ✅ SOL transfers
- ✅ Payment processing
- ✅ NFT minting
- ✅ NFT transfers
- ✅ Transaction history

### Step 3: Test via Frontend UI

**Open:** http://localhost:3000/blockchain

#### Test 1: Wallet Balances
- ✅ Check "Wallet Summary" section
- ✅ Main wallet should show 100 SOL
- ✅ Warehouse wallets should show 20 SOL each
- ✅ All balances should be visible

#### Test 2: NFT Creation
1. Click **"Create NFT"** button
2. Fill in form:
   - Product ID: `TEST-PRODUCT-001`
   - Warehouse: `warehouse_001`
   - Product Name: `Test Product`
   - Category: `Electronics`
   - Quantity: `100`
   - Unit Price: `50`
3. Click **"Create NFT"**
4. Wait 30-60 seconds for confirmation
5. ✅ NFT should appear in "NFT Gallery" section
6. ✅ Should show "On-chain" badge
7. ✅ Mint address should be visible

#### Test 3: NFT Transfer
1. Find an existing NFT in gallery
2. Click **"Transfer"** button (if available)
3. Select new owner wallet
4. ✅ Ownership should update
5. ✅ Transaction should appear in history

#### Test 4: SOL Transfer
1. Click **"Transfer SOL"** button
2. Fill in:
   - From: `main_wallet`
   - To: `warehouse_001`
   - Amount: `5.0`
3. Click **"Transfer"**
4. ✅ Transaction should appear in history
5. ✅ Balances should update

#### Test 5: Page Refresh Stability (CRITICAL)
1. Refresh page 10+ times (Cmd+Shift+R or F5)
2. ✅ Backend should stay running
3. ✅ No crashes
4. ✅ All data should display correctly
5. ✅ WebSocket connections should work

#### Test 6: Transaction History
- ✅ Should show all past transactions
- ✅ Should show payment details
- ✅ Should show SOL transfers
- ✅ "View on Solana Explorer" links should work

#### Test 7: Network Status
- ✅ Should show "healthy" status
- ✅ Should show current slot number
- ✅ Should show transactions/sec

### Step 4: Verify On-Chain Data
```bash
# Check NFT files
ls -lt blockchain_data/nfts/*.json | head -5

# Check transaction files
ls -lt blockchain_data/payments/*.json | head -5

# Verify NFT is on-chain
cat blockchain_data/nfts/TEST-PRODUCT-001_nft.json | python3 -m json.tool | grep -E "on_chain|status|mint_address"
```

**Expected:**
- `"on_chain": true`
- `"status": "confirmed"`
- Valid `mint_address` present

---

## ✅ Feature Checklist

After testing, verify all features work:

- [ ] ✅ Validator starts without crashes
- [ ] ✅ Wallets are funded (100 SOL main, 20 SOL warehouses)
- [ ] ✅ Wallet balances display in frontend
- [ ] ✅ NFT creation works via frontend
- [ ] ✅ NFT appears in gallery with on-chain badge
- [ ] ✅ NFT transfer updates ownership
- [ ] ✅ SOL transfers work
- [ ] ✅ Transaction history displays
- [ ] ✅ Page refresh doesn't crash (test 10+ times)
- [ ] ✅ Network status shows healthy
- [ ] ✅ All API endpoints respond
- [ ] ✅ WebSocket updates work

---

## 🔧 Troubleshooting

### Backend Not Starting:
```bash
# Check if port is in use
lsof -ti:8000

# Kill process and restart
lsof -ti:8000 | xargs kill -9
source venv/bin/activate
python3 api_server.py
```

### Validator Not Responding:
```bash
# Check if validator is running
ps aux | grep solana-test-validator

# Restart validator (clean start)
cd /Users/preet/Developer/supplychain-ai-agents
pkill -f solana-test-validator
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000
```

### Frontend Build Errors:
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Agents Not Starting:
```bash
# Install missing dependencies
source venv/bin/activate
pip install cosmpy

# Restart agents
pkill -f agent.py
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 &
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 &
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 &
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &
```

### Check Logs:
```bash
# Backend logs
tail -f api_server.log

# Agent logs
tail -f agents/inventory_agent.log
tail -f agents/demand_agent.log
tail -f agents/route_agent.log
tail -f agents/supplier_agent.log

# Frontend logs (in frontend terminal)
```

---

## 📁 Project Structure

```
supplychain-ai-agents/
├── agents/                    # AI Agents
│   ├── inventory_agent.py
│   ├── demand_forecasting_agent.py
│   ├── route_optimization_agent.py
│   └── supplier_coordination_agent.py
├── frontend/                  # Next.js Frontend
│   ├── app/
│   ├── components/
│   └── package.json
├── blockchain_data/           # Blockchain data storage
│   ├── nfts/
│   └── payments/
├── api_server.py             # FastAPI Backend
├── solana_blockchain_integration.py
├── requirements.txt
└── docker-compose.yml

```

---

## 🎯 What Runs Where

### ✅ Terminal (Host System):
- **Solana Validator** - Must run on host for blockchain operations
- **Backend API** - Connects to local validator
- **Frontend** - Serves UI
- **AI Agents** - Connect to backend

### ❌ Docker (Optional, Not Recommended):
- Has compatibility issues with uagents library
- Use only if you fix Python version to 3.8-3.10

---

## 🚦 Startup Order (Important!)

1. **First:** Solana Validator (Terminal 1)
   - Wait until you see "Processed Slot" messages
   
2. **Second:** Backend API (Terminal 2)
   - Wait for "Application startup complete"
   
3. **Third:** AI Agents (Terminal 3)
   - Check logs to verify startup
   
4. **Fourth:** Frontend (Terminal 4)
   - Wait for "compiled successfully"

**Total startup time:** ~30-60 seconds

---

## ✨ Features Available

### Working Features:
- ✅ Wallet Management (25+ wallets)
- ✅ Payment Processing
- ✅ Transaction History
- ✅ Wallet Creation
- ✅ NFT Gallery
- ✅ Real-time Agent Updates
- ✅ Page Refresh (No crashes!)

### All Features Working (After Funding):
- ✅ SOL Transfers (requires funded wallets)
- ✅ NFT Minting (requires funded wallets)
- ✅ NFT Transfers
- ✅ Payment Processing

---

## 💡 Quick Tips

1. **Always start validator first** - Everything depends on it
2. **Keep validator terminal open** - Don't close it
3. **Check logs if issues** - They show what's wrong
4. **Use Ctrl+C to stop services** - Clean shutdown
5. **Refresh frontend after changes** - See latest updates

---

## 📞 Common Commands

### Start Everything:
```bash
# Terminal 1 - Validator (MUST START FIRST)
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000

# Terminal 2 - Backend
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate && python3 api_server.py

# Terminal 3 - Agents
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate && \
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 & \
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 & \
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 & \
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &

# Terminal 4 - Frontend
cd /Users/preet/Developer/supplychain-ai-agents/frontend && npm run dev
```

### Stop Everything:
```bash
pkill -f "solana-test-validator"
pkill -f "api_server"
pkill -f "agent.py"
pkill -f "next dev"
```

### Check Status:
```bash
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend" || echo "❌ Backend"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend" || echo "❌ Frontend"
solana cluster-version --url http://localhost:8899 && echo "✅ Validator" || echo "❌ Validator"
```

---

## 🎉 You're Ready!

Open http://localhost:3000 and start exploring the Supply Chain AI Agents system!

**Main Pages:**
- Dashboard: http://localhost:3000
- Blockchain: http://localhost:3000/blockchain
- Agents: http://localhost:3000/agents
- Analytics: http://localhost:3000/analytics
- API Docs: http://localhost:8000/docs

---

**Last Updated:** November 11, 2025  
**Version:** 2.0 (Optimized & Crash-Free)

