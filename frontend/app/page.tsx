"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { StatsCard } from "@/components/dashboard/stats-card"
import { AgentCard } from "@/components/dashboard/agent-card"
import { Package, TrendingUp, Truck, Activity, AlertCircle } from "lucide-react"
import { useAgents, useSystemMetrics, useActivities, useAlerts } from "@/hooks/use-live-data"

export default function Dashboard() {
  const { agents, loading: agentsLoading, error: agentsError } = useAgents()
  const { metrics, loading: metricsLoading, error: metricsError } = useSystemMetrics()
  const { activities, loading: activitiesLoading } = useActivities()
  const { alerts, loading: alertsLoading } = useAlerts()

  // Transform agents data for display
  const transformedAgents = agents.map((agent, index) => ({
    name: agent.name,
    status: agent.status as "active" | "idle" | "stopped" | "simulating",
    efficiency: agent.efficiency,
    tasksCompleted: agent.tasks_completed,
    icon: ["📦", "📈", "🚚", "🤝"][index] || "🤖",
  }))

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 overflow-auto pt-16 p-6">
          <div className="max-w-7xl mx-auto space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground mt-1">Real-time overview of your supply chain operations</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                title="Active Agents"
                value={metricsLoading ? "..." : metrics?.active_agents?.toString() || "0"}
                change={metricsLoading ? "Loading..." : "All systems operational"}
                icon={<Activity className="w-5 h-5" />}
              />
              <StatsCard
                title="Inventory Value"
                value={metricsLoading ? "..." : `$${metrics?.total_inventory_value?.toLocaleString() || "0"}`}
                change={metricsLoading ? "Loading..." : "Real-time value"}
                icon={<Package className="w-5 h-5" />}
              />
              <StatsCard
                title="Pending Orders"
                value={metricsLoading ? "..." : metrics?.pending_orders?.toString() || "0"}
                change={metricsLoading ? "Loading..." : "Active orders"}
                icon={<TrendingUp className="w-5 h-5" />}
              />
              <StatsCard
                title="Active Routes"
                value={metricsLoading ? "..." : metrics?.active_routes?.toString() || "0"}
                change={metricsLoading ? "Loading..." : "Optimized routes"}
                icon={<Truck className="w-5 h-5" />}
              />
            </div>

            {/* AI Agents Status */}
            <div>
              <h2 className="text-xl font-bold mb-4">AI Agents Status</h2>
              {agentsLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="bg-card border border-border rounded-lg p-6 animate-pulse">
                      <div className="h-4 bg-muted rounded mb-2"></div>
                      <div className="h-8 bg-muted rounded mb-4"></div>
                      <div className="h-3 bg-muted rounded"></div>
                    </div>
                  ))}
                </div>
              ) : agentsError ? (
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
                  <p className="text-destructive">Error loading agents: {agentsError.message}</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {transformedAgents.map((agent) => (
                    <AgentCard key={agent.name} {...agent} />
                  ))}
                </div>
              )}
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">Recent Activities</h3>
                {activitiesLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3, 4].map((i) => (
                      <div key={i} className="flex items-start gap-4 pb-4 border-b border-border last:border-0">
                        <div className="w-2 h-2 rounded-full bg-muted mt-2 animate-pulse"></div>
                        <div className="flex-1">
                          <div className="h-4 bg-muted rounded mb-2 animate-pulse"></div>
                          <div className="h-3 bg-muted rounded w-1/2 animate-pulse"></div>
                        </div>
                        <div className="h-3 bg-muted rounded w-16 animate-pulse"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {activities.slice(0, 4).map((activity, i) => (
                      <div key={i} className="flex items-start gap-4 pb-4 border-b border-border last:border-0">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          activity.type === "success" ? "bg-green-500" :
                          activity.type === "warning" ? "bg-yellow-500" :
                          activity.type === "error" ? "bg-red-500" :
                          "bg-blue-500"
                        }`} />
                        <div className="flex-1">
                          <p className="font-medium text-sm">{activity.action}</p>
                          <p className="text-xs text-muted-foreground">{activity.agent}</p>
                        </div>
                        <span className="text-xs text-muted-foreground">{activity.time}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-card border border-border rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-accent" />
                  Alerts
                </h3>
                {alertsLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-3 rounded-lg bg-muted animate-pulse">
                        <div className="h-4 bg-muted-foreground/20 rounded"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {alerts.slice(0, 3).map((alert, i) => (
                      <div
                        key={i}
                        className={`p-3 rounded-lg text-sm ${
                          alert.level === "warning"
                            ? "bg-yellow-500/10 text-yellow-400"
                            : alert.level === "info"
                              ? "bg-blue-500/10 text-blue-400"
                              : alert.level === "error"
                                ? "bg-red-500/10 text-red-400"
                                : "bg-green-500/10 text-green-400"
                        }`}
                      >
                        {alert.message}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
