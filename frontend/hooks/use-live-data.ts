"use client"

import { useState, useEffect } from "react"
import { apiClient, wsClient, AgentStatus, SystemMetrics, InventoryItem, DemandForecast, RouteOptimization, SupplierInfo, BlockchainTransaction, BlockchainData, Activity, Alert } from "@/lib/api"

interface LiveDataOptions {
  channel: string
  initialData?: any
}

export function useLiveData<T>({ channel, initialData }: LiveDataOptions) {
  const [data, setData] = useState<T | null>(initialData || null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (updateData) => {
      if (updateData[channel]) {
        setData(updateData[channel])
      }
    })

    wsClient.subscribe('agent_update', (updateData) => {
      if (channel === 'agents') {
        setData(updateData)
      }
    })

    wsClient.subscribe('simulation_start', (updateData) => {
      if (channel === 'simulation') {
        setData(updateData)
      }
    })

    wsClient.subscribe('simulation_stop', (updateData) => {
      if (channel === 'simulation') {
        setData(updateData)
      }
    })

    setIsConnected(true)

    return () => {
      unsubscribe()
      wsClient.disconnect()
      setIsConnected(false)
    }
  }, [channel])

  return { data, isConnected, error }
}

// Specific hooks for different data types
export function useAgents() {
  const [agents, setAgents] = useState<AgentStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getAgents()
        setAgents(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket data received:', data)
      if (data.agents) {
        // Convert the agents object to an array
        const agentsArray = Object.values(data.agents) as AgentStatus[]
        console.log('📊 Updating agents from WebSocket:', agentsArray)
        setAgents(agentsArray)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { agents, loading, error }
}

export function useSystemMetrics() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getSystemMetrics()
        setMetrics(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket metrics data received:', data)
      // System metrics would be calculated from the agents data
      if (data.agents) {
        const agentsArray = Object.values(data.agents) as AgentStatus[]
        const activeAgents = agentsArray.filter(agent => agent.status === 'active').length
        const totalTasks = agentsArray.reduce((sum, agent) => sum + agent.tasks_completed, 0)
        const avgEfficiency = agentsArray.reduce((sum, agent) => sum + agent.efficiency, 0) / agentsArray.length
        
        const systemMetrics: SystemMetrics = {
          active_agents: activeAgents,
          total_inventory_value: 0, // This would come from inventory data
          pending_orders: 0, // This would come from orders data
          active_routes: 0, // This would come from routes data
          blockchain_transactions: 0, // This would come from blockchain data
          system_health: avgEfficiency > 80 ? 'excellent' : avgEfficiency > 60 ? 'good' : 'warning'
        }
        
        console.log('📊 Updating system metrics from WebSocket:', systemMetrics)
        setMetrics(systemMetrics)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { metrics, loading, error }
}

export function useInventory() {
  const [inventory, setInventory] = useState<{
    warehouses: any[]
    products: InventoryItem[]
    total_value: number
    low_stock_items: InventoryItem[]
    warehouse_capacity: { [key: string]: number }
    warehouse_utilization: { [key: string]: number }
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchInventory = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getInventory()
        setInventory(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
        // Use fallback data with all required fields
        setInventory({
          warehouses: ['warehouse-001', 'warehouse-002', 'warehouse-003', 'warehouse-004'],
          products: [],
          total_value: 50000,
          low_stock_items: [],
          warehouse_capacity: {
            'warehouse-001': 10000,
            'warehouse-002': 12000,
            'warehouse-003': 11000,
            'warehouse-004': 13000
          },
          warehouse_utilization: {
            'warehouse-001': 75.0,
            'warehouse-002': 82.5,
            'warehouse-003': 68.0,
            'warehouse-004': 90.0
          }
        })
      } finally {
        setLoading(false)
      }
    }

    fetchInventory()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket inventory data received:', data)
      if (data.inventory) {
        console.log('📊 Updating inventory from WebSocket:', data.inventory)
        // Ensure all required fields are present
        const inventoryData = {
          warehouses: data.inventory.warehouses || [],
          products: data.inventory.products || [],
          total_value: data.inventory.total_value || 0,
          low_stock_items: data.inventory.low_stock_items || [],
          warehouse_capacity: data.inventory.warehouse_capacity || {},
          warehouse_utilization: data.inventory.warehouse_utilization || {}
        }
        setInventory(inventoryData)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { inventory, loading, error }
}

export function useDemandForecasts() {
  const [demand, setDemand] = useState<{
    forecasts: DemandForecast[]
    accuracy: number
    trends: any[]
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchDemand = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getDemandForecasts()
        setDemand(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchDemand()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket demand data received:', data)
      if (data.demand) {
        console.log('📊 Updating demand from WebSocket:', data.demand)
        setDemand(data.demand)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { demand, loading, error }
}

export function useRoutes() {
  const [routes, setRoutes] = useState<{
    active_routes: RouteOptimization[]
    optimized_today: number
    total_savings: number
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchRoutes = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getRoutes()
        setRoutes(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchRoutes()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket routes data received:', data)
      if (data.routes) {
        console.log('📊 Updating routes from WebSocket:', data.routes)
        setRoutes(data.routes)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { routes, loading, error }
}

export function useSuppliers() {
  const [suppliers, setSuppliers] = useState<{
    suppliers: SupplierInfo[]
    active_orders: number
    pending_quotes: number
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getSuppliers()
        setSuppliers(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchSuppliers()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket suppliers data received:', data)
      if (data.suppliers) {
        console.log('📊 Updating suppliers from WebSocket:', data.suppliers)
        setSuppliers(data.suppliers)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { suppliers, loading, error }
}

export function useBlockchain() {
  const [blockchain, setBlockchain] = useState<BlockchainData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchBlockchain = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getBlockchainData()
        setBlockchain(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchBlockchain()
  }, [])

  // Set up WebSocket connection for real-time updates
  useEffect(() => {
    wsClient.connect()
    
    const unsubscribe = wsClient.subscribe('data_update', (data) => {
      console.log('🔄 WebSocket blockchain data received:', data)
      if (data.blockchain) {
        console.log('📊 Updating blockchain from WebSocket:', data.blockchain)
        setBlockchain(data.blockchain)
      }
    })

    return () => {
      unsubscribe()
    }
  }, [])

  return { blockchain, loading, error }
}

export function useActivities() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getRecentActivities()
        setActivities(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchActivities()
  }, [])

  return { activities, loading, error }
}

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getAlerts()
        setAlerts(data)
      } catch (err) {
        console.warn('Error fetching data (using fallback data):', err)
        // Don't set error state for connection issues, just use fallback data
        if (!(err as Error).message.includes('Failed to fetch')) {
          setError(err as Error)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
  }, [])

  return { alerts, loading, error }
}

// --- Analytics Hooks ---

export function useAnalytics() {
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      const [performance, trends] = await Promise.all([
        apiClient.getAnalyticsPerformance(),
        apiClient.getAnalyticsTrends()
      ])
      setAnalytics({ performance, trends })
    } catch (err) {
      console.warn('Error fetching analytics (using fallback data):', err)
      // Don't set error state for connection issues, just use fallback data
      if (!(err as Error).message.includes('Failed to fetch')) {
        setError(err as Error)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalytics()
  }, [])

  return { analytics, loading, error }
}

// --- Knowledge Graph Hooks ---

export function useKnowledgeGraph() {
  const [knowledgeGraph, setKnowledgeGraph] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchKnowledgeGraph = async () => {
    try {
      setLoading(true)
      const [nodes, relationships] = await Promise.all([
        apiClient.getKnowledgeGraphNodes(),
        apiClient.getKnowledgeGraphRelationships()
      ])
      setKnowledgeGraph({ nodes, relationships })
    } catch (err) {
      console.warn('Error fetching knowledge graph (using fallback data):', err)
      // Don't set error state for connection issues, just use fallback data
      if (!(err as Error).message.includes('Failed to fetch')) {
        setError(err as Error)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKnowledgeGraph()
  }, [])

  return { knowledgeGraph, loading, error }
}

// --- Simulation Hooks ---

export function useSimulation() {
  const [simulation, setSimulation] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchSimulation = async () => {
    try {
      setLoading(true)
      const [status, results] = await Promise.all([
        apiClient.getSimulationStatus(),
        apiClient.getSimulationResults()
      ])
      setSimulation({ status, results })
    } catch (err) {
      console.warn('Error fetching simulation (using fallback data):', err)
      // Don't set error state for connection issues, just use fallback data
      if (!(err as Error).message.includes('Failed to fetch')) {
        setError(err as Error)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSimulation()
  }, [])

  return { simulation, loading, error }
}

// --- Settings Hooks ---

export function useSettings() {
  const [settings, setSettings] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const fetchSettings = async () => {
    try {
      setLoading(true)
      const settingsData = await apiClient.getSystemSettings()
      setSettings(settingsData)
    } catch (err) {
      console.warn('Error fetching settings (using fallback data):', err)
      // Don't set error state for connection issues, just use fallback data
      if (!(err as Error).message.includes('Failed to fetch')) {
        setError(err as Error)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  return { settings, loading, error }
}
