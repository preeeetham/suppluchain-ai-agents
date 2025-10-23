import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Users, Star, AlertCircle, Plus } from "lucide-react"

export default function SupplierManagementPage() {
  const suppliers = [
    {
      id: 1,
      name: "Global Parts Inc",
      category: "Components",
      rating: 4.8,
      orders: 234,
      onTimeRate: 98.5,
      quality: 96,
      status: "active",
      leadTime: "5-7 days",
    },
    {
      id: 2,
      name: "Premium Materials Ltd",
      category: "Raw Materials",
      rating: 4.6,
      orders: 189,
      onTimeRate: 96.2,
      quality: 94,
      status: "active",
      leadTime: "7-10 days",
    },
    {
      id: 3,
      name: "Quick Supply Co",
      category: "Consumables",
      rating: 4.3,
      orders: 156,
      onTimeRate: 92.1,
      quality: 88,
      status: "active",
      leadTime: "2-3 days",
    },
    {
      id: 4,
      name: "Specialty Goods Ltd",
      category: "Specialized Parts",
      rating: 4.9,
      orders: 87,
      onTimeRate: 99.1,
      quality: 98,
      status: "active",
      leadTime: "10-14 days",
    },
  ]

  const performanceMetrics = [
    { metric: "Total Suppliers", value: "48", change: "+3 this quarter" },
    { metric: "Avg On-Time Rate", value: "96.5%", change: "+1.2% improvement" },
    { metric: "Avg Quality Score", value: "94.2%", change: "Stable" },
    { metric: "Active Orders", value: "1,247", change: "+156 pending" },
  ]

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 overflow-auto pt-16 p-6">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Supplier Management</h1>
                <p className="text-muted-foreground mt-1">Monitor supplier performance and manage relationships</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Add Supplier
              </Button>
            </div>

            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {performanceMetrics.map((metric) => (
                <Card key={metric.metric} className="bg-card border-border">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">{metric.metric}</p>
                      <p className="text-2xl font-bold">{metric.value}</p>
                      <p className="text-xs text-green-400">{metric.change}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Suppliers List */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-accent" />
                  Active Suppliers
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {suppliers.map((supplier) => (
                    <div key={supplier.id} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <p className="font-semibold">{supplier.name}</p>
                          <p className="text-sm text-muted-foreground">{supplier.category}</p>
                        </div>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < Math.floor(supplier.rating)
                                  ? "fill-yellow-500 text-yellow-500"
                                  : "text-muted-foreground"
                              }`}
                            />
                          ))}
                          <span className="text-sm font-semibold ml-2">{supplier.rating}</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-muted-foreground">Orders</p>
                          <p className="font-semibold">{supplier.orders}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">On-Time Rate</p>
                          <p className="font-semibold text-green-400">{supplier.onTimeRate}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Quality</p>
                          <p className="font-semibold text-green-400">{supplier.quality}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Lead Time</p>
                          <p className="font-semibold">{supplier.leadTime}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Status</p>
                          <Badge className="bg-green-500/20 text-green-400">{supplier.status}</Badge>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                          View Details
                        </Button>
                        <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                          Place Order
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Supplier Alerts */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-500" />
                  Supplier Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { supplier: "Quick Supply Co", alert: "On-time rate dropped to 92.1%", severity: "warning" },
                    { supplier: "Global Parts Inc", alert: "Lead time increased to 7-9 days", severity: "info" },
                    { supplier: "Premium Materials Ltd", alert: "Quality score improved to 94%", severity: "success" },
                  ].map((item, i) => (
                    <div
                      key={i}
                      className={`p-3 rounded-lg text-sm flex items-start gap-3 ${
                        item.severity === "warning"
                          ? "bg-yellow-500/10 text-yellow-400"
                          : item.severity === "info"
                            ? "bg-blue-500/10 text-blue-400"
                            : "bg-green-500/10 text-green-400"
                      }`}
                    >
                      <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" />
                      <div>
                        <p className="font-semibold">{item.supplier}</p>
                        <p className="text-xs opacity-80">{item.alert}</p>
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
