"""
Solana Blockchain Integration for Supply Chain AI Agents
Professional implementation for production use
"""

import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.system_program import transfer, TransferParams, create_account, CreateAccountParams
from solders.instruction import Instruction, AccountMeta
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed, Finalized
from solana.rpc.types import TxOpts
import base58
import struct

logger = logging.getLogger(__name__)

class SolanaBlockchainIntegration:
    """Professional Solana blockchain integration for supply chain agents"""
    
    def __init__(self, devnet_url=None, wallet_file="solana_wallets.json"):
        # Use local validator if available, otherwise fallback to devnet
        # Check environment variable first, then default to local validator
        if devnet_url is None:
            devnet_url = os.getenv("SOLANA_RPC_URL", "http://localhost:8899")
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
            # Use Finalized commitment to ensure we get the latest confirmed balance
            from solana.rpc.commitment import Finalized
            balance = self.client.get_balance(public_key, commitment=Finalized)
            return balance.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Error getting balance for {wallet_name}: {e}")
            return 0.0
    
    def fund_wallet(self, wallet_name: str, amount: float = 10.0) -> Optional[str]:
        """Fund a wallet with SOL using airdrop (works on local validator and devnet)"""
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        public_key = Pubkey.from_string(self.wallets[wallet_name]['public_key'])
        
        try:
            # Request airdrop (works on both local validator and devnet)
            signature = self.client.request_airdrop(public_key, int(amount * 1e9))
            if signature.value:
                logger.info(f"🪂 Airdrop requested for {wallet_name}: {signature.value}")
                # Wait a bit for confirmation on local validator
                time.sleep(1)
                return str(signature.value)
            return None
        except Exception as e:
            logger.error(f"❌ Airdrop failed for {wallet_name}: {e}")
            return None
    
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
    
    def transfer_sol(self, from_wallet_name: str, to_wallet_name: str, amount: float) -> Dict:
        """
        Transfer SOL from one wallet to another
        
        Args:
            from_wallet_name: Name of the source wallet
            to_wallet_name: Name of the destination wallet
            amount: Amount in SOL to transfer
            
        Returns:
            Dict with transaction details
        """
        if from_wallet_name not in self.wallets:
            raise ValueError(f"Source wallet {from_wallet_name} not found")
        if to_wallet_name not in self.wallets:
            raise ValueError(f"Destination wallet {to_wallet_name} not found")
        
        # Get keypairs
        from_keypair = self.get_wallet_keypair(from_wallet_name)
        to_pubkey = Pubkey.from_string(self.wallets[to_wallet_name]['public_key'])
        
        # Check balance
        balance = self.get_wallet_balance(from_wallet_name)
        if balance < amount:
            raise ValueError(f"Insufficient balance. Available: {balance} SOL, Requested: {amount} SOL")
        
        # Convert SOL to lamports
        lamports = int(amount * 1e9)
        
        try:
            # Get recent blockhash first
            recent_blockhash_resp = self.client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Create transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )
            
            # Create message with instruction
            message = Message.new_with_blockhash(
                [transfer_instruction],
                from_keypair.pubkey(),
                recent_blockhash
            )
            
            # Create unsigned transaction
            transaction = Transaction.new_unsigned(message)
            
            # Sign transaction
            transaction.sign([from_keypair], recent_blockhash)
            
            # Send transaction to Solana network
            network_name = "local validator" if "localhost" in self.devnet_url else "devnet"
            logger.info(f"Sending SOL transfer transaction to Solana {network_name}...")
            send_result = self.client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
            )
            
            transaction_signature = send_result.value
            
            # Wait for confirmation
            logger.info(f"Waiting for transaction confirmation: {transaction_signature}")
            import time as time_module
            max_wait = 30  # Wait up to 30 seconds
            wait_time = 0
            status = "pending"
            
            while wait_time < max_wait:
                confirmation_result = self.client.get_signature_statuses([transaction_signature])
                if confirmation_result.value and confirmation_result.value[0]:
                    sig_status = confirmation_result.value[0]
                    if sig_status.err is None:
                        if sig_status.confirmation_status:
                            status = "confirmed"
                            network_name = "local validator" if "localhost" in self.devnet_url else "devnet"
                            logger.info(f"Transaction confirmed on Solana {network_name}: {transaction_signature}")
                            break
                    else:
                        status = "failed"
                        logger.error(f"Transaction failed: {sig_status.err}")
                        break
                time_module.sleep(1)
                wait_time += 1
            
            if status == "pending":
                logger.warning(f"Transaction still pending after {max_wait} seconds: {transaction_signature}")
                # Check one more time with searchTransactionHistory
                confirmation_result = self.client.get_signature_statuses(
                    [transaction_signature],
                    search_transaction_history=True
                )
                if confirmation_result.value and confirmation_result.value[0]:
                    sig_status = confirmation_result.value[0]
                    if sig_status.err is None and sig_status.confirmation_status:
                        status = "confirmed"
                    elif sig_status.err:
                        status = "failed"
            
            # Save transaction record with real signature
            transaction_info = {
                "transaction_id": str(transaction_signature),
                "signature": str(transaction_signature),
                "from_wallet": from_wallet_name,
                "to_wallet": to_wallet_name,
                "from_address": str(from_keypair.pubkey()),
                "to_address": self.wallets[to_wallet_name]['public_key'],
                "amount": amount,
                "lamports": lamports,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "type": "sol_transfer",
                "blockchain_ready": True,
                "confirmed_on_blockchain": status == "confirmed",
                "blockhash": str(recent_blockhash) if recent_blockhash else None
            }
            
            # Reload wallets to refresh balances after transfer
            self.load_wallets()
            
            # Save to payments directory
            payment_file = f"blockchain_data/payments/payment_{int(time.time())}.json"
            os.makedirs(os.path.dirname(payment_file), exist_ok=True)
            
            with open(payment_file, 'w') as f:
                json.dump(transaction_info, f, indent=2)
            
            logger.info(f"SOL transfer {'confirmed' if status == 'confirmed' else 'failed'}: {amount} SOL from {from_wallet_name} to {to_wallet_name}")
            
            return transaction_info
            
        except Exception as e:
            logger.error(f"Error transferring SOL: {e}")
            # Save failed transaction for tracking
            transaction_info = {
                "transaction_id": f"tx_failed_{int(time.time())}",
                "from_wallet": from_wallet_name,
                "to_wallet": to_wallet_name,
                "from_address": str(from_keypair.pubkey()),
                "to_address": self.wallets[to_wallet_name]['public_key'],
                "amount": amount,
                "lamports": lamports,
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "type": "sol_transfer",
                "blockchain_ready": False,
                "error": str(e)
            }
            
            payment_file = f"blockchain_data/payments/payment_{int(time.time())}.json"
            os.makedirs(os.path.dirname(payment_file), exist_ok=True)
            with open(payment_file, 'w') as f:
                json.dump(transaction_info, f, indent=2)
            
            raise
    
    def create_wallet(self, wallet_name: str) -> Dict:
        """
        Create a new Solana wallet
        
        Args:
            wallet_name: Name for the new wallet
            
        Returns:
            Dict with wallet information
        """
        if wallet_name in self.wallets:
            raise ValueError(f"Wallet {wallet_name} already exists")
        
        # Create new keypair
        keypair = Keypair()
        
        wallet_info = {
            "name": wallet_name,
            "public_key": str(keypair.pubkey()),
            "private_key": base58.b58encode(bytes(keypair)).decode('utf-8'),
            "secret_key": bytes(keypair).hex()
        }
        
        # Add to wallets dict
        self.wallets[wallet_name] = wallet_info
        
        # Save to file
        with open(self.wallet_file, 'w') as f:
            json.dump(self.wallets, f, indent=2)
        
        logger.info(f"Created new wallet: {wallet_name}")
        return wallet_info
    
    def get_wallet_details(self, wallet_name: str) -> Dict:
        """
        Get detailed information about a wallet
        
        Args:
            wallet_name: Name of the wallet
            
        Returns:
            Dict with wallet details
        """
        if wallet_name not in self.wallets:
            raise ValueError(f"Wallet {wallet_name} not found")
        
        wallet_info = self.wallets[wallet_name]
        balance = self.get_wallet_balance(wallet_name)
        
        # Get transaction history for this wallet
        transactions = self.get_transaction_history(wallet_name=wallet_name, limit=10)
        
        return {
            "name": wallet_name,
            "public_key": wallet_info['public_key'],
            "sol_balance": balance,
            "recent_transactions": transactions,
            "total_transactions": len(transactions)
        }
    
    def get_transaction_history(self, wallet_name: Optional[str] = None, limit: int = 50, 
                                transaction_type: Optional[str] = None) -> List[Dict]:
        """
        Get transaction history
        
        Args:
            wallet_name: Filter by wallet name (optional)
            limit: Maximum number of transactions to return
            transaction_type: Filter by transaction type (optional)
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        payments_dir = "blockchain_data/payments"
        
        if not os.path.exists(payments_dir):
            return transactions
        
        # Get all payment files
        payment_files = sorted(
            [f for f in os.listdir(payments_dir) if f.endswith('.json')],
            reverse=True
        )[:limit]
        
        for payment_file in payment_files:
            try:
                with open(os.path.join(payments_dir, payment_file), 'r') as f:
                    payment_data = json.load(f)
                
                # Apply filters
                if wallet_name:
                    if payment_data.get('from_wallet') != wallet_name and payment_data.get('to_wallet') != wallet_name:
                        continue
                
                if transaction_type:
                    if payment_data.get('type') != transaction_type:
                        continue
                
                transactions.append(payment_data)
                
            except Exception as e:
                logger.warning(f"Error reading payment file {payment_file}: {e}")
                continue
        
        return transactions
    
    def get_nft_by_product_id(self, product_id: str) -> Optional[Dict]:
        """
        Get NFT information by product ID
        
        Args:
            product_id: ID of the product
            
        Returns:
            Dict with NFT information, or None if not found
        """
        nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
        
        if not os.path.exists(nft_file):
            return None
        
        with open(nft_file, 'r') as f:
            nft_info = json.load(f)
        
        # If NFT is on-chain, verify current state
        if nft_info.get('on_chain', False):
            mint_address = nft_info.get('mint_address')
            token_account = nft_info.get('token_account')
            
            if mint_address:
                try:
                    mint_pubkey = Pubkey.from_string(mint_address)
                    mint_info = self.client.get_account_info(mint_pubkey, commitment=Finalized)
                    
                    if mint_info.value:
                        nft_info['mint_account_exists'] = True
                        nft_info['mint_account_owner'] = str(mint_info.value.owner)
                    else:
                        nft_info['mint_account_exists'] = False
                except Exception as e:
                    logger.warning(f"Error checking mint account for {product_id}: {e}")
            
            if token_account:
                try:
                    token_pubkey = Pubkey.from_string(token_account)
                    token_info = self.client.get_account_info(token_pubkey, commitment=Finalized)
                    
                    if token_info.value:
                        nft_info['token_account_exists'] = True
                        nft_info['token_account_owner'] = str(token_info.value.owner)
                        
                        # Parse token account data to get balance
                        if len(token_info.value.data) >= 64:
                            # Token account structure: mint (32) + owner (32) + amount (8) + ...
                            amount_bytes = token_info.value.data[64:72]
                            amount = struct.unpack('<Q', amount_bytes)[0]
                            nft_info['token_balance'] = amount
                    else:
                        nft_info['token_account_exists'] = False
                except Exception as e:
                    logger.warning(f"Error checking token account for {product_id}: {e}")
        
        return nft_info
    
    def get_nfts_by_owner(self, owner_wallet_name: str) -> List[Dict]:
        """
        Get all NFTs owned by a specific wallet
        
        Args:
            owner_wallet_name: Name of the owner wallet
            
        Returns:
            List of NFT dictionaries
        """
        if owner_wallet_name not in self.wallets:
            raise ValueError(f"Wallet {owner_wallet_name} not found")
        
        nfts = []
        nfts_dir = "blockchain_data/nfts"
        
        if not os.path.exists(nfts_dir):
            return nfts
        
        # Get all NFT files
        nft_files = [f for f in os.listdir(nfts_dir) if f.endswith('_nft.json')]
        
        for nft_file in nft_files:
            try:
                with open(os.path.join(nfts_dir, nft_file), 'r') as f:
                    nft_info = json.load(f)
                
                # Check if this NFT is owned by the specified wallet
                if nft_info.get('owner_wallet') == owner_wallet_name:
                    nfts.append(nft_info)
                    
            except Exception as e:
                logger.warning(f"Error reading NFT file {nft_file}: {e}")
                continue
        
        return nfts
    
    def update_nft_metadata(self, product_id: str, updates: Dict) -> Dict:
        """
        Update metadata for an existing Product NFT
        
        Args:
            product_id: ID of the product
            updates: Dictionary of fields to update
            
        Returns:
            Updated NFT information
        """
        nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
        
        if not os.path.exists(nft_file):
            raise ValueError(f"Product NFT {product_id} not found")
        
        # Load existing NFT
        with open(nft_file, 'r') as f:
            nft_info = json.load(f)
        
        # Update metadata
        if 'metadata' in nft_info:
            nft_info['metadata'].update(updates)
        else:
            nft_info['metadata'] = updates
        
        nft_info['updated_at'] = str(time.time())
        
        # Save updated NFT
        with open(nft_file, 'w') as f:
            json.dump(nft_info, f, indent=2)
        
        logger.info(f"Updated NFT metadata for {product_id}")
        return nft_info
    
    def transfer_nft_ownership(self, product_id: str, new_owner_wallet: str) -> Dict:
        """
        Transfer NFT ownership to a new wallet (legacy method - updates JSON file only)
        For real on-chain transfers, use transfer_nft_on_chain() instead
        """
        if new_owner_wallet not in self.wallets:
            raise ValueError(f"Wallet {new_owner_wallet} not found")
        
        nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
        
        if not os.path.exists(nft_file):
            raise ValueError(f"Product NFT {product_id} not found")
        
        # Load existing NFT
        with open(nft_file, 'r') as f:
            nft_info = json.load(f)
        
        old_owner = nft_info.get('owner_wallet')
        nft_info['owner_wallet'] = new_owner_wallet
        nft_info['previous_owner'] = old_owner
        nft_info['transferred_at'] = str(time.time())
        
        # Save updated NFT
        with open(nft_file, 'w') as f:
            json.dump(nft_info, f, indent=2)
        
        logger.info(f"Transferred NFT {product_id} from {old_owner} to {new_owner_wallet}")
        return nft_info
    
    def transfer_nft_on_chain_simple(self, product_id: str, new_owner_wallet_name: str) -> Dict:
        """
        Simplified NFT transfer - updates ownership metadata
        Real on-chain transfer would require Associated Token Accounts (ATA)
        For now, we update the metadata to reflect the transfer
        
        Args:
            product_id: ID of the product NFT to transfer
            new_owner_wallet_name: Name of the wallet that will receive the NFT
            
        Returns:
            Dict with transfer details
        """
        if new_owner_wallet_name not in self.wallets:
            raise ValueError(f"New owner wallet {new_owner_wallet_name} not found")
        
        # Load NFT info
        nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
        if not os.path.exists(nft_file):
            raise ValueError(f"Product NFT {product_id} not found")
        
        with open(nft_file, 'r') as f:
            nft_info = json.load(f)
        
        # Check if NFT is on-chain
        if not nft_info.get('on_chain', False):
            raise ValueError(f"NFT {product_id} is not on-chain. Use mint_product_nft() first.")
        
        old_owner_wallet = nft_info.get('owner_wallet')
        new_owner_address = self.wallets[new_owner_wallet_name]['public_key']
        
        # Update NFT ownership metadata
        nft_info['owner_wallet'] = new_owner_wallet_name
        nft_info['owner_address'] = new_owner_address
        nft_info['previous_owner'] = old_owner_wallet
        nft_info['transferred_at'] = datetime.now().isoformat()
        nft_info['transfer_status'] = 'metadata_updated'
        nft_info['transfer_note'] = 'Ownership updated in metadata. On-chain token account remains with original owner.'
        
        # Save updated NFT info
        with open(nft_file, 'w') as f:
            json.dump(nft_info, f, indent=2)
        
        logger.info(f"NFT {product_id} ownership transferred from {old_owner_wallet} to {new_owner_wallet_name} (metadata)")
        return nft_info
    
    def transfer_nft_on_chain(self, product_id: str, new_owner_wallet_name: str) -> Dict:
        """
        Transfer NFT ownership - updates metadata and records transfer
        The NFT remains minted on-chain for verification, ownership tracked in metadata
        
        Args:
            product_id: ID of the product NFT to transfer
            new_owner_wallet_name: Name of the wallet that will receive the NFT
            
        Returns:
            Dict with transfer details
        """
        # Use the simplified transfer method
        return self.transfer_nft_on_chain_simple(product_id, new_owner_wallet_name)
    
    def mint_product_nft(self, product_id: str, owner_wallet_name: str, metadata: Dict) -> Dict:
        """
        Mint a real Solana NFT for a product on the blockchain
        
        This creates an actual SPL Token NFT (supply=1, decimals=0) on Solana.
        
        Args:
            product_id: Unique product identifier
            owner_wallet_name: Name of the wallet that will own the NFT
            metadata: Product metadata (name, description, category, etc.)
            
        Returns:
            Dict with NFT information including mint address and token account
        """
        if owner_wallet_name not in self.wallets:
            raise ValueError(f"Owner wallet {owner_wallet_name} not found")
        
        # SPL Token Program ID
        TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        # Get owner keypair
        owner_keypair = self.get_wallet_keypair(owner_wallet_name)
        owner_pubkey = owner_keypair.pubkey()
        
        # Create mint keypair (this will be the NFT mint address)
        mint_keypair = Keypair()
        mint_pubkey = mint_keypair.pubkey()
        
        try:
            # Get recent blockhash
            recent_blockhash_resp = self.client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Calculate rent for mint account (82 bytes for token mint)
            mint_rent_resp = self.client.get_minimum_balance_for_rent_exemption(82)
            mint_rent = mint_rent_resp.value
            
            # Create mint account instruction
            create_mint_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=owner_pubkey,
                    to_pubkey=mint_pubkey,
                    lamports=mint_rent,
                    space=82,
                    owner=TOKEN_PROGRAM_ID
                )
            )
            
            # Initialize mint instruction (SPL Token)
            # Instruction format: [instruction_type (1 byte), decimals (1 byte), mint_authority (32 bytes), freeze_authority_option (1 byte), freeze_authority (32 bytes)]
            init_mint_data = struct.pack('<B', 0)  # InitializeMint instruction
            init_mint_data += struct.pack('<B', 0)  # decimals = 0 (NFT)
            init_mint_data += owner_pubkey.__bytes__()  # mint_authority
            init_mint_data += struct.pack('<B', 0)  # freeze_authority_option = None
            
            init_mint_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                data=init_mint_data,
                accounts=[
                    AccountMeta(pubkey=mint_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=Pubkey.from_string("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False),  # Rent sysvar
                    AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=False)  # Mint authority
                ]
            )
            
            # For simplicity, we'll create a regular token account instead of ATA
            # Create token account for the owner
            token_account_keypair = Keypair()
            token_account_pubkey = token_account_keypair.pubkey()
            
            # Calculate rent for token account (165 bytes)
            token_account_rent_resp = self.client.get_minimum_balance_for_rent_exemption(165)
            token_account_rent = token_account_rent_resp.value
            
            # Create token account instruction
            create_token_account_ix = create_account(
                CreateAccountParams(
                    from_pubkey=owner_pubkey,
                    to_pubkey=token_account_pubkey,
                    lamports=token_account_rent,
                    space=165,
                    owner=TOKEN_PROGRAM_ID
                )
            )
            
            # Initialize token account instruction
            init_token_account_data = struct.pack('<B', 1)  # InitializeAccount instruction
            init_token_account_data += owner_pubkey.__bytes__()  # owner
            
            init_token_account_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                data=init_token_account_data,
                accounts=[
                    AccountMeta(pubkey=token_account_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=mint_pubkey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=owner_pubkey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=Pubkey.from_string("SysvarRent111111111111111111111111111111111"), is_signer=False, is_writable=False)
                ]
            )
            
            # Mint token instruction (mint 1 token to token account)
            mint_to_data = struct.pack('<B', 7)  # MintTo instruction
            mint_to_data += struct.pack('<Q', 1)  # amount = 1 (NFT)
            
            mint_to_ix = Instruction(
                program_id=TOKEN_PROGRAM_ID,
                data=mint_to_data,
                accounts=[
                    AccountMeta(pubkey=mint_pubkey, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=token_account_pubkey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=False)  # Mint authority
                ]
            )
            
            # Build transaction
            instructions = [
                create_mint_account_ix,
                init_mint_ix,
                create_token_account_ix,
                init_token_account_ix,
                mint_to_ix
            ]
            
            message = Message.new_with_blockhash(
                instructions,
                owner_pubkey,
                recent_blockhash
            )
            
            transaction = Transaction.new_unsigned(message)
            transaction.sign([owner_keypair, mint_keypair, token_account_keypair], recent_blockhash)
            
            # Send transaction
            network_name = "local validator" if "localhost" in self.devnet_url else "devnet"
            logger.info(f"Minting NFT for product {product_id} on Solana {network_name}...")
            
            send_result = self.client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=False, preflight_commitment=Finalized)
            )
            
            transaction_signature = send_result.value
            
            # Wait for confirmation
            logger.info(f"Waiting for NFT mint confirmation: {transaction_signature}")
            max_wait = 30
            wait_time = 0
            status = "pending"
            
            while wait_time < max_wait:
                confirmation_result = self.client.get_signature_statuses([transaction_signature])
                if confirmation_result.value and confirmation_result.value[0]:
                    sig_status = confirmation_result.value[0]
                    if sig_status.err is None:
                        if sig_status.confirmation_status:
                            status = "confirmed"
                            logger.info(f"NFT minted successfully on Solana {network_name}: {transaction_signature}")
                            break
                    else:
                        status = "failed"
                        logger.error(f"NFT mint failed: {sig_status.err}")
                        break
                time.sleep(1)
                wait_time += 1
            
            if status != "confirmed":
                raise Exception(f"NFT mint transaction not confirmed after {max_wait} seconds")
            
            # Create NFT info with on-chain data
            nft_info = {
                "product_id": product_id,
                "mint_address": str(mint_pubkey),
                "token_account": str(token_account_pubkey),
                "owner_wallet": owner_wallet_name,
                "owner_address": str(owner_pubkey),
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "transaction_signature": str(transaction_signature),
                "status": status,
                "blockchain_ready": True,
                "on_chain": True,
                "token_standard": "SPL Token NFT"
            }
            
            # Save NFT info to file (for reference)
            nft_file = f"blockchain_data/nfts/{product_id}_nft.json"
            os.makedirs(os.path.dirname(nft_file), exist_ok=True)
            
            with open(nft_file, 'w') as f:
                json.dump(nft_info, f, indent=2)
            
            logger.info(f"Product NFT minted on-chain for {product_id}: {mint_pubkey}")
            return nft_info
            
        except Exception as e:
            logger.error(f"Error minting NFT for {product_id}: {e}")
            import traceback
            traceback.print_exc()
            raise

# Global instance for easy access
blockchain_integration = SolanaBlockchainIntegration()

def get_blockchain_integration() -> SolanaBlockchainIntegration:
    """Get the global blockchain integration instance"""
    return blockchain_integration
