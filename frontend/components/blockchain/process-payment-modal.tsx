"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

interface ProcessPaymentModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  wallets: Record<string, { public_key: string; sol_balance: number }>
  onSuccess?: () => void
}

export function ProcessPaymentModal({ open, onOpenChange, wallets, onSuccess }: ProcessPaymentModalProps) {
  const [fromWallet, setFromWallet] = useState("")
  const [toWallet, setToWallet] = useState("")
  const [amount, setAmount] = useState("")
  const [productId, setProductId] = useState("")
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!fromWallet || !toWallet || !amount) {
      toast({
        title: "Error",
        description: "Please fill in all required fields",
        variant: "destructive"
      })
      return
    }

    const amountNum = parseFloat(amount)
    if (isNaN(amountNum) || amountNum <= 0) {
      toast({
        title: "Error",
        description: "Please enter a valid amount",
        variant: "destructive"
      })
      return
    }

    setLoading(true)
    try {
      const result = await apiClient.processPayment(
        fromWallet, 
        toWallet, 
        amountNum, 
        productId || undefined
      )
      toast({
        title: "Success",
        description: result.message
      })
      setFromWallet("")
      setToWallet("")
      setAmount("")
      setProductId("")
      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to process payment",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const walletNames = Object.keys(wallets)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Process Payment</DialogTitle>
          <DialogDescription>
            Process a supply chain payment between wallets
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="from-wallet">From Wallet *</Label>
            <Select value={fromWallet} onValueChange={setFromWallet}>
              <SelectTrigger id="from-wallet">
                <SelectValue placeholder="Select source wallet" />
              </SelectTrigger>
              <SelectContent>
                {walletNames.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name} ({wallets[name]?.sol_balance.toFixed(4)} SOL)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="to-wallet">To Wallet *</Label>
            <Select value={toWallet} onValueChange={setToWallet}>
              <SelectTrigger id="to-wallet">
                <SelectValue placeholder="Select destination wallet" />
              </SelectTrigger>
              <SelectContent>
                {walletNames.filter(name => name !== fromWallet).map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="amount">Amount (SOL) *</Label>
            <Input
              id="amount"
              type="number"
              step="0.0001"
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.0"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="product-id">Product ID (Optional)</Label>
            <Input
              id="product-id"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              placeholder="PROD-001"
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Process Payment
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

