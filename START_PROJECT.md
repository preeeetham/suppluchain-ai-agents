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

**⚠️ IMPORTANT: Follow this exact order to avoid errors!**

### Pre-Startup: Clean Up Previous Sessions

**Before starting, always clean up any leftover processes:**

```bash
cd /Users/preet/Developer/supplychain-ai-agents

# Stop all processes
pkill -f "solana-test-validator" 2>/dev/null
pkill -f "api_server" 2>/dev/null
pkill -f "agent.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Kill processes on ports (if pkill didn't work)
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8899 | xargs kill -9 2>/dev/null

# Clean ledger data (prevents validator crashes)
rm -rf test-ledger

echo "✅ Cleanup complete"
```

### Step 1: Start Solana Validator (Terminal 1)
**IMPORTANT: Keep this terminal open - blockchain runs here**

**Wait for validator to be ready before proceeding to Step 2!**

```bash
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000
```

**Why this method:**
- `rm -rf test-ledger` - Cleans old ledger data (prevents memory issues)
- `--reset` - Starts fresh blockchain state (⚠️ Wipes all balances!)
- `--limit-ledger-size 50000000` - Limits ledger size to prevent system kills

**Expected Output:**
```
Identity: EzbBDuixghcJNvQEDeEPEM9xkgoMwbuumgnruw6NQxxL
JSON RPC URL: http://127.0.0.1:8899
WebSocket PubSub URL: ws://127.0.0.1:8900
⠁ 00:00:16 | Processed Slot: 13003 | ...
```

**✅ Wait until you see "Processed Slot" messages before proceeding!**

**Verify validator is ready:**
```bash
# In a new terminal, run:
solana cluster-version --url http://localhost:8899
# Should return: "1.18.x" or similar version
```

### Step 2: Start Backend API (Terminal 2)

**⚠️ Wait for validator to be ready (Step 1) before starting backend!**

```bash
cd /Users/preet/Developer/supplychain-ai-agents

# Activate virtual environment
source venv/bin/activate

# Verify dependencies are installed
pip list | grep uvicorn || pip install -r requirements.txt

# Start backend
python3 api_server.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
Auto-funding wallets...
✅ Wallets funded successfully
```

**✅ Wait for "Application startup complete" before proceeding!**

**Verify backend is ready:**
```bash
# In a new terminal, run:
curl http://localhost:8000/docs
# Should return HTML (not error)
```

**If you see errors:**
- "Address already in use" → See Error 1 in Common Errors section
- "No module named uvicorn" → See Error 2 in Common Errors section
- "Failed to connect to validator" → Make sure Step 1 is complete

### Step 3: Start AI Agents (Terminal 3)

**⚠️ Wait for backend to be ready (Step 2) before starting agents!**

```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate

# Start all agents in background
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 &
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 &
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 &
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &

echo "✅ All agents started"

# Verify agents are running
sleep 2
ps aux | grep "agent.py" | grep -v grep | wc -l | awk '{print "✅ "$1" agents running"}'
```

**Verify agents are running:**
```bash
# Check agent logs for errors
tail -n 20 agents/inventory_agent.log
```

### Step 4: Start Frontend (Terminal 4)

**⚠️ Wait for backend to be ready (Step 2) before starting frontend!**

```bash
cd /Users/preet/Developer/supplychain-ai-agents/frontend

# Verify node_modules exists
[ -d "node_modules" ] || npm install

# Start frontend
npm run dev
```

**Expected Output:**
```
▲ Next.js 16.0.0
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
✓ Ready in 2.5s
```

**✅ Wait for "Ready" message before opening browser!**

**Verify frontend is ready:**
```bash
# In a new terminal, run:
curl http://localhost:3000
# Should return HTML (not error)
```

**If you see "Failed to fetch" errors:**
- Backend not running → Go back to Step 2
- Check browser console for specific errors
- See Error 3 in Common Errors section

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

## 🔄 Balance Update Problem & Solution (CRITICAL!)

