import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChartComponent } from "@/components/charts/line-chart-component"
import { BarChartComponent } from "@/components/charts/bar-chart-component"
import { TrendingUp } from "lucide-react"

export default function DemandForecastingPage() {
  const demandForecast = [
    { month: "Jan", actual: 12000, predicted: 11800, confidence: 95 },
    { month: "Feb", actual: 14000, predicted: 14200, confidence: 94 },
    { month: "Mar", actual: 16000, predicted: 15800, confidence: 96 },
    { month: "Apr", actual: 15000, predicted: 15200, confidence: 93 },
    { month: "May", actual: 18000, predicted: 17900, confidence: 95 },
    { month: "Jun", actual: 20000, predicted: 20100, confidence: 94 },
  ]

  const productForecasts = [
    { product: "Widget A", q3: 45000, q4: 52000, growth: 15.6 },
    { product: "Component X", q3: 32000, q4: 38000, growth: 18.8 },
    { product: "Part Y", q3: 28000, q4: 31000, growth: 10.7 },
    { product: "Assembly Z", q3: 18000, q4: 22000, growth: 22.2 },
  ]

  const seasonalTrends = [
    { season: "Q1", demand: 42000 },
    { season: "Q2", demand: 45000 },
    { season: "Q3", demand: 48000 },
    { season: "Q4", demand: 58000 },
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
              <h1 className="text-3xl font-bold">Demand Forecasting</h1>
              <p className="text-muted-foreground mt-1">AI-powered demand predictions and trend analysis</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Forecast Accuracy</p>
                    <p className="text-3xl font-bold">94.8%</p>
                    <p className="text-xs text-green-400">+2.1% from last month</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Avg Confidence</p>
                    <p className="text-3xl font-bold">94.5%</p>
                    <p className="text-xs text-green-400">High confidence predictions</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Q4 Forecast</p>
                    <p className="text-3xl font-bold">143K</p>
                    <p className="text-xs text-green-400">+18.5% vs Q3</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Demand Forecast Chart */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Actual vs Predicted Demand</CardTitle>
              </CardHeader>
              <CardContent>
                <LineChartComponent
                  data={demandForecast}
                  lines={[
                    { key: "actual", stroke: "hsl(264, 100%, 60%)", name: "Actual Demand" },
                    { key: "predicted", stroke: "hsl(30, 100%, 60%)", name: "Predicted Demand" },
                  ]}
                />
              </CardContent>
            </Card>

            {/* Seasonal Trends */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Seasonal Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <BarChartComponent
                  data={seasonalTrends}
                  bars={[{ key: "demand", fill: "hsl(264, 100%, 60%)", name: "Demand" }]}
                />
              </CardContent>
            </Card>

            {/* Product-Level Forecasts */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-accent" />
                  Product-Level Forecasts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-semibold">Product</th>
                        <th className="text-left py-3 px-4 font-semibold">Q3 Forecast</th>
                        <th className="text-left py-3 px-4 font-semibold">Q4 Forecast</th>
                        <th className="text-left py-3 px-4 font-semibold">Growth</th>
                        <th className="text-left py-3 px-4 font-semibold">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {productForecasts.map((product) => (
                        <tr key={product.product} className="border-b border-border hover:bg-muted/30">
                          <td className="py-3 px-4 font-medium">{product.product}</td>
                          <td className="py-3 px-4">{product.q3.toLocaleString()}</td>
                          <td className="py-3 px-4">{product.q4.toLocaleString()}</td>
                          <td className="py-3 px-4">
                            <Badge className="bg-green-500/20 text-green-400">+{product.growth}%</Badge>
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-muted rounded-full h-2">
                                <div
                                  className="bg-gradient-to-r from-primary to-accent h-2 rounded-full"
                                  style={{ width: "95%" }}
                                />
                              </div>
                              <span className="text-xs">95%</span>
                            </div>
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
