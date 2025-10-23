import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertCircle, Bell, Trash2, Archive } from "lucide-react"

export default function AlertsPage() {
  const alerts = [
    {
      id: 1,
      title: "Low Inventory Alert",
      message: "SKU-001 inventory level below reorder point in Warehouse B",
      severity: "warning",
      timestamp: "2 minutes ago",
      read: false,
    },
    {
      id: 2,
      title: "Route Delay",
      message: "Route RT-001 experiencing 45-minute delay due to traffic",
      severity: "warning",
      timestamp: "15 minutes ago",
      read: false,
    },
    {
      id: 3,
      title: "Supplier Alert",
      message: "Quick Supply Co on-time rate dropped to 92.1%",
      severity: "info",
      timestamp: "1 hour ago",
      read: true,
    },
    {
      id: 4,
      title: "Demand Spike Predicted",
      message: "AI forecasting predicts 25% demand increase for Q4",
      severity: "info",
      timestamp: "3 hours ago",
      read: true,
    },
    {
      id: 5,
      title: "Warehouse Capacity",
      message: "Warehouse C at 93% capacity - consider redistribution",
      severity: "warning",
      timestamp: "5 hours ago",
      read: true,
    },
  ]

  const alertStats = [
    { label: "Critical", value: "0", color: "text-red-400" },
    { label: "Warnings", value: "3", color: "text-yellow-400" },
    { label: "Info", value: "2", color: "text-blue-400" },
    { label: "Resolved", value: "847", color: "text-green-400" },
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
                <h1 className="text-3xl font-bold">Alerts & Notifications</h1>
                <p className="text-muted-foreground mt-1">Real-time supply chain alerts and notifications</p>
              </div>
              <Button variant="outline" className="bg-transparent">
                <Bell className="w-4 h-4 mr-2" />
                Configure Alerts
              </Button>
            </div>

            {/* Alert Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {alertStats.map((stat) => (
                <Card key={stat.label} className="bg-card border-border">
                  <CardContent className="pt-6">
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                      <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Active Alerts */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-accent" />
                  Active Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.map((alert) => {
                    const severityColors = {
                      critical: "bg-red-500/10 border-red-500/30 text-red-400",
                      warning: "bg-yellow-500/10 border-yellow-500/30 text-yellow-400",
                      info: "bg-blue-500/10 border-blue-500/30 text-blue-400",
                    }

                    return (
                      <div
                        key={alert.id}
                        className={`border rounded-lg p-4 ${severityColors[alert.severity as keyof typeof severityColors]} ${
                          !alert.read ? "ring-1 ring-accent" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-semibold">{alert.title}</p>
                              {!alert.read && <div className="w-2 h-2 rounded-full bg-accent" />}
                            </div>
                            <p className="text-sm opacity-80">{alert.message}</p>
                          </div>
                          <span className="text-xs opacity-60 whitespace-nowrap ml-4">{alert.timestamp}</span>
                        </div>

                        <div className="flex gap-2 mt-3">
                          <Button size="sm" variant="ghost" className="h-8 px-2 text-xs">
                            Acknowledge
                          </Button>
                          <Button size="sm" variant="ghost" className="h-8 px-2 text-xs">
                            <Archive className="w-3 h-3 mr-1" />
                            Archive
                          </Button>
                          <Button size="sm" variant="ghost" className="h-8 px-2 text-xs ml-auto">
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Alert Rules */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Alert Rules</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { rule: "Low Inventory", threshold: "< 100 units", enabled: true },
                    { rule: "Route Delay", threshold: "> 30 minutes", enabled: true },
                    { rule: "Warehouse Capacity", threshold: "> 90%", enabled: true },
                    { rule: "Supplier Performance", threshold: "< 95% on-time", enabled: true },
                    { rule: "Demand Spike", threshold: "> 20% increase", enabled: true },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                      <div>
                        <p className="font-semibold text-sm">{item.rule}</p>
                        <p className="text-xs text-muted-foreground">{item.threshold}</p>
                      </div>
                      <Badge
                        className={item.enabled ? "bg-green-500/20 text-green-400" : "bg-gray-500/20 text-gray-400"}
                      >
                        {item.enabled ? "Enabled" : "Disabled"}
                      </Badge>
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
