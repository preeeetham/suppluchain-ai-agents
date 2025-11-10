"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Copy, Check } from "lucide-react"

interface CreateWalletModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function CreateWalletModal({ open, onOpenChange, onSuccess }: CreateWalletModalProps) {
  const [walletName, setWalletName] = useState("")
  const [loading, setLoading] = useState(false)
  const [createdWallet, setCreatedWallet] = useState<{ name: string; public_key: string } | null>(null)
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!walletName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a wallet name",
        variant: "destructive"
      })
      return
    }

    setLoading(true)
    try {
      const result = await apiClient.createWallet(walletName.trim())
      setCreatedWallet(result.wallet)
      toast({
        title: "Success",
        description: result.message
      })
      setWalletName("")
      onSuccess?.()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to create wallet",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const copyPublicKey = () => {
    if (createdWallet?.public_key) {
      navigator.clipboard.writeText(createdWallet.public_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      toast({
        title: "Copied",
        description: "Public key copied to clipboard"
      })
    }
  }

  const handleClose = () => {
    setCreatedWallet(null)
    setWalletName("")
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Wallet</DialogTitle>
          <DialogDescription>
            Create a new Solana wallet for your supply chain
          </DialogDescription>
        </DialogHeader>

        {!createdWallet ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="wallet-name">Wallet Name *</Label>
              <Input
                id="wallet-name"
                value={walletName}
                onChange={(e) => setWalletName(e.target.value)}
                placeholder="new_wallet_name"
                required
              />
              <p className="text-xs text-muted-foreground">
                Use lowercase letters, numbers, and underscores only
              </p>
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Wallet
              </Button>
            </div>
          </form>
        ) : (
          <div className="space-y-4">
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
              <p className="text-sm font-medium text-green-400 mb-2">Wallet Created Successfully!</p>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Wallet Name</p>
                  <p className="font-mono text-sm">{createdWallet.name}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Public Key</p>
                  <div className="flex items-center gap-2">
                    <p className="font-mono text-sm flex-1 break-all">{createdWallet.public_key}</p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={copyPublicKey}
                      className="h-8 w-8 p-0"
                    >
                      {copied ? (
                        <Check className="h-4 w-4 text-green-400" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleClose}>Close</Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

