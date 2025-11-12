"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { CheckCircle, XCircle, Edit, Clock, AlertCircle } from "lucide-react"
import { apiClient } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface PendingApproval {
  id: string
  type: string
  agent_id: string
  title: string
  description: string
  details: Record<string, any>
  estimated_cost?: number
  created_at: string
  expires_at?: string
  status: string
}

export function ApprovalQueue() {
  const [approvals, setApprovals] = useState<PendingApproval[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null)
  const [modifyDialogOpen, setModifyDialogOpen] = useState(false)
  const [modifiedQuantity, setModifiedQuantity] = useState<number>(0)
  const { toast } = useToast()

  useEffect(() => {
    fetchApprovals()
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchApprovals, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchApprovals = async () => {
    try {
      const data = await apiClient.getPendingApprovals()
      // Ensure data is an array before filtering
      const approvalsArray = Array.isArray(data) ? data : []
      setApprovals(approvalsArray.filter((a: PendingApproval) => a.status === "pending"))
      setLoading(false)
    } catch (error) {
      console.error("Error fetching approvals:", error)
      setApprovals([]) // Set empty array on error
      setLoading(false)
    }
  }

  const handleApprovalAction = async (approvalId: string, action: "approve" | "reject", modifications?: Record<string, any>) => {
    try {
      await apiClient.processApprovalAction(approvalId, action, modifications)
      toast({
        title: "Success",
        description: `Approval ${action}d successfully`
      })
      fetchApprovals()
      setModifyDialogOpen(false)
      setSelectedApproval(null)
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || `Failed to ${action} approval`,
        variant: "destructive"
      })
    }
  }

  const handleModify = (approval: PendingApproval) => {
    setSelectedApproval(approval)
    setModifiedQuantity(approval.details.quantity || 0)
    setModifyDialogOpen(true)
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case "reorder": return "bg-blue-500/20 text-blue-400"
      case "supplier_selection": return "bg-purple-500/20 text-purple-400"
      case "route": return "bg-green-500/20 text-green-400"
      default: return "bg-gray-500/20 text-gray-400"
    }
  }

  const formatCost = (cost?: number) => {
    if (!cost) return "N/A"
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(cost)
  }

  if (loading) {
    return (
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Pending Approvals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">Loading approvals...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className="bg-card border-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Pending Approvals
            </CardTitle>
            <Badge variant="outline">{approvals.length} pending</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {approvals.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No pending approvals</p>
              <p className="text-sm mt-2">All agent actions are approved or auto-approved</p>
            </div>
          ) : (
            <div className="space-y-4">
              {approvals.map((approval, index) => (
                <div key={`${approval.id}-${index}`} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{approval.title}</h3>
                        <Badge className={getTypeColor(approval.type)}>
                          {approval.type}
                        </Badge>
                        {approval.estimated_cost && (
                          <Badge variant="outline" className="ml-2">
                            {formatCost(approval.estimated_cost)}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{approval.description}</p>
                      
                      {approval.type === "reorder" && (
                        <div className="text-sm space-y-1 mt-3 bg-muted/30 rounded p-3">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Product:</span>
                            <span className="font-medium">{approval.details.product_id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Warehouse:</span>
                            <span className="font-medium">{approval.details.warehouse_id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Quantity:</span>
                            <span className="font-medium">{approval.details.quantity} units</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Current Stock:</span>
                            <span className="font-medium">{approval.details.current_quantity} units</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Reorder Point:</span>
                            <span className="font-medium">{approval.details.reorder_point} units</span>
                          </div>
                        </div>
                      )}
                      
                      <div className="text-xs text-muted-foreground mt-3">
                        Created: {new Date(approval.created_at).toLocaleString()}
                        {approval.expires_at && (
                          <span className="ml-4">
                            Expires: {new Date(approval.expires_at).toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 mt-4">
                    <Button
                      size="sm"
                      onClick={() => handleApprovalAction(approval.id, "approve")}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleModify(approval)}
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Modify
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleApprovalAction(approval.id, "reject")}
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modify Dialog */}
      <Dialog open={modifyDialogOpen} onOpenChange={setModifyDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modify Approval</DialogTitle>
            <DialogDescription>
              Adjust the approval details before approving
            </DialogDescription>
          </DialogHeader>
          {selectedApproval && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={modifiedQuantity}
                  onChange={(e) => setModifiedQuantity(parseInt(e.target.value) || 0)}
                  min={1}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setModifyDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => handleApprovalAction(
                    selectedApproval.id,
                    "approve",
                    { quantity: modifiedQuantity }
                  )}
                >
                  Approve with Changes
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}

