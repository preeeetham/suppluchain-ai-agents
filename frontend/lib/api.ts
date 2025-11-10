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
  current_quantity?: number; // For low stock items
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
  from_wallet?: string;
  to_wallet?: string;
  product_id?: string;
  blockchain_ready?: boolean;
  agent_id?: string;
}

export interface BlockchainData {
  transactions: BlockchainTransaction[];
  wallets: Record<string, { public_key: string; sol_balance: number }>;
  total_wallets: number;
  total_nfts: number;
  total_transactions: number;
  network_status: {
    current_slot: number;
    network_health: string;
    rpc_url: string;
    transactions_per_second?: number;
  };
  main_wallet_balance: number;
  nfts_created: number;
  payments_processed: number;
  wallet_addresses?: Record<string, string>;
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
      console.log(`🔄 Making API request to: ${url}`);
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
        // Add timeout and retry logic
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });

      console.log(`📡 API response: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ API request successful for ${endpoint}:`, data);
      return data;
    } catch (error) {
      console.error(`❌ API request failed for ${endpoint}:`, error);
      // For agent control operations, we should throw the error instead of using fallback
      if (endpoint.includes('/agents/') && (endpoint.includes('/start') || endpoint.includes('/stop') || endpoint.includes('/restart'))) {
        throw error;
      }
      // Return fallback data for other endpoints
      return this.getFallbackData<T>(endpoint);
    }
  }

  private getFallbackData<T>(endpoint: string): T {
    // Provide fallback data when API is not available
    const fallbackData: Record<string, any> = {
      '/agents': [
        {
          name: "Inventory Management",
          status: "connecting",
          efficiency: 0,
          tasks_completed: 0,
          last_activity: new Date().toISOString(),
          uptime: "Connecting..."
        },
        {
          name: "Demand Forecasting", 
          status: "connecting",
          efficiency: 0,
          tasks_completed: 0,
          last_activity: new Date().toISOString(),
          uptime: "Connecting..."
        },
        {
          name: "Route Optimization",
          status: "connecting", 
          efficiency: 0,
          tasks_completed: 0,
          last_activity: new Date().toISOString(),
          uptime: "Connecting..."
        },
        {
          name: "Supplier Coordination",
          status: "connecting",
          efficiency: 0,
          tasks_completed: 0,
          last_activity: new Date().toISOString(),
          uptime: "Connecting..."
        }
      ],
      '/metrics': {
        active_agents: 0,
        total_inventory_value: 0,
        pending_orders: 0,
        active_routes: 0,
        blockchain_transactions: 0,
        system_health: "connecting"
      },
      '/inventory': {
        warehouses: [],
        products: [],
        total_value: 0,
        low_stock_items: []
      },
      '/demand': {
        forecasts: [],
        accuracy: 0,
        trends: []
      },
      '/routes': {
        active_routes: [],
        optimized_today: 0,
        total_savings: 0
      },
      '/suppliers': {
        suppliers: [],
        active_orders: 0,
        pending_quotes: 0
      },
      '/blockchain': {
        transactions: [],
        wallet_balance: 0,
        network_status: "connecting"
      },
      '/activities': [
        {
          time: "Just now",
          action: "Connecting to backend...",
          agent: "System",
          type: "info"
        }
      ],
      '/alerts': [
        {
          level: "info",
          message: "Backend server not connected. Please start the API server.",
          timestamp: new Date().toISOString()
        }
      ],
      '/health': {
        status: "connecting",
        timestamp: new Date().toISOString()
      }
    };

    return fallbackData[endpoint] || {} as T;
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
  async getBlockchainData(): Promise<BlockchainData> {
    return this.request<BlockchainData>('/blockchain');
  }

  // Interactive Blockchain Operations
  async transferSOL(fromWallet: string, toWallet: string, amount: number): Promise<{
    success: boolean;
    transaction: any;
    message: string;
  }> {
    return this.request('/blockchain/transfer', {
      method: 'POST',
      body: JSON.stringify({ from_wallet: fromWallet, to_wallet: toWallet, amount }),
    });
  }

  async createNFT(productId: string, warehouseWallet: string, metadata: Record<string, any>): Promise<{
    success: boolean;
    nft: any;
    message: string;
  }> {
    return this.request('/blockchain/create-nft', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, warehouse_wallet: warehouseWallet, metadata }),
    });
  }

  async processPayment(fromWallet: string, toWallet: string, amount: number, productId?: string): Promise<{
    success: boolean;
    payment: any;
    message: string;
  }> {
    return this.request('/blockchain/process-payment', {
      method: 'POST',
      body: JSON.stringify({ from_wallet: fromWallet, to_wallet: toWallet, amount, product_id: productId }),
    });
  }

  async createWallet(walletName: string): Promise<{
    success: boolean;
    wallet: { name: string; public_key: string };
    message: string;
  }> {
    return this.request('/blockchain/create-wallet', {
      method: 'POST',
      body: JSON.stringify({ wallet_name: walletName }),
    });
  }

  async getWalletDetails(walletName: string): Promise<{
    success: boolean;
    wallet: {
      name: string;
      public_key: string;
      sol_balance: number;
      recent_transactions: any[];
      total_transactions: number;
    };
  }> {
    return this.request(`/blockchain/wallet/${walletName}`);
  }

  async getTransactions(walletName?: string, transactionType?: string, limit: number = 50): Promise<{
    success: boolean;
    transactions: any[];
    count: number;
  }> {
    const params = new URLSearchParams();
    if (walletName) params.append('wallet_name', walletName);
    if (transactionType) params.append('transaction_type', transactionType);
    params.append('limit', limit.toString());
    return this.request(`/blockchain/transactions?${params.toString()}`);
  }

  async updateNFTMetadata(productId: string, updates: Record<string, any>): Promise<{
    success: boolean;
    nft: any;
    message: string;
  }> {
    return this.request('/blockchain/update-nft', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, updates }),
    });
  }

  async transferNFTOwnership(productId: string, newOwnerWallet: string): Promise<{
    success: boolean;
    nft: any;
    message: string;
  }> {
    return this.request('/blockchain/transfer-nft', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, new_owner_wallet: newOwnerWallet }),
    });
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

  // Agent Control Methods
  async startAgent(agentId: string): Promise<{ status: string; message: string }> {
    return this.request(`/agents/${agentId}/start`, { method: 'POST' });
  }

  async stopAgent(agentId: string): Promise<{ status: string; message: string }> {
    return this.request(`/agents/${agentId}/stop`, { method: 'POST' });
  }

  async restartAgent(agentId: string): Promise<{ status: string; message: string }> {
    return this.request(`/agents/${agentId}/restart`, { method: 'POST' });
  }

  async getAgentStatus(agentId: string): Promise<AgentStatus & { agent_id: string }> {
    return this.request(`/agents/${agentId}/status`);
  }

  async getAgentCommunicationLog(): Promise<Array<{
    id: string;
    from_agent: string;
    to_agent: string;
    message: string;
    timestamp: string;
    message_type: string;
  }>> {
    return this.request('/agents/communication-log');
  }

  // --- Analytics Methods ---
  async getAnalyticsPerformance(): Promise<any> {
    return this.request('/analytics/performance');
  }

  async getAnalyticsTrends(): Promise<any> {
    return this.request('/analytics/trends');
  }

  // --- Knowledge Graph Methods ---
  async getKnowledgeGraphNodes(): Promise<any> {
    return this.request('/knowledge-graph/nodes');
  }

  async getKnowledgeGraphRelationships(): Promise<any> {
    return this.request('/knowledge-graph/relationships');
  }

  async queryKnowledgeGraph(query: string): Promise<any> {
    return this.request('/knowledge-graph/query', { method: 'POST', body: JSON.stringify({ query }) });
  }

  // --- Simulation Methods ---
  async getSimulationStatus(): Promise<any> {
    return this.request('/simulation/status');
  }

  async getSimulationResults(): Promise<any> {
    return this.request('/simulation/results');
  }

  async startSimulation(scenario: { name: string }): Promise<any> {
    return this.request('/simulation/start', { method: 'POST', body: JSON.stringify(scenario) });
  }

  async stopSimulation(): Promise<any> {
    return this.request('/simulation/stop', { method: 'POST' });
  }

  // --- Settings Methods ---
  async getSystemSettings(): Promise<any> {
    return this.request('/settings');
  }

  async updateSystemSettings(settings: any): Promise<any> {
    return this.request('/settings', { method: 'PUT', body: JSON.stringify(settings) });
  }

  async backupSystemSettings(): Promise<any> {
    return this.request('/settings/backup');
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
  private maxReconnectAttempts = 3; // Reduced from 5 to 3
  private reconnectDelay = 2000; // Increased delay
  private listeners: Map<string, ((data: any) => void)[]> = new Map();

  constructor(private url: string = 'ws://localhost:8000/ws') {
    // Don't auto-connect immediately, let components decide when to connect
  }

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
          console.log('🔌 WebSocket message received:', data);
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
        console.warn('WebSocket error (will retry):', error);
        // Don't immediately attempt reconnect on error, let onclose handle it
      };
    } catch (error) {
      console.warn('Error connecting WebSocket (will retry):', error);
      this.attemptReconnect();
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
      console.warn('WebSocket: Max reconnection attempts reached. Will retry when manually triggered.');
      // Don't show error, just warn and allow manual reconnection
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  manualReconnect(): void {
    console.log('Manual WebSocket reconnection triggered');
    this.reconnectAttempts = 0; // Reset attempts
    this.connect();
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
    console.log(`🔔 Notifying ${listeners?.length || 0} listeners for event: ${eventType}`);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }
}

// Export WebSocket singleton
export const wsClient = new WebSocketClient();
