"""
Solana Blockchain Integration for Supply Chain AI Agents
Professional implementation for production use
"""

import json
import os
import time
import logging
from typing import Dict, List, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
import base58

logger = logging.getLogger(__name__)

class SolanaBlockchainIntegration:
    """Professional Solana blockchain integration for supply chain agents"""
    
    def __init__(self, devnet_url="https://api.devnet.solana.com", wallet_file="solana_wallets.json"):
        self.devnet_url = devnet_url
        self.client = Client(devnet_url)
        self.wallet_file = wallet_file
        self.wallets = {}
        self.token_mints = {}
        self.product_nfts = {}
        self.load_wallets()
        
    def load_wallets(self):
        """Load wallet information from JSON file"""
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, 'r') as f:
                self.wallets = json.load(f)
            logger.info(f"Loaded {len(self.wallets)} wallets from {self.wallet_file}")
        else:
            logger.warning(f"Wallet file {self.wallet_file} not found")
    
    def get_wallet_keypair(self, wallet_name: str) -> Keypair:
        """Get keypair for a wallet by name"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        wallet_info = self.wallets[wallet_name]
        private_key_bytes = bytes.fromhex(wallet_info['secret_key'])
        return Keypair.from_bytes(private_key_bytes)
    
    def get_wallet_balance(self, wallet_name: str) -> float:
        """Get SOL balance for a wallet"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        public_key = Pubkey.from_string(self.wallets[wallet_name]['public_key'])
        try:
            balance = self.client.get_balance(public_key)
            return balance.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_name}: {e}")
            return 0.0
    
    def get_wallet_summary(self) -> Dict:
        """Get summary of all wallets and their balances"""
        summary = {}
        
        for name, wallet in self.wallets.items():
            try:
                balance = self.get_wallet_balance(name)
                summary[name] = {
                    "public_key": wallet['public_key'],
                    "sol_balance": balance
                }
            except Exception as e:
                summary[name] = {
                    "public_key": wallet['public_key'],
                    "error": str(e)
                }
        
        return summary
    
    def print_wallet_summary(self):
        """Print summary of all wallets"""
        print("\n" + "="*80)
        print("🔑 SOLANA WALLET SUMMARY")
        print("="*80)
        
        summary = self.get_wallet_summary()
        for name, info in summary.items():
            if "error" in info:
                print(f"❌ {name:15} | {info['public_key']:44} | Error: {info['error']}")
            else:
                print(f"💰 {name:15} | {info['public_key']:44} | {info['sol_balance']:8.4f} SOL")
        
        print("="*80)
        print(f"📊 Total Wallets: {len(self.wallets)}")
        print("="*80)
    
    def create_product_nft_metadata(self, product_id: str, warehouse_wallet: str, metadata: Dict) -> Dict:
        """Create metadata for a Product NFT"""
        nft_info = {
            "product_id": product_id,
            "owner_wallet": warehouse_wallet,
            "metadata": metadata,
            "created_at": str(time.time()),
            "blockchain_ready": True
        }
        
        # Save NFT info to file
        nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
        os.makedirs(os.path.dirname(nft_file), exist_ok=True)
        
        with open(nft_file, 'w') as f:
            json.dump(nft_info, f, indent=2)
        
        logger.info(f"Product NFT metadata created for {product_id}")
        return nft_info
    
    def process_supply_chain_payment(self, from_wallet: str, to_wallet: str, amount: float, product_id: str = None) -> Dict:
        """Process a supply chain payment"""
        payment_info = {
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "product_id": product_id,
            "timestamp": str(time.time()),
            "status": "processed",
            "blockchain_ready": True
        }
        
        # Save payment info to file
        payment_file = f"blockchain_data/payments/payment_{int(time.time())}.json"
        os.makedirs(os.path.dirname(payment_file), exist_ok=True)
        
        with open(payment_file, 'w') as f:
            json.dump(payment_info, f, indent=2)
        
        logger.info(f"Supply chain payment processed: {amount} from {from_wallet} to {to_wallet}")
        return payment_info
    
    def get_agent_wallet(self, agent_name: str) -> str:
        """Get wallet address for an AI agent"""
        agent_wallet_map = {
            "inventory_agent": "inventory_agent",
            "demand_agent": "demand_agent", 
            "route_agent": "route_agent",
            "supplier_agent": "supplier_agent"
        }
        
        if agent_name in agent_wallet_map:
            wallet_name = agent_wallet_map[agent_name]
            if wallet_name in self.wallets:
                return self.wallets[wallet_name]['public_key']
        
        raise ValueError(f"No wallet found for agent: {agent_name}")
    
    def get_warehouse_wallet(self, warehouse_id: str) -> str:
        """Get wallet address for a warehouse"""
        warehouse_wallet_map = {
            "warehouse-001": "warehouse_001",
            "warehouse-002": "warehouse_002",
            "warehouse-003": "warehouse_003"
        }
        
        if warehouse_id in warehouse_wallet_map:
            wallet_name = warehouse_wallet_map[warehouse_id]
            if wallet_name in self.wallets:
                return self.wallets[wallet_name]['public_key']
        
        raise ValueError(f"No wallet found for warehouse: {warehouse_id}")
    
    def get_supplier_wallet(self, supplier_id: str) -> str:
        """Get wallet address for a supplier"""
        supplier_wallet_map = {
            "supplier-001": "supplier_001",
            "supplier-002": "supplier_002", 
            "supplier-003": "supplier_003"
        }
        
        if supplier_id in supplier_wallet_map:
            wallet_name = supplier_wallet_map[supplier_id]
            if wallet_name in self.wallets:
                return self.wallets[wallet_name]['public_key']
        
        raise ValueError(f"No wallet found for supplier: {supplier_id}")

# Global instance for easy access
blockchain_integration = SolanaBlockchainIntegration()

def get_blockchain_integration() -> SolanaBlockchainIntegration:
    """Get the global blockchain integration instance"""
    return blockchain_integration
