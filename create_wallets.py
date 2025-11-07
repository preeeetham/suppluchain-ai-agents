#!/usr/bin/env python3
"""
Quick wallet creation script for Supply Chain AI Agents
Creates wallets and saves them to solana_wallets.json
"""

import json
import os
from solders.keypair import Keypair
import base58

def create_wallet(name: str) -> dict:
    """Create a new Solana wallet and return keypair info"""
    keypair = Keypair()
    
    wallet_info = {
        "name": name,
        "public_key": str(keypair.pubkey()),
        "private_key": base58.b58encode(bytes(keypair)).decode('utf-8'),
        "secret_key": bytes(keypair).hex()
    }
    
    return wallet_info

def main():
    """Create all wallets needed for the supply chain system"""
    print("🔑 Creating Solana Wallets for Supply Chain AI Agents")
    print("=" * 60)
    
    wallets = {}
    
    # List of wallets to create
    wallet_names = [
        "main_wallet",           # Main funding wallet
        "inventory_agent",       # Inventory Management Agent wallet
        "demand_agent",          # Demand Forecasting Agent wallet
        "route_agent",           # Route Optimization Agent wallet
        "supplier_agent",        # Supplier Coordination Agent wallet
        "warehouse_001",         # Warehouse 1 wallet
        "warehouse_002",         # Warehouse 2 wallet
        "warehouse_003",         # Warehouse 3 wallet
        "supplier_001",          # Supplier 1 wallet
        "supplier_002",          # Supplier 2 wallet
        "supplier_003",          # Supplier 3 wallet
        "customer_001",          # Customer 1 wallet
        "customer_002",          # Customer 2 wallet
        "customer_003",          # Customer 3 wallet
    ]
    
    print("\n📝 Creating wallets...")
    for wallet_name in wallet_names:
        wallet = create_wallet(wallet_name)
        wallets[wallet_name] = wallet
        print(f"✅ {wallet_name:20} - {wallet['public_key']}")
    
    # Save to file
    wallet_file = "solana_wallets.json"
    
    # Remove directory if it exists
    if os.path.exists(wallet_file) and os.path.isdir(wallet_file):
        os.rmdir(wallet_file)
        print(f"\n🗑️  Removed existing directory: {wallet_file}")
    
    # Save wallets
    with open(wallet_file, 'w') as f:
        json.dump(wallets, f, indent=2)
    
    print(f"\n💾 Wallets saved to {wallet_file}")
    
    # Display main wallet address prominently
    main_wallet = wallets["main_wallet"]
    print("\n" + "=" * 60)
    print("🎯 MAIN WALLET ADDRESS (Fund this with Devnet SOL):")
    print("=" * 60)
    print(f"Public Key: {main_wallet['public_key']}")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Copy the main wallet address above")
    print("2. Get Devnet SOL from: https://faucet.solana.com/")
    print("3. Send SOL to the main wallet address")
    print("4. Once funded, you can distribute SOL to other wallets")
    print("\n✅ All wallets created successfully!")
    
    return wallets

if __name__ == "__main__":
    main()

