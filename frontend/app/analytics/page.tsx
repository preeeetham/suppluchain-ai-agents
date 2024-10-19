"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { LineChartComponent } from "@/components/charts/line-chart-component"
import { BarChartComponent } from "@/components/charts/bar-chart-component"
import { TrendingUp, Activity, Zap } from "lucide-react"
import { useAnalytics } from "@/hooks/use-live-data"

export default function AnalyticsPage() {
  const { analytics, loading: analyticsLoading, error: analyticsError } = useAnalytics()

  // Transform real data for display
  const kpis = analytics?.performance ? [
    { label: "Supply Chain Efficiency", value: analytics.performance.system_uptime, change: "+3.2%", icon: Activity },
    { label: "Cost Reduction", value: `$${Math.floor(analytics.performance.throughput_per_second / 1000)}K`, change: "+12.5%", icon: TrendingUp },
    { label: "On-Time Delivery", value: analytics.performance.blockchain_transactions?.success_rate || "98.1%", change: "+1.8%", icon: Zap },
    { label: "Inventory Turnover", value: "8.4x", change: "+0.6x", icon: Activity },
  ] : [
    { label: "Supply Chain Efficiency", value: "92.3%", change: "+3.2%", icon: Activity },
    { label: "Cost Reduction", value: "$847K", change: "+12.5%", icon: TrendingUp },
    { label: "On-Time Delivery", value: "98.1%", change: "+1.8%", icon: Zap },
    { label: "Inventory Turnover", value: "8.4x", change: "+0.6x", icon: Activity },
  ]

  const performanceData = analytics?.trends?.inventory_trends?.map((trend, index) => ({
    week: `W${index + 1}`,
    efficiency: Math.floor(trend.value / 1000),
    cost: Math.floor(100 - (trend.change * 2)),
    delivery: Math.floor(95 + (trend.change * 0.5))
  })) || [
    { week: "W1", efficiency: 88, cost: 95, delivery: 96 },
    { week: "W2", efficiency: 89, cost: 93, delivery: 97 },
    { week: "W3", efficiency: 91, cost: 91, delivery: 98 },
    { week: "W4", efficiency: 92, cost: 89, delivery: 98 },
    { week: "W5", efficiency: 93, cost: 87, delivery: 99 },
    { week: "W6", efficiency: 92, cost: 88, delivery: 98 },
  ]

  const departmentMetrics = analytics?.performance?.agent_efficiency ? 
    Object.entries(analytics.performance.agent_efficiency).map(([dept, score]) => ({
      dept: dept.charAt(0).toUpperCase() + dept.slice(1),
      score: Math.floor(score)
    })) : [
    { dept: "Inventory", score: 94 },
    { dept: "Forecasting", score: 91 },
    { dept: "Routes", score: 88 },
    { dept: "Suppliers", score: 85 },
    { dept: "Logistics", score: 92 },
  ]

  const topMetrics = [
    { metric: "Warehouse Utilization", value: "87%", trend: "up" },
    { metric: "Vehicle Utilization", value: "82%", trend: "up" },
    { metric: "Order Accuracy", value: "99.2%", trend: "stable" },
    { metric: "Return Rate", value: "0.8%", trend: "down" },
    { metric: "Lead Time Variance", value: "±2.1 days", trend: "down" },
    { metric: "Supplier Reliability", value: "96.8%", trend: "up" },
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
              <h1 className="text-3xl font-bold">Analytics</h1>
              <p className="text-muted-foreground mt-1">Comprehensive supply chain performance metrics</p>
            </div>

            {/* Key Performance Indicators */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {kpis.map((kpi) => {
                const Icon = kpi.icon
                return (
                  <Card key={kpi.label} className="bg-card border-border">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm text-muted-foreground">{kpi.label}</p>
                          <p className="text-2xl font-bold mt-2">{kpi.value}</p>
                          <p className="text-xs text-green-400 mt-2">{kpi.change}</p>
                        </div>
                        <Icon className="w-8 h-8 text-accent opacity-50" />
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>

            {/* Performance Trends */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Weekly Performance Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <LineChartComponent
                  data={performanceData}
                  lines={[
                    { key: "efficiency", stroke: "hsl(264, 100%, 60%)", name: "Efficiency %" },
                    { key: "cost", stroke: "hsl(30, 100%, 60%)", name: "Cost Index" },
                    { key: "delivery", stroke: "hsl(120, 100%, 50%)", name: "On-Time %" },
                  ]}
                />
              </CardContent>
            </Card>

            {/* Department Performance */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Department Performance Scores</CardTitle>
              </CardHeader>
              <CardContent>
                <BarChartComponent
                  data={departmentMetrics}
                  bars={[{ key: "score", fill: "hsl(264, 100%, 60%)", name: "Performance Score" }]}
                />
              </CardContent>
            </Card>

            {/* Detailed Metrics */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Detailed Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {topMetrics.map((metric) => (
                    <div key={metric.metric} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-semibold">{metric.metric}</p>
                        <Badge
                          className={
                            metric.trend === "up"
                              ? "bg-green-500/20 text-green-400"
                              : metric.trend === "down"
                                ? "bg-blue-500/20 text-blue-400"
                                : "bg-gray-500/20 text-gray-400"
                          }
                        >
                          {metric.trend === "up" ? "↑" : metric.trend === "down" ? "↓" : "→"}
                        </Badge>
                      </div>
                      <p className="text-2xl font-bold">{metric.value}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Insights */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    {
                      title: "Efficiency Improvement",
                      desc: "Supply chain efficiency improved 3.2% this month, driven by route optimization",
                    },
                    {
                      title: "Cost Savings",
                      desc: "Multi-agent coordination saved $847K in operational costs",
                    },
                    {
                      title: "Delivery Performance",
                      desc: "On-time delivery rate reached 98.1%, exceeding target of 95%",
                    },
                  ].map((insight, i) => (
                    <div key={i} className="p-3 bg-muted/30 rounded-lg">
                      <p className="font-semibold text-sm">{insight.title}</p>
                      <p className="text-xs text-muted-foreground mt-1">{insight.desc}</p>
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
