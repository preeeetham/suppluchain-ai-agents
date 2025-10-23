"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChartComponent } from "@/components/charts/line-chart-component"
import { BarChartComponent } from "@/components/charts/bar-chart-component"
import { TrendingUp } from "lucide-react"
import { useDemandForecasts } from "@/hooks/use-live-data"

export default function DemandForecastingPage() {
  const { demand, loading: demandLoading, error: demandError } = useDemandForecasts()

  // Transform real data for display
  const demandForecast = [
    { month: "Jan", actual: 12000, predicted: demand?.forecasts?.[0]?.predicted_demand || 11800, confidence: demand?.accuracy || 95 },
    { month: "Feb", actual: 14000, predicted: demand?.forecasts?.[1]?.predicted_demand || 14200, confidence: demand?.accuracy || 94 },
    { month: "Mar", actual: 16000, predicted: demand?.forecasts?.[2]?.predicted_demand || 15800, confidence: demand?.accuracy || 96 },
    { month: "Apr", actual: 15000, predicted: demand?.forecasts?.[3]?.predicted_demand || 15200, confidence: demand?.accuracy || 93 },
    { month: "May", actual: 18000, predicted: demand?.forecasts?.[4]?.predicted_demand || 17900, confidence: demand?.accuracy || 95 },
    { month: "Jun", actual: 20000, predicted: demand?.forecasts?.[5]?.predicted_demand || 20100, confidence: demand?.accuracy || 94 },
  ]

  const productForecasts = demand?.forecasts?.map((forecast, index) => ({
    product: forecast.product_name,
    q3: Math.floor(forecast.predicted_demand * 0.8),
    q4: forecast.predicted_demand,
    growth: forecast.seasonal_factor * 10,
  })) || [
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
                    {demandLoading ? (
                      <div className="h-8 bg-muted rounded animate-pulse"></div>
                    ) : (
                      <p className="text-3xl font-bold">{demand?.accuracy || 94.8}%</p>
                    )}
                    <p className="text-xs text-green-400">+2.1% from last month</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Avg Confidence</p>
                    {demandLoading ? (
                      <div className="h-8 bg-muted rounded animate-pulse"></div>
                    ) : (
                      <p className="text-3xl font-bold">
                        {demand?.forecasts?.length ? 
                          Math.round(demand.forecasts.reduce((acc, f) => acc + f.confidence_score, 0) / demand.forecasts.length) : 
                          94.5
                        }%
                      </p>
                    )}
                    <p className="text-xs text-green-400">High confidence predictions</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Q4 Forecast</p>
                    {demandLoading ? (
                      <div className="h-8 bg-muted rounded animate-pulse"></div>
                    ) : (
                      <p className="text-3xl font-bold">
                        {demand?.forecasts?.length ? 
                          Math.round(demand.forecasts.reduce((acc, f) => acc + f.predicted_demand, 0) / 1000) + 'K' : 
                          '143K'
                        }
                      </p>
                    )}
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
