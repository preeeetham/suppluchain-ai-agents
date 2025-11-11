#!/bin/bash

# Solana Test Validator Startup Script
# Prevents validator from being killed by system

echo "🔗 Starting Solana Test Validator (Optimized)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Clean up old ledger to prevent memory issues
echo ""
echo "🧹 Cleaning old ledger data..."
rm -rf test-ledger
echo "✅ Old data removed"

echo ""
echo "🚀 Starting validator with optimized settings..."
echo ""

# Start validator with resource limits
solana-test-validator \
  --reset \
  --quiet \
  --rpc-port 8899 \
  --faucet-sol 1000000 \
  --limit-ledger-size 50000000 \
  --log test-ledger/validator.log

# If the above gets killed, the script will show this:
echo ""
echo "⚠️  Validator was terminated"
echo ""
echo "💡 If validator keeps getting killed:"
echo "   1. Check Activity Monitor for memory usage"
echo "   2. Close other heavy applications"
echo "   3. Restart your Mac if memory is low"
echo "   4. Or use --limit-ledger-size with smaller value"

