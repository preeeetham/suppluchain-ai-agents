/**
 * API client for Supply Chain AI Agents
 * Connects frontend with backend agents and real data
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface AgentStatus {
  name: string;
  status: 'active' | 'idle' | 'stopped' | 'simulating';
  efficiency: number;
  tasks_completed: number;
  last_activity: string;
  uptime: string;
}

export interface InventoryItem {
  warehouse_id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  reorder_point: number;
  unit_price: number;
  last_updated: string;
}

export interface DemandForecast {
  product_id: string;
  product_name: string;
  forecast_period: string;
  predicted_demand: number;
  confidence_score: number;
  seasonal_factor: number;
  trend: string;
}

export interface RouteOptimization {
  route_id: string;
  warehouse_id: string;
  destinations: string[];
  total_distance: number;
  estimated_time: number;
  efficiency_score: number;
  cost_savings: number;
}

export interface SupplierInfo {
  supplier_id: string;
  name: string;
  reliability_score: number;
  lead_time_days: number;
  cost_per_unit: number;
  quality_rating: number;
  active_orders: number;
}

export interface BlockchainTransaction {
  transaction_id: string;
  type: string;
  amount: number;
  timestamp: string;
  status: string;
  agent_id: string;
}

export interface SystemMetrics {
  active_agents: number;
  total_inventory_value: number;
  pending_orders: number;
  active_routes: number;
  blockchain_transactions: number;
  system_health: string;
}

export interface Activity {
  time: string;
  action: string;
  agent: string;
  type: 'success' | 'warning' | 'info' | 'error';
}

export interface Alert {
  level: 'warning' | 'info' | 'success' | 'error';
  message: string;
  timestamp: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Agent Management
  async getAgents(): Promise<AgentStatus[]> {
    return this.request<AgentStatus[]>('/agents');
  }

  async controlAgent(agentId: string, action: 'start' | 'stop' | 'restart'): Promise<{ status: string; action: string; agent_id: string }> {
    return this.request(`/agents/${agentId}/control`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
  }

  // Inventory Management
  async getInventory(): Promise<{
    warehouses: any[];
    products: InventoryItem[];
    total_value: number;
    low_stock_items: InventoryItem[];
  }> {
    return this.request('/inventory');
  }

  // Demand Forecasting
  async getDemandForecasts(): Promise<{
    forecasts: DemandForecast[];
    accuracy: number;
    trends: any[];
  }> {
    return this.request('/demand');
  }

  // Route Optimization
  async getRoutes(): Promise<{
    active_routes: RouteOptimization[];
    optimized_today: number;
    total_savings: number;
  }> {
    return this.request('/routes');
  }

  // Supplier Management
  async getSuppliers(): Promise<{
    suppliers: SupplierInfo[];
    active_orders: number;
    pending_quotes: number;
  }> {
    return this.request('/suppliers');
  }

  // Blockchain Integration
  async getBlockchainData(): Promise<{
    transactions: BlockchainTransaction[];
    wallet_balance: number;
    network_status: string;
  }> {
    return this.request('/blockchain');
  }

  // System Metrics
  async getSystemMetrics(): Promise<SystemMetrics> {
    return this.request('/metrics');
  }

  // Activities and Alerts
  async getRecentActivities(): Promise<Activity[]> {
    return this.request('/activities');
  }

  async getAlerts(): Promise<Alert[]> {
    return this.request('/alerts');
  }

  // Simulation Control
  async startSimulation(): Promise<{ status: string; message: string }> {
    return this.request('/simulation/start', {
      method: 'POST',
    });
  }

  async stopSimulation(): Promise<{ status: string; message: string }> {
    return this.request('/simulation/stop', {
      method: 'POST',
    });
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request('/health');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// WebSocket connection for real-time updates
export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor(private url: string = 'ws://localhost:8000/ws') {}

  connect(): void {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data.type, data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    
    this.listeners.get(eventType)!.push(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(eventType);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  private notifyListeners(eventType: string, data: any): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }
}

// Export WebSocket singleton
export const wsClient = new WebSocketClient();
