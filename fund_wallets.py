#!/usr/bin/env python3
"""
Quick script to fund wallets via CLI
Usage: python3 fund_wallets.py
"""

from solana_blockchain_integration import SolanaBlockchainIntegration

def main():
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

if __name__ == "__main__":
    main()

