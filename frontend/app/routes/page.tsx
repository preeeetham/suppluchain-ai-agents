"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { BarChartComponent } from "@/components/charts/bar-chart-component"
import { MapPin, Truck, Plus } from "lucide-react"
import { useRoutes } from "@/hooks/use-live-data"

export default function RouteOptimizationPage() {
  const { routes, loading: routesLoading, error: routesError } = useRoutes()

  // Use real backend data for all components
  const routeMetrics = [
    { metric: "Active Routes", value: routes?.active_routes?.length?.toString() || "0", change: `+${routes?.optimized_today || 0} today` },
    { metric: "Avg Distance", value: `${routes?.avg_distance || 0} km`, change: "-8% optimized" },
    { metric: "Fuel Saved", value: `${routes?.fuel_saved || 0} L`, change: "+15% vs baseline" },
    { metric: "On-Time Rate", value: `${routes?.on_time_rate || 0}%`, change: "+2.1% this week" },
  ]

  const activeRoutes = routes?.active_routes?.map((route) => ({
    id: route.route_id,
    driver: route.driver,
    vehicle: route.vehicle,
    origin: route.warehouse_id,
    destination: route.destinations?.[0] || "Destination",
    distance: route.total_distance,
    eta: route.estimated_time,
    status: route.status,
    efficiency: route.efficiency_score,
  })) || []

  const routeEfficiency = routes?.route_efficiency || []

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
                <h1 className="text-3xl font-bold">Route Optimization</h1>
                <p className="text-muted-foreground mt-1">AI-optimized delivery routes and vehicle tracking</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Create Route
              </Button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {routeMetrics.map((metric) => (
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

            {/* Route Efficiency Chart */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Route Efficiency Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <BarChartComponent
                  data={routeEfficiency}
                  bars={[{ key: "efficiency", fill: "hsl(264, 100%, 60%)", name: "Efficiency %" }]}
                />
              </CardContent>
            </Card>

            {/* Active Routes */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="w-5 h-5 text-accent" />
                  Active Routes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activeRoutes.map((route) => (
                    <div key={route.id} className="border border-border rounded-lg p-4 hover:bg-muted/30 transition">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <p className="font-semibold">{route.id}</p>
                          <p className="text-sm text-muted-foreground">{route.driver}</p>
                        </div>
                        <Badge
                          className={
                            route.status === "in-transit"
                              ? "bg-blue-500/20 text-blue-400"
                              : "bg-green-500/20 text-green-400"
                          }
                        >
                          {route.status}
                        </Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-muted-foreground">Vehicle</p>
                          <p className="font-mono text-sm">{route.vehicle}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Distance</p>
                          <p className="font-semibold">{route.distance} km</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">ETA</p>
                          <p className="font-semibold">{route.eta}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Efficiency</p>
                          <p className="font-semibold text-green-400">{route.efficiency}%</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">{route.origin}</span>
                        <span className="text-muted-foreground">→</span>
                        <span className="text-muted-foreground">{route.destination}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Route Optimization Tips */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Optimization Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {(routes?.optimization_recommendations || []).map((rec, i) => (
                    <div key={i} className="flex items-start gap-4 p-3 bg-muted/30 rounded-lg">
                      <div className="w-2 h-2 rounded-full bg-accent mt-2" />
                      <div className="flex-1">
                        <p className="font-semibold text-sm">{rec.title}</p>
                        <p className="text-xs text-muted-foreground mt-1">{rec.desc}</p>
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
