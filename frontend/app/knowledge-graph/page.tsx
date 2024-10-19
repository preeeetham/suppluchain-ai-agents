"use client"

import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Network, Plus, Search } from "lucide-react"
import { useKnowledgeGraph } from "@/hooks/use-live-data"
import { apiClient } from "@/lib/api"
import { useState } from "react"

export default function KnowledgeGraphPage() {
  const { knowledgeGraph, loading: kgLoading, error: kgError } = useKnowledgeGraph()
  const [query, setQuery] = useState("")
  const [queryResults, setQueryResults] = useState<any[]>([])

  // Transform real data for display
  const entities = knowledgeGraph?.nodes?.nodes?.reduce((acc, node) => {
    const existing = acc.find(e => e.type === node.type)
    if (existing) {
      existing.count++
    } else {
      acc.push({
        type: node.type.charAt(0).toUpperCase() + node.type.slice(1),
        count: 1,
        color: `bg-${['blue', 'green', 'purple', 'orange', 'pink', 'cyan'][acc.length % 6]}-500/20 text-${['blue', 'green', 'purple', 'orange', 'pink', 'cyan'][acc.length % 6]}-400`
      })
    }
    return acc
  }, []) || [
    { type: "Warehouse", count: 12, color: "bg-blue-500/20 text-blue-400" },
    { type: "Supplier", count: 48, color: "bg-green-500/20 text-green-400" },
    { type: "Product", count: 2847, color: "bg-purple-500/20 text-purple-400" },
    { type: "Route", count: 156, color: "bg-orange-500/20 text-orange-400" },
    { type: "Agent", count: 4, color: "bg-pink-500/20 text-pink-400" },
    { type: "Customer", count: 1247, color: "bg-cyan-500/20 text-cyan-400" },
  ]

  const relationships = knowledgeGraph?.relationships?.relationships?.map(rel => ({
    from: rel.source,
    to: rel.target,
    type: rel.type,
    strength: rel.weight > 0.8 ? "strong" : rel.weight > 0.5 ? "medium" : "weak"
  })) || [
    { from: "Warehouse A", to: "Supplier 1", type: "supplies", strength: "strong" },
    { from: "Product SKU-001", to: "Warehouse B", type: "stored_in", strength: "strong" },
    { from: "Route RT-001", to: "Warehouse A", type: "originates_from", strength: "medium" },
    { from: "Agent IM", to: "Warehouse C", type: "manages", strength: "strong" },
    { from: "Supplier 2", to: "Product SKU-045", type: "manufactures", strength: "strong" },
    { from: "Customer 123", to: "Route RT-002", type: "assigned_to", strength: "medium" },
  ]

  const handleQuery = async () => {
    if (!query.trim()) return
    
    try {
      const results = await apiClient.queryKnowledgeGraph(query)
      setQueryResults(results.results || [])
    } catch (error) {
      console.warn('Error executing query:', error)
      setQueryResults([])
    }
  }

  const insights = [
    {
      title: "Supplier Network Optimization",
      desc: `Identified ${relationships.filter(r => r.type === 'supplies').length} supplier relationships that could reduce lead times by 15%`,
    },
    {
      title: "Product Clustering",
      desc: `Grouped ${entities.find(e => e.type === 'Product')?.count || 847} products into ${entities.length} categories for better inventory management`,
    },
    {
      title: "Route Efficiency Patterns",
      desc: `Discovered ${relationships.filter(r => r.type.includes('route')).length} route patterns that correlate with 92%+ efficiency scores`,
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
                <h1 className="text-3xl font-bold">Knowledge Graph</h1>
                <p className="text-muted-foreground mt-1">MeTTa-based semantic relationships in supply chain</p>
              </div>
              <Button className="bg-primary hover:bg-primary/90">
                <Plus className="w-4 h-4 mr-2" />
                Add Entity
              </Button>
            </div>

            {/* Graph Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Total Entities</p>
                    <p className="text-3xl font-bold">4,314</p>
                    <p className="text-xs text-green-400">+156 this week</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Total Relationships</p>
                    <p className="text-3xl font-bold">8,247</p>
                    <p className="text-xs text-green-400">+342 this week</p>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card border-border">
                <CardContent className="pt-6">
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">Graph Density</p>
                    <p className="text-3xl font-bold">0.847</p>
                    <p className="text-xs text-green-400">Well-connected</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Entity Types */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Network className="w-5 h-5 text-accent" />
                  Entity Types
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {entities.map((entity) => (
                    <div key={entity.type} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-semibold">{entity.type}</p>
                        <Badge className={entity.color}>{entity.count}</Badge>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-primary to-accent h-2 rounded-full"
                          style={{ width: `${(entity.count / 2847) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Relationships */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Key Relationships</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {relationships.map((rel, i) => (
                    <div key={i} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2 flex-1">
                          <span className="font-semibold text-sm">{rel.from}</span>
                          <span className="text-muted-foreground">→</span>
                          <span className="font-semibold text-sm">{rel.to}</span>
                        </div>
                        <Badge
                          className={
                            rel.strength === "strong"
                              ? "bg-green-500/20 text-green-400"
                              : "bg-yellow-500/20 text-yellow-400"
                          }
                        >
                          {rel.strength}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">Relationship: {rel.type}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Graph Search */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Graph Search</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2 mb-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search entities or relationships..."
                      className="w-full pl-10 pr-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                  <Button className="bg-primary hover:bg-primary/90">Search</Button>
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>AI-Generated Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {insights.map((insight, i) => (
                    <div key={i} className="p-4 bg-muted/30 rounded-lg border border-border">
                      <p className="font-semibold text-sm mb-1">{insight.title}</p>
                      <p className="text-sm text-muted-foreground">{insight.desc}</p>
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
