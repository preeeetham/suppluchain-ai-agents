"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

interface TransferNFTModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  wallets: Record<string, { public_key: string; sol_balance: number }>
  nfts: any[]
  onSuccess?: () => void
}

export function TransferNFTModal({ open, onOpenChange, wallets, nfts, onSuccess }: TransferNFTModalProps) {
  const [productId, setProductId] = useState("")
  const [newOwnerWallet, setNewOwnerWallet] = useState("")
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  // Reset form when modal opens/closes
  useEffect(() => {
    if (!open) {
      setProductId("")
      setNewOwnerWallet("")
    }
  }, [open])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!productId || !newOwnerWallet) {
      toast({
        title: "Error",
        description: "Please fill in all fields",
        variant: "destructive"
      })
      return
    }

    setLoading(true)
    try {
      const result = await apiClient.transferNFTOwnership(productId, newOwnerWallet)
      
      if (result.success) {
        toast({
          title: "Success",
          description: `NFT ${productId} transferred to ${newOwnerWallet} successfully`,
        })
        onSuccess?.()
        onOpenChange(false)
      } else {
        toast({
          title: "Error",
          description: result.message || "Failed to transfer NFT",
          variant: "destructive"
        })
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to transfer NFT",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const walletOptions = Object.keys(wallets || {}).map(walletName => ({
    value: walletName,
    label: `${walletName} (${wallets[walletName]?.sol_balance?.toFixed(4) || "0.0000"} SOL)`
  }))

  const nftOptions = nfts.map(nft => ({
    value: nft.product_id,
    label: `${nft.product_id} - ${nft.metadata?.name || "Unnamed"} (Owner: ${nft.owner_wallet})`
  }))

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Transfer NFT Ownership</DialogTitle>
          <DialogDescription>
            Transfer a Product NFT to a new wallet owner on the Solana blockchain
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="product-id">Product ID *</Label>
            <Select value={productId} onValueChange={setProductId} required>
              <SelectTrigger id="product-id">
                <SelectValue placeholder="Select NFT to transfer" />
              </SelectTrigger>
              <SelectContent>
                {nftOptions.length > 0 ? (
                  nftOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))
                ) : (
                  <SelectItem value="" disabled>No NFTs available</SelectItem>
                )}
              </SelectContent>
            </Select>
            {nftOptions.length === 0 && (
              <p className="text-xs text-muted-foreground">
                No NFTs found. Create an NFT first.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="new-owner">New Owner Wallet *</Label>
            <Select value={newOwnerWallet} onValueChange={setNewOwnerWallet} required>
              <SelectTrigger id="new-owner">
                <SelectValue placeholder="Select destination wallet" />
              </SelectTrigger>
              <SelectContent>
                {walletOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !productId || !newOwnerWallet || nftOptions.length === 0}>
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Transfer NFT
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

