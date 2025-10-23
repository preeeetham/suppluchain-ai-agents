import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Blocks, Copy, ExternalLink, CheckCircle } from "lucide-react"

export default function BlockchainPage() {
  const transactions = [
    {
      id: "0x7f3a...8c2e",
      type: "Shipment Recorded",
      status: "confirmed",
      timestamp: "2 minutes ago",
      value: "Warehouse A → Distribution B",
      hash: "0x7f3a8b9c2d1e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8c2e",
    },
    {
      id: "0x2b4c...9d3f",
      type: "Inventory Update",
      status: "confirmed",
      timestamp: "15 minutes ago",
      value: "SKU-001: +500 units",
      hash: "0x2b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b",
    },
    {
      id: "0x9e1f...4a5b",
      type: "Supplier Payment",
      status: "pending",
      timestamp: "1 hour ago",
      value: "Global Parts Inc: $45,000",
      hash: "0x9e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e",
    },
    {
      id: "0x5c6d...1e2f",
      type: "Route Optimization",
      status: "confirmed",
      timestamp: "3 hours ago",
      value: "Route RT-001 optimized",
      hash: "0x5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b",
    },
  ]

  const blockchainStats = [
    { label: "Total Transactions", value: "12,847", change: "+234 today" },
    { label: "Network Status", value: "Healthy", change: "99.9% uptime" },
    { label: "Gas Fees (Avg)", value: "0.0012 SOL", change: "-15% vs week" },
    { label: "Verified Records", value: "98.7%", change: "All critical" },
  ]

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 overflow-auto pt-16 p-6">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold">Blockchain Integration</h1>
              <p className="text-muted-foreground mt-1">Immutable supply chain records on Solana network</p>
            </div>

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
                    <p className="text-sm text-muted-foreground mb-2">Current Block</p>
                    <p className="text-2xl font-bold font-mono">247,582,341</p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Transactions/sec</p>
                    <p className="text-2xl font-bold">4,200+</p>
                  </div>
                  <div className="p-4 bg-muted/30 rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">Network Health</p>
                    <Badge className="bg-green-500/20 text-green-400">Optimal</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Transactions */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Recent Blockchain Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {transactions.map((tx) => (
                    <div key={tx.id} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-semibold">{tx.type}</p>
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
                          </div>
                          <p className="text-sm text-muted-foreground">{tx.value}</p>
                        </div>
                        <span className="text-xs text-muted-foreground">{tx.timestamp}</span>
                      </div>

                      <div className="bg-muted/30 rounded p-3 mb-3">
                        <p className="text-xs text-muted-foreground mb-2">Transaction Hash</p>
                        <div className="flex items-center gap-2">
                          <code className="text-xs font-mono flex-1 truncate">{tx.hash}</code>
                          <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                            <Copy className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>

                      <Button size="sm" variant="outline" className="bg-transparent w-full">
                        <ExternalLink className="w-4 h-4 mr-2" />
                        View on Solana Explorer
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Smart Contracts */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Smart Contracts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      name: "Shipment Tracking",
                      address: "0x7f3a...8c2e",
                      status: "active",
                      calls: "2,847",
                    },
                    {
                      name: "Inventory Management",
                      address: "0x2b4c...9d3f",
                      status: "active",
                      calls: "1,234",
                    },
                    {
                      name: "Supplier Payments",
                      address: "0x9e1f...4a5b",
                      status: "active",
                      calls: "856",
                    },
                  ].map((contract) => (
                    <div key={contract.address} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-semibold">{contract.name}</p>
                        <Badge className="bg-green-500/20 text-green-400">{contract.status}</Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Address</p>
                          <p className="font-mono text-xs">{contract.address}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Function Calls</p>
                          <p className="font-semibold">{contract.calls}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
