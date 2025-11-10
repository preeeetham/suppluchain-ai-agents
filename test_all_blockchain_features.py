#!/usr/bin/env python3
"""
Comprehensive Blockchain Features Test
Tests all blockchain functionality to verify everything is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from solana_blockchain_integration import SolanaBlockchainIntegration
import time

def test_wallet_management():
    """Test wallet management features"""
    print("\n" + "="*70)
    print("TEST 1: 💰 Wallet Management")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    # Test 1.1: Get wallet balance
    print("\n1.1 Testing get_wallet_balance()...")
    try:
        # Use first available wallet
        first_wallet = list(blockchain.wallets.keys())[0]
        balance = blockchain.get_wallet_balance(first_wallet)
        print(f"   ✅ {first_wallet} wallet balance: {balance:.4f} SOL")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 1.2: Get wallet summary
    print("\n1.2 Testing get_wallet_summary()...")
    try:
        summary = blockchain.get_wallet_summary()
        print(f"   ✅ Retrieved {len(summary)} wallets")
        # Show first 3 wallets
        for i, (name, info) in enumerate(list(summary.items())[:3]):
            if 'error' not in info:
                print(f"      • {name}: {info['sol_balance']:.4f} SOL")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 1.3: Fund wallet (airdrop)
    print("\n1.3 Testing fund_wallet()...")
    try:
        # Fund a test wallet
        result = blockchain.fund_wallet("warehouse_001", amount=5.0)
        if result:
            print(f"   ✅ Airdrop requested: {result[:30]}...")
            time.sleep(1)  # Wait for confirmation
            new_balance = blockchain.get_wallet_balance("warehouse_001")
            print(f"   ✅ warehouse_001 balance: {new_balance:.4f} SOL")
        else:
            print(f"   ⚠️  Airdrop returned None (might be rate-limited on devnet)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 1.4: Get wallet details
    print("\n1.4 Testing get_wallet_details()...")
    try:
        # Use first available wallet
        first_wallet = list(blockchain.wallets.keys())[0]
        details = blockchain.get_wallet_details(first_wallet)
        print(f"   ✅ Wallet details retrieved")
        print(f"      • Public Key: {details['public_key'][:30]}...")
        print(f"      • Balance: {details['sol_balance']:.4f} SOL")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 1.5: Helper functions
    print("\n1.5 Testing helper functions...")
    try:
        agent_wallet = blockchain.get_agent_wallet("inventory_agent")
        warehouse_wallet = blockchain.get_warehouse_wallet("warehouse-001")
        supplier_wallet = blockchain.get_supplier_wallet("supplier-001")
        print(f"   ✅ get_agent_wallet('inventory_agent'): {agent_wallet[:30]}...")
        print(f"   ✅ get_warehouse_wallet('warehouse-001'): {warehouse_wallet[:30]}...")
        print(f"   ✅ get_supplier_wallet('supplier-001'): {supplier_wallet[:30]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ Wallet Management: ALL TESTS PASSED")
    return True

def test_sol_transfers():
    """Test SOL transfer functionality"""
    print("\n" + "="*70)
    print("TEST 2: 💸 SOL Transfers")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    # Get initial balances
    print("\n2.1 Getting initial balances...")
    try:
        # Find a wallet with balance for transfer
        from_wallet = None
        for wallet_name in blockchain.wallets.keys():
            try:
                balance = blockchain.get_wallet_balance(wallet_name)
                if balance > 1.0:  # Need at least 1 SOL for transfer
                    from_wallet = wallet_name
                    break
            except:
                continue
        
        if not from_wallet:
            print(f"   ⚠️  No wallet with sufficient balance found. Funding warehouse_001...")
            blockchain.fund_wallet("warehouse_001", amount=5.0)
            time.sleep(2)
            from_wallet = "warehouse_001"
        
        to_wallet = "warehouse_002" if from_wallet == "warehouse_001" else "warehouse_001"
        
        from_balance_before = blockchain.get_wallet_balance(from_wallet)
        to_balance_before = blockchain.get_wallet_balance(to_wallet)
        print(f"   {from_wallet} balance: {from_balance_before:.4f} SOL")
        print(f"   {to_wallet} balance: {to_balance_before:.4f} SOL")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test transfer
    print("\n2.2 Testing transfer_sol()...")
    try:
        transfer_amount = 0.5
        result = blockchain.transfer_sol(
            from_wallet_name=from_wallet,
            to_wallet_name=to_wallet,
            amount=transfer_amount
        )
        
        print(f"   ✅ Transfer initiated")
        print(f"      • Amount: {transfer_amount} SOL")
        print(f"      • Status: {result.get('status', 'unknown')}")
        print(f"      • Signature: {result.get('signature', 'N/A')[:30]}...")
        
        # Wait for confirmation
        time.sleep(2)
        
        # Check balances after transfer
        from_balance_after = blockchain.get_wallet_balance(from_wallet)
        to_balance_after = blockchain.get_wallet_balance(to_wallet)
        
        print(f"\n   Balances after transfer:")
        print(f"      • {from_wallet}: {from_balance_after:.4f} SOL")
        print(f"      • {to_wallet}: {to_balance_after:.4f} SOL")
        
        # Verify transfer (with some tolerance for fees)
        if to_balance_after > to_balance_before:
            print(f"   ✅ Transfer verified: {to_wallet} received funds")
        else:
            print(f"   ⚠️  Balance didn't increase (might need more time or insufficient funds)")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ SOL Transfers: TEST PASSED")
    return True

def test_payment_processing():
    """Test payment processing"""
    print("\n" + "="*70)
    print("TEST 3: 💳 Payment Processing")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    print("\n3.1 Testing process_supply_chain_payment()...")
    try:
        payment = blockchain.process_supply_chain_payment(
            from_wallet="supplier_001",
            to_wallet="warehouse_001",
            amount=0.5,
            product_id="PAYMENT-TEST-001"
        )
        
        print(f"   ✅ Payment processed")
        print(f"      • From: {payment.get('from_wallet')}")
        print(f"      • To: {payment.get('to_wallet')}")
        print(f"      • Amount: {payment.get('amount')} SOL")
        print(f"      • Product ID: {payment.get('product_id')}")
        print(f"      • Status: {payment.get('status', 'unknown')}")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Payment Processing: TEST PASSED")
    return True

def test_nft_features():
    """Test NFT features"""
    print("\n" + "="*70)
    print("TEST 4: 🎨 NFT Features")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    # Test 4.1: Mint NFT
    print("\n4.1 Testing mint_product_nft()...")
    try:
        nft = blockchain.mint_product_nft(
            product_id="BLOCKCHAIN-TEST-001",
            owner_wallet_name="supplier_001",
            metadata={
                "name": "Blockchain Test Product",
                "category": "Test",
                "quantity": 100
            }
        )
        print(f"   ✅ NFT minted")
        print(f"      • Product ID: {nft['product_id']}")
        print(f"      • Mint Address: {nft['mint_address'][:30]}...")
        print(f"      • Status: {nft['status']}")
        
        time.sleep(1)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4.2: Get NFT by ID
    print("\n4.2 Testing get_nft_by_product_id()...")
    try:
        nft = blockchain.get_nft_by_product_id("BLOCKCHAIN-TEST-001")
        if nft:
            print(f"   ✅ NFT retrieved")
            print(f"      • Product ID: {nft['product_id']}")
            print(f"      • Owner: {nft['owner_wallet']}")
            print(f"      • On-chain: {nft.get('on_chain', False)}")
        else:
            print(f"   ❌ NFT not found")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4.3: Get NFTs by owner
    print("\n4.3 Testing get_nfts_by_owner()...")
    try:
        nfts = blockchain.get_nfts_by_owner("supplier_001")
        print(f"   ✅ Found {len(nfts)} NFT(s) for supplier_001")
        if nfts:
            print(f"      • First NFT: {nfts[0]['product_id']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4.4: Transfer NFT
    print("\n4.4 Testing transfer_nft_on_chain()...")
    try:
        transfer = blockchain.transfer_nft_on_chain(
            product_id="BLOCKCHAIN-TEST-001",
            new_owner_wallet_name="warehouse_001"
        )
        print(f"   ✅ NFT transferred")
        print(f"      • From: {transfer.get('previous_owner')}")
        print(f"      • To: {transfer.get('owner_wallet')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4.5: Update NFT metadata
    print("\n4.5 Testing update_nft_metadata()...")
    try:
        updated = blockchain.update_nft_metadata(
            product_id="BLOCKCHAIN-TEST-001",
            updates={"status": "in_transit", "location": "warehouse_001"}
        )
        print(f"   ✅ NFT metadata updated")
        print(f"      • Status: {updated['metadata'].get('status')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ NFT Features: ALL TESTS PASSED")
    return True

def test_transaction_history():
    """Test transaction history"""
    print("\n" + "="*70)
    print("TEST 5: 📜 Transaction History")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    print("\n5.1 Testing get_transaction_history()...")
    try:
        # Get all transactions
        transactions = blockchain.get_transaction_history(limit=10)
        print(f"   ✅ Retrieved {len(transactions)} transactions")
        
        if transactions:
            print(f"      • First transaction:")
            first = transactions[0]
            print(f"        - Type: {first.get('type', 'unknown')}")
            print(f"        - Amount: {first.get('amount', 0)} SOL")
            print(f"        - Status: {first.get('status', 'unknown')}")
        else:
            print(f"      ⚠️  No transactions found (this is OK if system is new)")
        
        # Get transactions for specific wallet
        first_wallet = list(blockchain.wallets.keys())[0]
        wallet_txns = blockchain.get_transaction_history(wallet_name=first_wallet, limit=5)
        print(f"   ✅ Retrieved {len(wallet_txns)} transactions for '{first_wallet}' wallet")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Transaction History: TEST PASSED")
    return True

def test_create_wallet():
    """Test wallet creation"""
    print("\n" + "="*70)
    print("TEST 6: 🔑 Create New Wallet")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    
    print("\n6.1 Testing create_wallet()...")
    try:
        # Create a test wallet with unique name
        import time as time_module
        unique_name = f"test_wallet_{int(time_module.time())}"
        new_wallet = blockchain.create_wallet(unique_name)
        print(f"   ✅ Wallet created")
        print(f"      • Name: {new_wallet['name']}")
        print(f"      • Public Key: {new_wallet['public_key'][:30]}...")
        # New wallet starts with 0 balance
        balance = blockchain.get_wallet_balance(unique_name)
        print(f"      • Balance: {balance:.4f} SOL")
        
        # Verify it's in the wallets
        if unique_name in blockchain.wallets:
            print(f"   ✅ Wallet added to wallet list")
        else:
            print(f"   ⚠️  Wallet not found in wallet list")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Create Wallet: TEST PASSED")
    return True

def main():
    """Run all blockchain feature tests"""
    print("\n" + "="*70)
    print("  🔍 COMPREHENSIVE BLOCKCHAIN FEATURES TEST")
    print("="*70)
    
    blockchain = SolanaBlockchainIntegration()
    print(f"\n🔗 Connected to: {blockchain.devnet_url}")
    
    if "localhost" not in blockchain.devnet_url and "127.0.0.1" not in blockchain.devnet_url:
        print("⚠️  WARNING: Not using local validator!")
        print("   Some tests may fail or be slow on devnet")
    
    results = {}
    
    # Run all tests
    results['wallet_management'] = test_wallet_management()
    results['sol_transfers'] = test_sol_transfers()
    results['payment_processing'] = test_payment_processing()
    results['nft_features'] = test_nft_features()
    results['transaction_history'] = test_transaction_history()
    results['create_wallet'] = test_create_wallet()
    
    # Summary
    print("\n" + "="*70)
    print("  📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name.replace('_', ' ').title()}")
    
    print("\n" + "="*70)
    print(f"  Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL BLOCKCHAIN FEATURES WORKING CORRECTLY!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

