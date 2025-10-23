import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { LineChartComponent } from "@/components/charts/line-chart-component"
import { AlertTriangle, Plus, Download } from "lucide-react"

export default function InventoryPage() {
  const warehouseData = [
    { name: "Warehouse A", capacity: 10000, current: 8500, utilization: 85 },
    { name: "Warehouse B", capacity: 8000, current: 5200, utilization: 65 },
    { name: "Warehouse C", capacity: 12000, current: 11200, utilization: 93 },
    { name: "Warehouse D", capacity: 6000, current: 4800, utilization: 80 },
  ]

  const inventoryTrend = [
    { month: "Jan", inventory: 45000, orders: 12000 },
    { month: "Feb", inventory: 48000, orders: 14000 },
    { month: "Mar", inventory: 52000, orders: 16000 },
    { month: "Apr", inventory: 50000, orders: 15000 },
    { month: "May", inventory: 55000, orders: 18000 },
    { month: "Jun", inventory: 58000, orders: 20000 },
  ]

  const lowStockItems = [
    { sku: "SKU-001", product: "Widget A", current: 45, reorder: 100, warehouse: "Warehouse B" },
    { sku: "SKU-045", product: "Component X", current: 12, reorder: 50, warehouse: "Warehouse A" },
    { sku: "SKU-089", product: "Part Y", current: 8, reorder: 75, warehouse: "Warehouse D" },
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
                <h1 className="text-3xl font-bold">Inventory Management</h1>
                <p className="text-muted-foreground mt-1">Track inventory across all warehouses</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" className="bg-transparent">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
                <Button className="bg-primary hover:bg-primary/90">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Stock
                </Button>
              </div>
            </div>

            {/* Warehouse Capacity */}
            <div>
              <h2 className="text-xl font-bold mb-4">Warehouse Capacity</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {warehouseData.map((warehouse) => (
                  <Card key={warehouse.name} className="bg-card border-border">
                    <CardContent className="pt-6">
                      <div className="space-y-4">
                        <div>
                          <p className="text-sm font-semibold">{warehouse.name}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {warehouse.current.toLocaleString()} / {warehouse.capacity.toLocaleString()} units
                          </p>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              warehouse.utilization > 90
                                ? "bg-red-500"
                                : warehouse.utilization > 75
                                  ? "bg-yellow-500"
                                  : "bg-green-500"
                            }`}
                            style={{ width: `${warehouse.utilization}%` }}
                          />
                        </div>
                        <p className="text-sm font-bold">{warehouse.utilization}% Utilized</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Inventory Trend */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Inventory Trend</CardTitle>
              </CardHeader>
              <CardContent>
                <LineChartComponent
                  data={inventoryTrend}
                  lines={[
                    { key: "inventory", stroke: "hsl(264, 100%, 60%)", name: "Total Inventory" },
                    { key: "orders", stroke: "hsl(30, 100%, 60%)", name: "Orders" },
                  ]}
                />
              </CardContent>
            </Card>

            {/* Low Stock Alerts */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  Low Stock Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-semibold">SKU</th>
                        <th className="text-left py-3 px-4 font-semibold">Product</th>
                        <th className="text-left py-3 px-4 font-semibold">Current</th>
                        <th className="text-left py-3 px-4 font-semibold">Reorder Level</th>
                        <th className="text-left py-3 px-4 font-semibold">Warehouse</th>
                        <th className="text-left py-3 px-4 font-semibold">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lowStockItems.map((item) => (
                        <tr key={item.sku} className="border-b border-border hover:bg-muted/30">
                          <td className="py-3 px-4 font-mono text-xs">{item.sku}</td>
                          <td className="py-3 px-4">{item.product}</td>
                          <td className="py-3 px-4">
                            <Badge className="bg-red-500/20 text-red-400">{item.current}</Badge>
                          </td>
                          <td className="py-3 px-4">{item.reorder}</td>
                          <td className="py-3 px-4 text-muted-foreground">{item.warehouse}</td>
                          <td className="py-3 px-4">
                            <Button size="sm" variant="outline" className="bg-transparent">
                              Reorder
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
