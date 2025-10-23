import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { LineChartComponent } from "@/components/charts/line-chart-component"
import { Play, Pause, RotateCcw, Plus } from "lucide-react"

export default function SimulationPage() {
  const simulationData = [
    { scenario: "Baseline", cost: 100000, efficiency: 85, time: "45 days" },
    { scenario: "Optimized Routes", cost: 92000, efficiency: 91, time: "38 days" },
    { scenario: "Increased Inventory", cost: 115000, efficiency: 88, time: "42 days" },
    { scenario: "Multi-Agent Coordination", cost: 85000, efficiency: 94, time: "35 days" },
  ]

  const simulationResults = [
    { month: "Jan", baseline: 100000, optimized: 92000, multiAgent: 85000 },
    { month: "Feb", baseline: 102000, optimized: 90000, multiAgent: 83000 },
    { month: "Mar", baseline: 105000, optimized: 91000, multiAgent: 84000 },
    { month: "Apr", baseline: 103000, optimized: 89000, multiAgent: 82000 },
    { month: "May", baseline: 107000, optimized: 93000, multiAgent: 86000 },
    { month: "Jun", baseline: 110000, optimized: 95000, multiAgent: 88000 },
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
                <h1 className="text-3xl font-bold">Simulation</h1>
                <p className="text-muted-foreground mt-1">Test scenarios and optimize supply chain strategies</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                New Simulation
              </Button>
            </div>

            {/* Active Simulation */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Current Simulation</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Scenario</p>
                    <p className="text-lg font-bold">Multi-Agent Coordination</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Progress</p>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-primary to-accent h-2 rounded-full"
                        style={{ width: "65%" }}
                      />
                    </div>
                    <p className="text-sm font-semibold mt-2">65% Complete</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Time Remaining</p>
                    <p className="text-lg font-bold">~2 hours</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button size="sm" className="bg-primary hover:bg-primary/90">
                    <Play className="w-4 h-4 mr-2" />
                    Resume
                  </Button>
                  <Button size="sm" variant="outline" className="bg-transparent">
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </Button>
                  <Button size="sm" variant="outline" className="bg-transparent">
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Scenario Comparison */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Scenario Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-semibold">Scenario</th>
                        <th className="text-left py-3 px-4 font-semibold">Total Cost</th>
                        <th className="text-left py-3 px-4 font-semibold">Efficiency</th>
                        <th className="text-left py-3 px-4 font-semibold">Cycle Time</th>
                        <th className="text-left py-3 px-4 font-semibold">Savings</th>
                      </tr>
                    </thead>
                    <tbody>
                      {simulationData.map((scenario) => (
                        <tr key={scenario.scenario} className="border-b border-border hover:bg-muted/30">
                          <td className="py-3 px-4 font-medium">{scenario.scenario}</td>
                          <td className="py-3 px-4">${scenario.cost.toLocaleString()}</td>
                          <td className="py-3 px-4">
                            <Badge className="bg-green-500/20 text-green-400">{scenario.efficiency}%</Badge>
                          </td>
                          <td className="py-3 px-4">{scenario.time}</td>
                          <td className="py-3 px-4 text-green-400 font-semibold">
                            {scenario.scenario === "Baseline" ? "-" : `-$${(100000 - scenario.cost).toLocaleString()}`}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Cost Comparison Chart */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Cost Projection Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <LineChartComponent
                  data={simulationResults}
                  lines={[
                    { key: "baseline", stroke: "hsl(0, 0%, 50%)", name: "Baseline" },
                    { key: "optimized", stroke: "hsl(264, 100%, 60%)", name: "Optimized Routes" },
                    { key: "multiAgent", stroke: "hsl(30, 100%, 60%)", name: "Multi-Agent" },
                  ]}
                />
              </CardContent>
            </Card>

            {/* Simulation Parameters */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Simulation Parameters</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-semibold block mb-2">Demand Variability</label>
                      <input type="range" min="0" max="100" defaultValue="50" className="w-full" />
                      <p className="text-xs text-muted-foreground mt-1">50%</p>
                    </div>
                    <div>
                      <label className="text-sm font-semibold block mb-2">Supply Disruption Risk</label>
                      <input type="range" min="0" max="100" defaultValue="30" className="w-full" />
                      <p className="text-xs text-muted-foreground mt-1">30%</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-semibold block mb-2">Warehouse Capacity</label>
                      <input type="range" min="0" max="100" defaultValue="80" className="w-full" />
                      <p className="text-xs text-muted-foreground mt-1">80%</p>
                    </div>
                    <div>
                      <label className="text-sm font-semibold block mb-2">Transportation Cost</label>
                      <input type="range" min="0" max="100" defaultValue="60" className="w-full" />
                      <p className="text-xs text-muted-foreground mt-1">60%</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
