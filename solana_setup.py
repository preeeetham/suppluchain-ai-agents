"""
Solana Development Setup for Supply Chain AI Agents
Creates wallets, configures devnet, and sets up token infrastructure
"""

import json
import os
import asyncio
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solana.system_program import create_account, CreateAccountParams
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import create_mint, initialize_mint, create_account as create_token_account
import base58
import requests

class SolanaSupplyChainSetup:
    def __init__(self, devnet_url="https://api.devnet.solana.com"):
        self.devnet_url = devnet_url
        self.client = Client(devnet_url)
        self.wallets = {}
        self.token_mints = {}
        
    def create_wallet(self, name: str) -> dict:
        """Create a new Solana wallet and return keypair info"""
        keypair = Keypair()
        
        wallet_info = {
            "name": name,
            "public_key": str(keypair.public_key),
            "private_key": base58.b58encode(keypair.secret_key).decode('utf-8'),
            "secret_key": keypair.secret_key.hex()
        }
        
        self.wallets[name] = wallet_info
        return wallet_info
    
    def create_all_wallets(self):
        """Create all necessary wallets for the supply chain system"""
        wallets_to_create = [
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
        
        for wallet_name in wallets_to_create:
            self.create_wallet(wallet_name)
            print(f"✅ Created wallet: {wallet_name}")
            print(f"   Public Key: {self.wallets[wallet_name]['public_key']}")
        
        return self.wallets
    
    def save_wallets_to_file(self, filename="solana_wallets.json"):
        """Save all wallet information to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.wallets, f, indent=2)
        print(f"💾 Wallets saved to {filename}")
    
    def load_wallets_from_file(self, filename="solana_wallets.json"):
        """Load wallet information from JSON file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                self.wallets = json.load(f)
            print(f"📁 Wallets loaded from {filename}")
            return True
        return False
    
    def get_wallet_balance(self, wallet_name: str) -> float:
        """Get SOL balance for a wallet"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        public_key = PublicKey(self.wallets[wallet_name]['public_key'])
        balance = self.client.get_balance(public_key)
        return balance.value / 1e9  # Convert lamports to SOL
    
    def airdrop_sol(self, wallet_name: str, amount: float = 2.0):
        """Request SOL airdrop for a wallet (devnet only)"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        public_key = PublicKey(self.wallets[wallet_name]['public_key'])
        
        try:
            # Request airdrop
            signature = self.client.request_airdrop(public_key, int(amount * 1e9))
            print(f"🪂 Airdrop requested for {wallet_name}: {signature.value}")
            return signature.value
        except Exception as e:
            print(f"❌ Airdrop failed for {wallet_name}: {e}")
            return None
    
    def create_supply_chain_token(self, mint_authority_wallet: str = "main_wallet"):
        """Create the Supply Chain Token (SCT)"""
        if mint_authority_wallet not in self.wallets:
            raise ValueError(f"Wallet {mint_authority_wallet} not found")
        
        # Create mint keypair
        mint_keypair = Keypair()
        mint_authority = PublicKey(self.wallets[mint_authority_wallet]['public_key'])
        
        # Create mint account
        mint_rent = self.client.get_minimum_balance_for_rent_exemption(82)  # Mint account size
        mint_account_ix = create_account(
            CreateAccountParams(
                from_pubkey=mint_authority,
                to_pubkey=mint_keypair.public_key,
                lamports=mint_rent.value,
                space=82,
                program_id=TOKEN_PROGRAM_ID
            )
        )
        
        # Initialize mint
        init_mint_ix = initialize_mint(
            mint=mint_keypair.public_key,
            decimals=6,  # 6 decimals for SCT
            mint_authority=mint_authority,
            freeze_authority=mint_authority
        )
        
        # Create transaction
        transaction = Transaction()
        transaction.add(mint_account_ix)
        transaction.add(init_mint_ix)
        
        try:
            # Send transaction
            signature = self.client.send_transaction(transaction, mint_keypair)
            print(f"🪙 Supply Chain Token created: {signature.value}")
            
            token_info = {
                "mint": str(mint_keypair.public_key),
                "mint_authority": str(mint_authority),
                "decimals": 6,
                "signature": signature.value
            }
            
            self.token_mints["SCT"] = token_info
            return token_info
            
        except Exception as e:
            print(f"❌ Token creation failed: {e}")
            return None
    
    def create_token_account(self, wallet_name: str, token_mint: str):
        """Create a token account for a wallet"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        wallet_pubkey = PublicKey(self.wallets[wallet_name]['public_key'])
        mint_pubkey = PublicKey(token_mint)
        
        # Create associated token account
        token_account = Token.get_associated_token_address(wallet_pubkey, mint_pubkey)
        
        try:
            # Create the account
            signature = self.client.send_transaction(
                Transaction().add(
                    create_token_account(
                        payer=wallet_pubkey,
                        owner=wallet_pubkey,
                        mint=mint_pubkey
                    )
                )
            )
            
            print(f"💳 Token account created for {wallet_name}: {signature.value}")
            return str(token_account)
            
        except Exception as e:
            print(f"❌ Token account creation failed for {wallet_name}: {e}")
            return None
    
    def print_wallet_summary(self):
        """Print summary of all wallets and their balances"""
        print("\n" + "="*80)
        print("🔑 SOLANA WALLET SUMMARY")
        print("="*80)
        
        for name, wallet in self.wallets.items():
            try:
                balance = self.get_wallet_balance(name)
                print(f"💰 {name:15} | {wallet['public_key']:44} | {balance:8.4f} SOL")
            except Exception as e:
                print(f"❌ {name:15} | {wallet['public_key']:44} | Error: {e}")
        
        print("="*80)
        print(f"📊 Total Wallets: {len(self.wallets)}")
        print("="*80)

def main():
    """Main setup function"""
    print("🚀 SOLANA SUPPLY CHAIN SETUP")
    print("="*50)
    
    # Initialize setup
    setup = SolanaSupplyChainSetup()
    
    # Create all wallets
    print("\n🔑 Creating wallets...")
    setup.create_all_wallets()
    
    # Save wallets to file
    setup.save_wallets_to_file()
    
    # Print wallet summary
    setup.print_wallet_summary()
    
    # Create Supply Chain Token
    print("\n🪙 Creating Supply Chain Token...")
    token_info = setup.create_supply_chain_token()
    
    if token_info:
        print(f"✅ SCT Token Mint: {token_info['mint']}")
        print(f"✅ Mint Authority: {token_info['mint_authority']}")
        
        # Save token info
        with open("solana_tokens.json", 'w') as f:
            json.dump(setup.token_mints, f, indent=2)
        print("💾 Token info saved to solana_tokens.json")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Fund the main_wallet with devnet SOL")
    print("2. Run: python solana_setup.py --airdrop")
    print("3. Start the supply chain agents with Solana integration")
    
    return setup

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--airdrop":
        # Airdrop SOL to all wallets
        setup = SolanaSupplyChainSetup()
        setup.load_wallets_from_file()
        
        print("🪂 Requesting airdrops for all wallets...")
        for wallet_name in setup.wallets.keys():
            setup.airdrop_sol(wallet_name, 2.0)
        
        setup.print_wallet_summary()
    else:
        main()
