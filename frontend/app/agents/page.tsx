"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Settings, Play, Pause, RotateCcw, Loader2 } from "lucide-react"
import { apiClient, AgentStatus } from "@/lib/api"
import { useAgents } from "@/hooks/use-live-data"
import { ApprovalQueue } from "@/components/approvals/approval-queue"

interface AgentControlState {
  [key: string]: 'idle' | 'loading' | 'success' | 'error'
}

export default function AgentManagement() {
  const { agents, loading: agentsLoading, error: agentsError } = useAgents()
  const [controlState, setControlState] = useState<AgentControlState>({})
  const [communicationLog, setCommunicationLog] = useState<any[]>([])
  const [logLoading, setLogLoading] = useState(false)

  // Load communication log
  useEffect(() => {
    const loadCommunicationLog = async () => {
      try {
        setLogLoading(true)
        const log = await apiClient.getAgentCommunicationLog()
        setCommunicationLog(log)
      } catch (error) {
        console.warn('Error loading communication log:', error)
      } finally {
        setLogLoading(false)
      }
    }

    loadCommunicationLog()
  }, [])

  const handleAgentControl = async (agentId: string, action: 'start' | 'stop' | 'restart') => {
    setControlState(prev => ({ ...prev, [agentId]: 'loading' }))
    
    try {
      let result
      switch (action) {
        case 'start':
          result = await apiClient.startAgent(agentId)
          break
        case 'stop':
          result = await apiClient.stopAgent(agentId)
          break
        case 'restart':
          result = await apiClient.restartAgent(agentId)
          break
      }
      
      setControlState(prev => ({ ...prev, [agentId]: 'success' }))
      
      // Reset success state after 2 seconds
      setTimeout(() => {
        setControlState(prev => ({ ...prev, [agentId]: 'idle' }))
      }, 2000)
      
    } catch (error) {
      console.error(`Error ${action}ing agent:`, error)
      setControlState(prev => ({ ...prev, [agentId]: 'error' }))
      
      // Reset error state after 3 seconds
      setTimeout(() => {
        setControlState(prev => ({ ...prev, [agentId]: 'idle' }))
      }, 3000)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400'
      case 'idle': return 'bg-yellow-500/20 text-yellow-400'
      case 'stopped': return 'bg-red-500/20 text-red-400'
      case 'restarting': return 'bg-blue-500/20 text-blue-400'
      default: return 'bg-gray-500/20 text-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Active'
      case 'idle': return 'Idle'
      case 'stopped': return 'Stopped'
      case 'restarting': return 'Restarting'
      case 'connecting': return 'Connecting...'
      default: return 'Unknown'
    }
  }

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
              {agentsLoading ? (
                // Loading state
                Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i} className="bg-card border-border animate-pulse">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="h-6 bg-muted rounded mb-2"></div>
                          <div className="h-4 bg-muted rounded w-3/4"></div>
                        </div>
                        <div className="h-6 w-16 bg-muted rounded"></div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="h-4 bg-muted rounded"></div>
                        <div className="h-4 bg-muted rounded"></div>
                        <div className="h-4 bg-muted rounded"></div>
                      </div>
                      <div className="h-20 bg-muted rounded"></div>
                      <div className="flex gap-2">
                        <div className="flex-1 h-8 bg-muted rounded"></div>
                        <div className="flex-1 h-8 bg-muted rounded"></div>
                        <div className="flex-1 h-8 bg-muted rounded"></div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : agentsError ? (
                <div className="col-span-2 bg-destructive/10 border border-destructive/20 rounded-lg p-6">
                  <p className="text-destructive">Error loading agents: {agentsError.message}</p>
                </div>
              ) : (
                agents.map((agent, index) => {
                  // Map agent names to correct backend IDs
                  const agentIdMap: { [key: string]: string } = {
                    'Inventory Management': 'inventory',
                    'Demand Forecasting': 'demand', 
                    'Route Optimization': 'route',
                    'Supplier Coordination': 'supplier'
                  }
                  const agentId = agentIdMap[agent.name] || `agent-${String(index + 1).padStart(3, '0')}`
                  const isControlLoading = controlState[agentId] === 'loading'
                  const isControlSuccess = controlState[agentId] === 'success'
                  const isControlError = controlState[agentId] === 'error'
                  
                  return (
                    <Card key={agentId} className="bg-card border-border">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-lg">{agent.name}</CardTitle>
                            <p className="text-sm text-muted-foreground mt-1">
                              {agent.name === "Inventory Management" && "Manages inventory levels across all warehouses"}
                              {agent.name === "Demand Forecasting" && "Predicts demand patterns using ML models"}
                              {agent.name === "Route Optimization" && "Optimizes delivery routes for efficiency"}
                              {agent.name === "Supplier Coordination" && "Manages supplier communications and orders"}
                            </p>
                          </div>
                          <Badge className={getStatusColor(agent.status)}>
                            {getStatusText(agent.status)}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <p className="text-xs text-muted-foreground">Efficiency</p>
                            <p className="text-lg font-bold">{agent.efficiency}%</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Tasks</p>
                            <p className="text-lg font-bold">{agent.tasks_completed}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Last Activity</p>
                            <p className="text-sm font-semibold">
                              {new Date(agent.last_activity).toLocaleTimeString()}
                            </p>
                          </div>
                        </div>

                        {/* Configuration */}
                        <div className="bg-muted/30 rounded-lg p-4">
                          <p className="text-xs font-semibold text-muted-foreground mb-3">Configuration</p>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-muted-foreground">Status:</span>
                              <span className="font-medium">{getStatusText(agent.status)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-muted-foreground">Efficiency:</span>
                              <span className="font-medium">{agent.efficiency}%</span>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-muted-foreground">Tasks Completed:</span>
                              <span className="font-medium">{agent.tasks_completed}</span>
                            </div>
                          </div>
                        </div>

                        {/* Controls */}
                        <div className="flex gap-2">
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="flex-1 bg-transparent"
                            onClick={() => handleAgentControl(agentId, 'start')}
                            disabled={isControlLoading || agent.status === 'active'}
                          >
                            {isControlLoading && controlState[agentId] === 'loading' ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Play className="w-4 h-4 mr-2" />
                            )}
                            {isControlSuccess ? 'Started' : 'Start'}
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="flex-1 bg-transparent"
                            onClick={() => handleAgentControl(agentId, 'stop')}
                            disabled={isControlLoading || agent.status === 'stopped'}
                          >
                            {isControlLoading && controlState[agentId] === 'loading' ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Pause className="w-4 h-4 mr-2" />
                            )}
                            {isControlSuccess ? 'Stopped' : 'Stop'}
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="flex-1 bg-transparent"
                            onClick={() => handleAgentControl(agentId, 'restart')}
                            disabled={isControlLoading}
                          >
                            {isControlLoading && controlState[agentId] === 'loading' ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <RotateCcw className="w-4 h-4 mr-2" />
                            )}
                            {isControlSuccess ? 'Restarted' : 'Restart'}
                          </Button>
                        </div>

                        {/* Control Status */}
                        {isControlError && (
                          <div className="text-sm text-destructive">
                            Error: Failed to control agent
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  )
                })
              )}
            </div>

            {/* Approval Queue */}
            <ApprovalQueue />

            {/* Agent Communication Log */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Agent Communication Log</CardTitle>
              </CardHeader>
              <CardContent>
                {logLoading ? (
                  <div className="space-y-3">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div key={i} className="flex items-center gap-4 pb-3 border-b border-border last:border-0 animate-pulse">
                        <div className="flex-1">
                          <div className="h-4 bg-muted rounded mb-2"></div>
                          <div className="h-3 bg-muted rounded w-3/4"></div>
                        </div>
                        <div className="h-3 bg-muted rounded w-16"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {communicationLog.length > 0 ? (
                      communicationLog.slice(0, 10).map((log, i) => (
                        <div key={`${log.id || 'log'}-${i}`} className="flex items-center gap-4 pb-3 border-b border-border last:border-0">
                          <div className="flex-1">
                            <p className="text-sm font-medium">
                              <span className="text-primary">{log.from_agent}</span>
                              <span className="text-muted-foreground mx-2">→</span>
                              <span className="text-accent">{log.to_agent}</span>
                              <Badge variant="outline" className="ml-2 text-xs">
                                {log.message_type}
                              </Badge>
                            </p>
                            <p className="text-sm text-muted-foreground mt-1">{log.message}</p>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-muted-foreground">
                        <p>No communication logs available</p>
                        <p className="text-sm">Agent communication will appear here when agents interact</p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
