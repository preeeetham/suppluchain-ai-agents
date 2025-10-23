import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings, Play, Pause, RotateCcw } from "lucide-react"

export default function AgentManagement() {
  const agents = [
    {
      id: 1,
      name: "Inventory Management Agent",
      description: "Manages inventory levels across all warehouses",
      status: "active",
      uptime: "99.8%",
      tasksProcessed: 1247,
      lastUpdate: "2 minutes ago",
      config: { updateInterval: "5m", warehouses: 12 },
    },
    {
      id: 2,
      name: "Demand Forecasting Agent",
      description: "Predicts demand patterns using ML models",
      status: "active",
      uptime: "99.5%",
      tasksProcessed: 856,
      lastUpdate: "5 minutes ago",
      config: { model: "LSTM", accuracy: "98.2%" },
    },
    {
      id: 3,
      name: "Route Optimization Agent",
      description: "Optimizes delivery routes for efficiency",
      status: "active",
      uptime: "98.9%",
      tasksProcessed: 623,
      lastUpdate: "1 minute ago",
      config: { algorithm: "Genetic", routes: 156 },
    },
    {
      id: 4,
      name: "Supplier Coordination Agent",
      description: "Manages supplier communications and orders",
      status: "idle",
      uptime: "99.2%",
      tasksProcessed: 445,
      lastUpdate: "30 minutes ago",
      config: { suppliers: 48, orders: 234 },
    },
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
                <h1 className="text-3xl font-bold">Agent Management</h1>
                <p className="text-muted-foreground mt-1">Monitor and control autonomous supply chain agents</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90">
                <Settings className="w-4 h-4 mr-2" />
                Configure Agents
              </Button>
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {agents.map((agent) => (
                <Card key={agent.id} className="bg-card border-border">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">{agent.description}</p>
                      </div>
                      <Badge
                        className={
                          agent.status === "active"
                            ? "bg-green-500/20 text-green-400"
                            : "bg-yellow-500/20 text-yellow-400"
                        }
                      >
                        {agent.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Uptime</p>
                        <p className="text-lg font-bold">{agent.uptime}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Tasks</p>
                        <p className="text-lg font-bold">{agent.tasksProcessed}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Last Update</p>
                        <p className="text-sm font-semibold">{agent.lastUpdate}</p>
                      </div>
                    </div>

                    {/* Configuration */}
                    <div className="bg-muted/30 rounded-lg p-4">
                      <p className="text-xs font-semibold text-muted-foreground mb-3">Configuration</p>
                      <div className="space-y-2">
                        {Object.entries(agent.config).map(([key, value]) => (
                          <div key={key} className="flex justify-between text-sm">
                            <span className="text-muted-foreground capitalize">{key}:</span>
                            <span className="font-medium">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Controls */}
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        <Play className="w-4 h-4 mr-2" />
                        Start
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        <Pause className="w-4 h-4 mr-2" />
                        Pause
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                        <RotateCcw className="w-4 h-4 mr-2" />
                        Reset
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Agent Communication Log */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Agent Communication Log</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      from: "Inventory Management",
                      to: "Demand Forecasting",
                      msg: "Requesting demand forecast for Q4",
                      time: "2 min ago",
                    },
                    {
                      from: "Route Optimization",
                      to: "Inventory Management",
                      msg: "Confirming pickup locations",
                      time: "5 min ago",
                    },
                    {
                      from: "Supplier Coordination",
                      to: "Inventory Management",
                      msg: "New shipment received",
                      time: "12 min ago",
                    },
                  ].map((log, i) => (
                    <div key={i} className="flex items-center gap-4 pb-3 border-b border-border last:border-0">
                      <div className="flex-1">
                        <p className="text-sm font-medium">
                          <span className="text-primary">{log.from}</span>
                          <span className="text-muted-foreground mx-2">→</span>
                          <span className="text-accent">{log.to}</span>
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">{log.msg}</p>
                      </div>
                      <span className="text-xs text-muted-foreground">{log.time}</span>
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
