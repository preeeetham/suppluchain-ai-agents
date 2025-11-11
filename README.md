# 🚀 Supply Chain AI Agents

AI-powered supply chain optimization system with blockchain integration on Solana.

## 🎯 Quick Start

**See [START_PROJECT.md](START_PROJECT.md) for complete startup instructions.**

### TL;DR - Start in 4 Terminals:

```bash
# Terminal 1 - Blockchain (MUST START FIRST)
cd /Users/preet/Developer/supplychain-ai-agents
rm -rf test-ledger
solana-test-validator --reset --limit-ledger-size 50000000

# Terminal 2 - Backend
source venv/bin/activate && python3 api_server.py

# Terminal 3 - Agents
source venv/bin/activate && \
python3 agents/inventory_agent.py > agents/inventory_agent.log 2>&1 & \
python3 agents/demand_forecasting_agent.py > agents/demand_agent.log 2>&1 & \
python3 agents/route_optimization_agent.py > agents/route_agent.log 2>&1 & \
python3 agents/supplier_coordination_agent.py > agents/supplier_agent.log 2>&1 &

# Terminal 4 - Frontend
cd frontend && npm run dev
```

**Access:** http://localhost:3000

---

## 🌟 Features

- **AI Agents**: Inventory, Demand Forecasting, Route Optimization, Supplier Coordination
- **Blockchain**: Solana integration for transparent payments and NFT-based inventory tracking
- **Real-time**: Live updates via WebSocket connections
- **Analytics**: Comprehensive supply chain analytics and visualizations
- **Knowledge Graph**: MeTTa-based reasoning for intelligent decision making

---

## 🏗️ Architecture

- **Frontend**: Next.js 16 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Blockchain**: Solana (local validator)
- **AI Agents**: uAgents framework
- **Database**: JSON-based storage for rapid prototyping

---

## 📊 Services & Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000/docs |
| Solana Validator | 8899 | http://localhost:8899 |
| AI Agents | 8001-8004 | Internal |

---

## 💰 Funding Wallets

Wallets are automatically funded on backend startup. To manually fund:

```bash
source venv/bin/activate
python3 << 'EOF'
from solana_blockchain_integration import SolanaBlockchainIntegration
blockchain = SolanaBlockchainIntegration()
blockchain.auto_fund_wallets(min_balance=1.0)
EOF
```

## 🧪 Testing

### Backend Testing:
```bash
# Test all blockchain features
python3 test_all_blockchain_features.py
```

### Frontend Testing:
1. Open http://localhost:3000/blockchain
2. **Test NFT Creation:**
   - Click "Create NFT"
   - Fill form and submit
   - Verify NFT appears in gallery
3. **Test Page Refresh:**
   - Refresh 10+ times (should NOT crash)
4. **Test Wallet Balances:**
   - Verify all wallets show correct SOL amounts
5. **Test Transactions:**
   - View transaction history
   - Verify Solana Explorer links work

**See [START_PROJECT.md](START_PROJECT.md) for complete testing guide.**

---

## 📖 Documentation

- **[START_PROJECT.md](START_PROJECT.md)** - Complete startup guide
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Solana.py
- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **Blockchain**: Solana, SPL Token
- **AI**: uAgents, Fetch.ai
- **UI**: shadcn/ui, Recharts

---

## ⚡ Performance

- ✅ Page refresh optimized (no crashes)
- ✅ Efficient data caching
- ✅ Lightweight blockchain queries
- ✅ Real-time WebSocket updates

---

## 📝 License

See [LICENSE](LICENSE) file for details.

---

## 🚀 Status

**Version:** 2.0 (Optimized & Crash-Free)  
**Last Updated:** November 11, 2025  
**Status:** Production Ready ✅