### Problem: Wallet Balances Not Updating After SOL Transfers

**Symptoms:**
- After performing a SOL transfer via frontend, wallet balances remain unchanged
- Frontend shows old balances even though transaction is confirmed
- WebSocket updates may show stale data overwriting fresh balance queries

**Root Causes:**
1. **Test Validator Delay**: Solana test validator needs time to propagate balance changes
2. **Cache Staleness**: Backend cache not refreshed after transfers
3. **WebSocket Race Condition**: WebSocket updates overwriting fresh manual balance fetches

### Solution Implemented

#### Backend Fix (`api_server.py` - `/api/blockchain/transfer` endpoint):

```python
# After transfer completes:
1. Wait 1.0 second for test validator to propagate balance
2. Force refresh wallet balances directly from blockchain (bypass cache)
3. Update backend cache with fresh balances
4. Refresh transaction list
5. Broadcast updated data via WebSocket
```

**Key Code Changes:**
- Added `await asyncio.sleep(1.0)` after transfer for balance propagation
- Force refresh: `blockchain_integration.get_wallet_summary()` (fresh query, no cache)
- Update cache: `blockchain_cache["wallets"] = wallet_summary`
- Broadcast fresh data via WebSocket

#### Frontend Fix (`frontend/app/blockchain/page.tsx` - TransferSOLModal):

```typescript
onSuccess={async () => {
  // Wait 1.5s for transaction confirmation
  await new Promise(resolve => setTimeout(resolve, 1500))
  // Trigger backend balance refresh
  await apiClient.refreshWalletBalances()
  // Fetch fresh data with balance refresh enabled
  await refetchWithBalances?.()
  // Final refresh after 2s for confirmation
  setTimeout(() => {
    refetchWithBalances?.()
  }, 2000)
}}
```

#### Frontend Hook Fix (`frontend/hooks/use-live-data.ts` - useBlockchain):

**Problem:** WebSocket updates were overwriting fresh manual balance fetches

**Solution:** Implemented time-based WebSocket update filtering

```typescript
const lastFetchTimeRef = useRef<number>(Date.now())

// On manual fetch:
lastFetchTimeRef.current = Date.now()

// On WebSocket update:
const timeSinceLastFetch = Date.now() - lastFetchTimeRef.current
if (timeSinceLastFetch > 2000) { // Only use WebSocket if > 2s since manual fetch
  setBlockchain(data.blockchain)
}
```

**Why This Works:**
- Prevents stale WebSocket data from overwriting fresh manual fetches
- Allows WebSocket updates for real-time updates when not manually refreshing
- 2-second window ensures manual refresh takes priority

### How to Verify Balance Updates Work:

1. **Check Initial Balances:**
   ```bash
   curl http://localhost:8000/api/blockchain | python3 -m json.tool | grep -A 2 "main_wallet"
   ```

2. **Perform Transfer via Frontend:**
   - Go to http://localhost:3000/blockchain
   - Click "Transfer SOL"
   - Transfer 5 SOL from `main_wallet` to `warehouse_001`
   - Click "Transfer"

3. **Verify Balance Update:**
   - ✅ Frontend should update within 2-3 seconds
   - ✅ Both wallets should show updated balances
   - ✅ Transaction should appear in history
   - ✅ No need to manually refresh page

4. **If Balances Don't Update:**
   - Click "Refresh Balances" button on blockchain page
   - Check backend logs: `tail -f api_server.log`
   - Verify validator is running: `solana cluster-version --url http://localhost:8899`

### Manual Balance Refresh:

If balances still don't update automatically:

```bash
# Via API
curl -X POST http://localhost:8000/api/blockchain/refresh-balances

# Via Frontend
# Click "Refresh Balances" button on http://localhost:3000/blockchain
```

---

## 🚨 Common Startup Errors & Fixes

### Error 1: "Address already in use" (Port 8000 or 3000)

**Problem:** Previous process still running on port

**Fix:**
```bash
# Kill process on port 8000 (Backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (Frontend)
lsof -ti:3000 | xargs kill -9

# Then restart the service
```

