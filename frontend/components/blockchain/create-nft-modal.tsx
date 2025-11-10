"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

interface CreateNFTModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  wallets: Record<string, { public_key: string; sol_balance: number }>
  onSuccess?: () => void
}

export function CreateNFTModal({ open, onOpenChange, wallets, onSuccess }: CreateNFTModalProps) {
  const [productId, setProductId] = useState("")
  const [warehouseWallet, setWarehouseWallet] = useState("")
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [category, setCategory] = useState("")
  const [quantity, setQuantity] = useState("")
  const [unitPrice, setUnitPrice] = useState("")
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const warehouseWallets = Object.keys(wallets).filter(name => 
    name.startsWith("warehouse_") || name.startsWith("warehouse-")
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!productId || !warehouseWallet || !name || !category) {
      toast({
        title: "Error",
        description: "Please fill in required fields",
        variant: "destructive"
      })
      return
    }

    setLoading(true)
    try {
      const metadata: Record<string, any> = {
        name,
        description: description || undefined,
        category,
      }

      if (quantity) {
        metadata.quantity = parseInt(quantity)
      }
      if (unitPrice) {
        metadata.unit_price = parseFloat(unitPrice)
      }

      const result = await apiClient.createNFT(productId, warehouseWallet, metadata)
      toast({
        title: "Success",
        description: result.message
      })
      
      // Reset form
      setProductId("")
      setWarehouseWallet("")
      setName("")
      setDescription("")
      setCategory("")
      setQuantity("")
      setUnitPrice("")
      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to create NFT",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Product NFT</DialogTitle>
          <DialogDescription>
            Create a blockchain NFT to track a product in the supply chain
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="product-id">Product ID *</Label>
            <Input
              id="product-id"
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              placeholder="PROD-001"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="warehouse">Warehouse Wallet *</Label>
            <Select value={warehouseWallet} onValueChange={setWarehouseWallet}>
              <SelectTrigger id="warehouse">
                <SelectValue placeholder="Select warehouse wallet" />
              </SelectTrigger>
              <SelectContent>
                {warehouseWallets.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Product Name *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Product Name"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Product description"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category *</Label>
              <Input
                id="category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="Electronics"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                placeholder="100"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="unit-price">Unit Price</Label>
            <Input
              id="unit-price"
              type="number"
              step="0.01"
              value={unitPrice}
              onChange={(e) => setUnitPrice(e.target.value)}
              placeholder="25.50"
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create NFT
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}

