"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Blocks, Copy, ExternalLink, CheckCircle, Wallet, TrendingUp, Send, Plus, CreditCard, Coins, Image as ImageIcon, Shield } from "lucide-react"
import { useBlockchain } from "@/hooks/use-live-data"
import { formatDistanceToNow } from "date-fns"
import { useState, useEffect } from "react"
import { TransferSOLModal } from "@/components/blockchain/transfer-sol-modal"
import { TransferNFTModal } from "@/components/blockchain/transfer-nft-modal"
import { CreateNFTModal } from "@/components/blockchain/create-nft-modal"
import { ProcessPaymentModal } from "@/components/blockchain/process-payment-modal"
import { CreateWalletModal } from "@/components/blockchain/create-wallet-modal"
import { apiClient } from "@/lib/api"

export default function BlockchainPage() {
  const { blockchain, loading, error, refetch, refetchWithBalances } = useBlockchain()
  const [copiedHash, setCopiedHash] = useState<string | null>(null)
  const [transferModalOpen, setTransferModalOpen] = useState(false)
  const [transferNFTModalOpen, setTransferNFTModalOpen] = useState(false)
  const [createNFTModalOpen, setCreateNFTModalOpen] = useState(false)
  const [paymentModalOpen, setPaymentModalOpen] = useState(false)
  const [createWalletModalOpen, setCreateWalletModalOpen] = useState(false)
  const [nfts, setNfts] = useState<any[]>([])
  const [nftsLoading, setNftsLoading] = useState(false)

  const copyToClipboard = (text: string, txId: string) => {
    navigator.clipboard.writeText(text)
    setCopiedHash(txId)
    setTimeout(() => setCopiedHash(null), 2000)
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true })
    } catch {
      return timestamp
    }
  }

  const formatSolanaAddress = (address: string) => {
    if (!address) return "N/A"
    return `${address.slice(0, 4)}...${address.slice(-4)}`
  }

  const getSolanaExplorerUrl = (addressOrTx: string) => {
    // Use devnet explorer for Solana addresses
    return `https://explorer.solana.com/address/${addressOrTx}?cluster=devnet`
  }

  // Calculate stats from real data
  const blockchainStats = blockchain ? [
    { 
      label: "Total Transactions", 
      value: blockchain.total_transactions?.toLocaleString() || "0", 
      change: `+${blockchain.payments_processed || 0} processed` 
    },
    {
      label: "Network Status", 
      value: blockchain.network_status?.network_health || "Unknown", 
      change: blockchain.network_status?.rpc_url || "Not connected" 
    },
    { 
      label: "Main Wallet Balance", 
      value: `${blockchain.main_wallet_balance?.toFixed(4) || "0.0000"} SOL`, 
      change: blockchain.total_wallets ? `${blockchain.total_wallets} wallets` : "No wallets" 
    },
    { 
      label: "NFTs Created", 
      value: blockchain.nfts_created?.toLocaleString() || "0", 
      change: blockchain.nfts_created ? "Product tracking active" : "No NFTs yet" 
    },
  ] : [
    { label: "Total Transactions", value: "0", change: "Loading..." },
    { label: "Network Status", value: "Connecting...", change: "Checking..." },
    { label: "Main Wallet Balance", value: "0.0000 SOL", change: "Loading..." },
    { label: "NFTs Created", value: "0", change: "Loading..." },
  ]

  const transactions = blockchain?.transactions || []
  const networkStatus = blockchain?.network_status

  // Fetch NFTs for all wallets (with debounce to prevent excessive requests)
  useEffect(() => {
    const fetchNFTs = async () => {
      if (!blockchain?.wallets) return
      
      setNftsLoading(true)
      try {
        const allNFTs: any[] = []
        const walletNames = Object.keys(blockchain.wallets)
        
        // Limit to first 10 wallets to prevent too many requests
        const walletsToCheck = walletNames.slice(0, 10)
        
        // Fetch NFTs for each wallet with error handling
        const promises = walletsToCheck.map(async (walletName) => {
          try {
            const result = await apiClient.getNFTsByOwner(walletName)
            if (result.success && result.nfts) {
              return result.nfts
            }
            return []
          } catch (err) {
            // Skip wallets with errors - don't crash
            console.debug(`No NFTs found for wallet ${walletName}`)
            return []
          }
        })
        
        // Wait for all requests with timeout
        const results = await Promise.allSettled(promises)
        results.forEach((result) => {
          if (result.status === 'fulfilled') {
            allNFTs.push(...result.value)
          }
        })
        
        setNfts(allNFTs)
      } catch (err) {
        console.error('Error fetching NFTs:', err)
        // Don't crash - just set empty array
        setNfts([])
      } finally {
        setNftsLoading(false)
      }
    }

    if (blockchain && !loading) {
      // Add a small delay to debounce rapid refreshes
      const timeoutId = setTimeout(() => {
        fetchNFTs()
      }, 300)
      
      return () => clearTimeout(timeoutId)
    }
  }, [blockchain, loading])

  const handleRefreshBalances = async () => {
    try {
      await apiClient.refreshWalletBalances()
      await refetchWithBalances()
    } catch (error) {
      console.error("Error refreshing balances:", error)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 overflow-auto pt-16 p-6">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Refresh Button */}
            <div className="flex justify-end">
              <Button 
                onClick={handleRefreshBalances}
                variant="outline"
                className="gap-2"
              >
                <TrendingUp className="w-4 h-4" />
                Refresh Balances
              </Button>
            </div>
            {/* Header */}
            <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Blockchain Integration</h1>
                <p className="text-muted-foreground mt-1">
                  Real-time supply chain records on Solana network
                  {blockchain?.network_status?.rpc_url && (
                    <span className="ml-2 text-xs">({blockchain.network_status.rpc_url})</span>
                  )}
                </p>
              </div>
              {!loading && !error && blockchain && (
                <div className="flex gap-2">
                  <Button onClick={() => setTransferModalOpen(true)} variant="outline" size="sm">
                    <Coins className="w-4 h-4 mr-2" />
                    Transfer SOL
                  </Button>
                  <Button onClick={() => setTransferNFTModalOpen(true)} variant="outline" size="sm">
                    <Send className="w-4 h-4 mr-2" />
                    Transfer NFT
                  </Button>
                  <Button onClick={() => setCreateNFTModalOpen(true)} variant="outline" size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Create NFT
                  </Button>
                  <Button onClick={() => setPaymentModalOpen(true)} variant="outline" size="sm">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Process Payment
                  </Button>
                  <Button onClick={() => setCreateWalletModalOpen(true)} variant="outline" size="sm">
                    <Wallet className="w-4 h-4 mr-2" />
                    Create Wallet
                  </Button>
                </div>
              )}
            </div>

            {loading && (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Loading blockchain data...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <p className="text-red-400">Error loading blockchain data: {error.message}</p>
              </div>
            )}

            {!loading && !error && blockchain && (
              <>
            {/* Blockchain Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {blockchainStats.map((stat) => (
                <Card key={stat.label} className="bg-card border-border">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      <p className="text-2xl font-bold">{stat.value}</p>
                      <p className="text-xs text-green-400">{stat.change}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Network Status */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Blocks className="w-5 h-5 text-accent" />
                  Solana Network Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-muted/30 rounded-lg">
                        <p className="text-sm text-muted-foreground mb-2">Current Slot</p>
                        <p className="text-2xl font-bold font-mono">
                          {networkStatus?.current_slot?.toLocaleString() || "0"}
                        </p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Transactions/sec</p>
                        <p className="text-2xl font-bold">
                          {networkStatus?.transactions_per_second?.toLocaleString() || "4,200+"}
                        </p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Network Health</p>
                        <Badge className={
                          networkStatus?.network_health === "healthy" 
                            ? "bg-green-500/20 text-green-400" 
                            : "bg-yellow-500/20 text-yellow-400"
                        }>
                          {networkStatus?.network_health || "Unknown"}
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Wallet Information */}
                    {blockchain.wallets && Object.keys(blockchain.wallets).length > 0 && (
                      <div className="mt-4">
                        <p className="text-sm text-muted-foreground mb-3">Active Wallets ({blockchain.total_wallets})</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          {Object.entries(blockchain.wallets).slice(0, 6).map(([name, info]: [string, any]) => (
                            <div key={name} className="p-3 bg-muted/20 rounded-lg border border-border">
                              <div className="flex items-center gap-2 mb-1">
                                <Wallet className="w-4 h-4 text-muted-foreground" />
                                <p className="text-sm font-semibold">{name.replace('_', ' ')}</p>
                              </div>
                              <p className="text-xs text-muted-foreground font-mono mb-1">
                                {formatSolanaAddress(info.public_key || '')}
                              </p>
                              <p className="text-sm font-bold">
                                {info.sol_balance?.toFixed(4) || "0.0000"} SOL
                              </p>
                            </div>
                          ))}
                  </div>
                </div>
                    )}
              </CardContent>
            </Card>

            {/* Recent Transactions */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Recent Blockchain Transactions</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Real transactions from {blockchain.payments_processed || 0} payment records
                    </p>
              </CardHeader>
              <CardContent>
                    {transactions.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">
                        <p>No transactions yet. Transactions will appear here when agents process payments.</p>
                        <p className="text-xs mt-2">Transactions are created when:</p>
                        <ul className="text-xs mt-2 space-y-1">
                          <li>• Agents process supplier payments</li>
                          <li>• Product NFTs are created for inventory tracking</li>
                          <li>• Supply chain payments are executed</li>
                        </ul>
                      </div>
                    ) : (
                <div className="space-y-3">
                        {transactions.slice(0, 10).map((tx, index) => {
                          const txHash = tx.transaction_id || tx.signature || "unknown"
                          const isCopied = copiedHash === txHash
                          // Use index + txHash to ensure unique keys even if transactions have duplicate IDs
                          const uniqueKey = `${index}-${txHash}`
                          
                          return (
                            <div key={uniqueKey} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                                    <p className="font-semibold">
                                      {tx.type === 'supply_chain_payment' ? 'Supply Chain Payment' :
                                       tx.type === 'wallet_initialization' ? 'Wallet Initialization' :
                                       tx.type || 'Transaction'}
                                    </p>
                            <Badge
                              className={
                                tx.status === "confirmed"
                                  ? "bg-green-500/20 text-green-400"
                                  : "bg-yellow-500/20 text-yellow-400"
                              }
                            >
                              {tx.status === "confirmed" ? (
                                <>
                                  <CheckCircle className="w-3 h-3 mr-1" />
                                  Confirmed
                                </>
                              ) : (
                                "Pending"
                              )}
                            </Badge>
                                    {tx.blockchain_ready && (
                                      <Badge className="bg-blue-500/20 text-blue-400">Blockchain Ready</Badge>
                                    )}
                                  </div>
                                  
                                  <div className="space-y-1 text-sm text-muted-foreground">
                                    {tx.amount > 0 && (
                                      <p>Amount: <span className="font-semibold text-foreground">{tx.amount.toFixed(4)} SOL</span></p>
                                    )}
                                    {tx.from_wallet && tx.to_wallet && (
                                      <p>
                                        From: <span className="font-mono text-xs">{formatSolanaAddress(tx.from_wallet)}</span> → 
                                        To: <span className="font-mono text-xs">{formatSolanaAddress(tx.to_wallet)}</span>
                                      </p>
                                    )}
                                    {tx.product_id && (
                                      <p>Product: <span className="font-semibold">{tx.product_id}</span></p>
                                    )}
                          </div>
                        </div>
                                <span className="text-xs text-muted-foreground">{formatTimestamp(tx.timestamp)}</span>
                      </div>

                      <div className="bg-muted/30 rounded p-3 mb-3">
                                <p className="text-xs text-muted-foreground mb-2">Transaction ID</p>
                        <div className="flex items-center gap-2">
                                  <code className="text-xs font-mono flex-1 truncate">{txHash}</code>
                                  <Button 
                                    size="sm" 
                                    variant="ghost" 
                                    className="h-6 w-6 p-0"
                                    onClick={() => copyToClipboard(txHash, txHash)}
                                  >
                                    <Copy className={`w-4 h-4 ${isCopied ? 'text-green-400' : ''}`} />
                          </Button>
                        </div>
                      </div>

                              {tx.from_wallet && (
                                <Button 
                                  size="sm" 
                                  variant="outline" 
                                  className="bg-transparent w-full"
                                  onClick={() => window.open(getSolanaExplorerUrl(tx.from_wallet!), '_blank')}
                                >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        View on Solana Explorer
                      </Button>
                              )}
                    </div>
                          )
                        })}
                </div>
                    )}
              </CardContent>
            </Card>

                {/* NFT Gallery */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="w-5 h-5 text-accent" />
                  Product NFTs (On-Chain)
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Real Solana NFTs tracking products in the supply chain
                </p>
              </CardHeader>
              <CardContent>
                {nftsLoading ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <p>Loading NFTs...</p>
                  </div>
                ) : nfts.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <ImageIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No NFTs created yet.</p>
                    <p className="text-xs mt-2">Create your first product NFT to start tracking on the blockchain.</p>
                    <Button 
                      onClick={() => setCreateNFTModalOpen(true)} 
                      variant="outline" 
                      size="sm"
                      className="mt-4"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Create NFT
                    </Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {nfts.map((nft, index) => {
                      const mintAddress = nft.mint_address || 'N/A'
                      const tokenAccount = nft.token_account || 'N/A'
                      const isOnChain = nft.on_chain || false
                      const isCopied = copiedHash === mintAddress
                      // Use index + product_id to ensure unique keys
                      const uniqueKey = `${index}-${nft.product_id}`
                      
                      return (
                        <div key={uniqueKey} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <p className="font-semibold">{nft.metadata?.name || nft.product_id}</p>
                                {isOnChain && (
                                  <Badge className="bg-green-500/20 text-green-400">
                                    <Shield className="w-3 h-3 mr-1" />
                                    On-Chain
                                  </Badge>
                                )}
                                {nft.status === 'confirmed' && (
                                  <Badge className="bg-blue-500/20 text-blue-400">
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    Confirmed
                                  </Badge>
                                )}
                              </div>
                              
                              <div className="space-y-2 text-sm">
                                <div>
                                  <p className="text-muted-foreground text-xs">Product ID</p>
                                  <p className="font-mono text-xs">{nft.product_id}</p>
                                </div>
                                
                                {nft.metadata && (
                                  <div>
                                    <p className="text-muted-foreground text-xs">Category</p>
                                    <p className="text-xs">{nft.metadata.category || 'N/A'}</p>
                                  </div>
                                )}
                                
                                <div>
                                  <p className="text-muted-foreground text-xs">Owner</p>
                                  <p className="text-xs">{nft.owner_wallet || 'N/A'}</p>
                                </div>
                                
                                {mintAddress !== 'N/A' && (
                                  <div>
                                    <p className="text-muted-foreground text-xs">Mint Address</p>
                                    <div className="flex items-center gap-2">
                                      <code className="text-xs font-mono flex-1 truncate">{mintAddress}</code>
                                      <Button 
                                        size="sm" 
                                        variant="ghost" 
                                        className="h-6 w-6 p-0"
                                        onClick={() => copyToClipboard(mintAddress, mintAddress)}
                                      >
                                        <Copy className={`w-3 h-3 ${isCopied ? 'text-green-400' : ''}`} />
                                      </Button>
                                    </div>
                                  </div>
                                )}
                                
                                {tokenAccount !== 'N/A' && (
                                  <div>
                                    <p className="text-muted-foreground text-xs">Token Account</p>
                                    <p className="font-mono text-xs truncate">{formatSolanaAddress(tokenAccount)}</p>
                                  </div>
                                )}
                                
                                {nft.transaction_signature && (
                                  <div>
                                    <p className="text-muted-foreground text-xs">Transaction</p>
                                    <p className="font-mono text-xs truncate">{formatSolanaAddress(nft.transaction_signature)}</p>
                                  </div>
                                )}
                                
                                {nft.created_at && (
                                  <div>
                                    <p className="text-muted-foreground text-xs">Created</p>
                                    <p className="text-xs">{formatTimestamp(nft.created_at)}</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {mintAddress !== 'N/A' && (
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="bg-transparent w-full mt-3"
                              onClick={() => window.open(getSolanaExplorerUrl(mintAddress), '_blank')}
                            >
                              <ExternalLink className="w-4 h-4 mr-2" />
                              View on Solana Explorer
                            </Button>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Wallet Summary */}
                {blockchain.wallets && Object.keys(blockchain.wallets).length > 0 && (
            <Card className="bg-card border-border">
              <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Wallet className="w-5 h-5 text-accent" />
                        Wallet Summary
                      </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                        {Object.entries(blockchain.wallets).map(([name, info]: [string, any]) => (
                          <div key={name} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                              <p className="font-semibold">{name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</p>
                              <Badge className="bg-green-500/20 text-green-400">
                                {info.sol_balance?.toFixed(4) || "0.0000"} SOL
                              </Badge>
                      </div>
                            <div className="grid grid-cols-1 gap-2 text-sm">
                        <div>
                                <p className="text-muted-foreground">Public Address</p>
                                <p className="font-mono text-xs break-all">{info.public_key || 'N/A'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
                )}
              </>
            )}

            {/* Interactive Modals */}
            {blockchain && (
              <>
                <TransferSOLModal
                  open={transferModalOpen}
                  onOpenChange={setTransferModalOpen}
                  wallets={blockchain.wallets || {}}
                  onSuccess={async () => {
                    // Refresh balances immediately
                    await apiClient.refreshWalletBalances()
                    // Then fetch fresh data with balance refresh
                    setTimeout(() => {
                      refetchWithBalances?.()
                    }, 1000)
                    // Also refresh again after transaction confirms
                    setTimeout(() => {
                      refetchWithBalances?.()
                    }, 3000)
                  }}
                />
                <TransferNFTModal
                  open={transferNFTModalOpen}
                  onOpenChange={setTransferNFTModalOpen}
                  wallets={blockchain.wallets || {}}
                  nfts={nfts}
                  onSuccess={() => {
                    // Immediate refresh
                    refetch?.()
                    // Refresh NFTs after transfer
                    setTimeout(() => {
                      const fetchNFTs = async () => {
                        if (!blockchain?.wallets) return
                        const allNFTs: any[] = []
                        const walletNames = Object.keys(blockchain.wallets).slice(0, 10)
                        const promises = walletNames.map(async (walletName) => {
                          try {
                            const result = await apiClient.getNFTsByOwner(walletName)
                            if (result.success && result.nfts) {
                              return result.nfts
                            }
                            return []
                          } catch {
                            return []
                          }
                        })
                        const results = await Promise.allSettled(promises)
                        results.forEach((result) => {
                          if (result.status === 'fulfilled') {
                            allNFTs.push(...result.value)
                          }
                        })
                        setNfts(allNFTs)
                      }
                      fetchNFTs()
                    }, 2000)
                  }}
                />
                <CreateNFTModal
                  open={createNFTModalOpen}
                  onOpenChange={setCreateNFTModalOpen}
                  wallets={blockchain.wallets || {}}
                  onSuccess={() => {
                    // Immediate refresh
                    refetch?.()
                    // Refresh NFTs
                    setNftsLoading(true)
                    // Also refresh after a short delay to ensure backend has updated
                    setTimeout(() => {
                      refetch?.()
                      setNftsLoading(false)
                    }, 500)
                    setTimeout(() => {
                      refetch?.()
                      setNftsLoading(false)
                    }, 1500)
                  }}
                />
                <ProcessPaymentModal
                  open={paymentModalOpen}
                  onOpenChange={setPaymentModalOpen}
                  wallets={blockchain.wallets || {}}
                  onSuccess={() => {
                    // Immediate refresh
                    refetch?.()
                    // Also refresh after a short delay to ensure backend has updated
                    setTimeout(() => refetch?.(), 500)
                    setTimeout(() => refetch?.(), 1500)
                  }}
                />
                <CreateWalletModal
                  open={createWalletModalOpen}
                  onOpenChange={setCreateWalletModalOpen}
                  onSuccess={() => {
                    // Immediate refresh
                    refetch?.()
                    // Also refresh after a short delay to ensure backend has updated
                    setTimeout(() => refetch?.(), 500)
                    setTimeout(() => refetch?.(), 1500)
                  }}
                />
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