### Error 2: "No module named uvicorn"

**Problem:** Virtual environment not activated or dependencies not installed

**Fix:**
```bash
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
pip install -r requirements.txt
python3 api_server.py
```

### Error 3: "Failed to fetch" (Frontend can't connect to Backend)

**Problem:** Backend not running or wrong port

**Fix:**
```bash
# Check if backend is running
curl http://localhost:8000/docs

# If not running, start it:
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
python3 api_server.py
```

### Error 4: Wallets Showing 0 Balance

**Problem:** Validator was reset (wipes all balances) or auto-funding didn't run

**Fix:**
```bash
# Check if validator is running
solana cluster-version --url http://localhost:8899

# If validator is running, restart backend (auto-funding runs on startup)
# Or manually fund wallets:
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
python3 << 'EOF'
from solana_blockchain_integration import SolanaBlockchainIntegration
blockchain = SolanaBlockchainIntegration()
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

### Error 5: Validator Gets Killed by macOS

**Problem:** Ledger data too large, macOS kills process

**Fix:**
```bash
# Always clean ledger before starting
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000
```

### Error 6: Backend Crashes on Page Refresh

**Problem:** WebSocket connection issues or excessive refresh requests

**Fix:**
- This was fixed in the codebase
- If still happening, check backend logs: `tail -f api_server.log`
- Restart backend if needed

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

### Start Everything (Follow Order!):
```bash
# STEP 0: Clean up first
cd /Users/preet/Developer/supplychain-ai-agents
pkill -f "solana-test-validator" 2>/dev/null
pkill -f "api_server" 2>/dev/null
pkill -f "agent.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8899 | xargs kill -9 2>/dev/null
rm -rf test-ledger

# STEP 1: Terminal 1 - Validator (MUST START FIRST, WAIT FOR READY!)
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000
# ⚠️ Wait until you see "Processed Slot" messages!

# STEP 2: Terminal 2 - Backend (WAIT FOR VALIDATOR TO BE READY!)
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
pip list | grep uvicorn || pip install -r requirements.txt
python3 api_server.py
# ⚠️ Wait for "Application startup complete"!

# STEP 3: Terminal 3 - Agents (WAIT FOR BACKEND TO BE READY!)
cd /Users/preet/Developer/supplychain-ai-agents
source venv/bin/activate
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 & \
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 & \
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 & \
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &
echo "✅ All agents started"

# STEP 4: Terminal 4 - Frontend (WAIT FOR BACKEND TO BE READY!)
cd /Users/preet/Developer/supplychain-ai-agents/frontend
[ -d "node_modules" ] || npm install
npm run dev
# ⚠️ Wait for "Ready" message!
```

### Stop Everything:
```bash
cd /Users/preet/Developer/supplychain-ai-agents

# Stop all processes
pkill -f "solana-test-validator"
pkill -f "api_server"
pkill -f "agent.py"
pkill -f "next dev"

# Kill by port (if pkill didn't work)
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8899 | xargs kill -9 2>/dev/null

echo "✅ All processes stopped"
```

### Check Status:
```bash
# Quick status check
echo "Checking services..."
curl -s http://localhost:8000/docs > /dev/null && echo "✅ Backend running" || echo "❌ Backend down"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend down"
solana cluster-version --url http://localhost:8899 > /dev/null 2>&1 && echo "✅ Validator running" || echo "❌ Validator down"
ps aux | grep "agent.py" | grep -v grep | wc -l | awk '{if ($1 > 0) print "✅ "$1" agents running"; else print "❌ No agents running"}'
```

### Verify Wallet Balances:
```bash
# Check if wallets are funded
curl -s http://localhost:8000/api/blockchain | python3 -m json.tool | grep -A 2 "main_wallet" | grep "sol_balance"
# Should show a balance > 0 (e.g., "sol_balance": 100.0)

# If balances are 0, restart backend (auto-funding runs on startup)
# Or manually fund (see Error 4 in Common Errors section)
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

