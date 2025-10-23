"use client"

import { useState, useEffect } from "react"
import { apiClient, wsClient, AgentStatus, SystemMetrics, InventoryItem, DemandForecast, RouteOptimization, SupplierInfo, BlockchainTransaction, Activity, Alert } from "@/lib/api"

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

  const { data: liveData } = useLiveData<{ agents: AgentStatus[] }>({ channel: 'agents' })

  useEffect(() => {
    if (liveData?.agents) {
      setAgents(liveData.agents)
    }
  }, [liveData])

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

  const { data: liveData } = useLiveData<SystemMetrics>({ channel: 'metrics' })

  useEffect(() => {
    if (liveData) {
      setMetrics(liveData)
    }
  }, [liveData])

  return { metrics, loading, error }
}

export function useInventory() {
  const [inventory, setInventory] = useState<{
    warehouses: any[]
    products: InventoryItem[]
    total_value: number
    low_stock_items: InventoryItem[]
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
      } finally {
        setLoading(false)
      }
    }

    fetchInventory()
  }, [])

  const { data: liveData } = useLiveData<typeof inventory>({ channel: 'inventory' })

  useEffect(() => {
    if (liveData) {
      setInventory(liveData)
    }
  }, [liveData])

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

  const { data: liveData } = useLiveData<typeof demand>({ channel: 'demand' })

  useEffect(() => {
    if (liveData) {
      setDemand(liveData)
    }
  }, [liveData])

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

  const { data: liveData } = useLiveData<typeof routes>({ channel: 'routes' })

  useEffect(() => {
    if (liveData) {
      setRoutes(liveData)
    }
  }, [liveData])

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

  const { data: liveData } = useLiveData<typeof suppliers>({ channel: 'suppliers' })

  useEffect(() => {
    if (liveData) {
      setSuppliers(liveData)
    }
  }, [liveData])

  return { suppliers, loading, error }
}

export function useBlockchain() {
  const [blockchain, setBlockchain] = useState<{
    transactions: BlockchainTransaction[]
    wallet_balance: number
    network_status: string
  } | null>(null)
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

  const { data: liveData } = useLiveData<typeof blockchain>({ channel: 'blockchain' })

  useEffect(() => {
    if (liveData) {
      setBlockchain(liveData)
    }
  }, [liveData])

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
