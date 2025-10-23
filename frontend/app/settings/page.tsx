import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Save } from "lucide-react"

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col ml-64">
        <Header />
        <main className="flex-1 overflow-auto pt-16 p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold">Settings</h1>
              <p className="text-muted-foreground mt-1">Configure your supply chain platform</p>
            </div>

            {/* General Settings */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-sm font-semibold block mb-2">Organization Name</label>
                  <input
                    type="text"
                    defaultValue="Supply Chain Corp"
                    className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold block mb-2">Default Currency</label>
                  <select className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                    <option>USD</option>
                    <option>EUR</option>
                    <option>GBP</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-semibold block mb-2">Time Zone</label>
                  <select className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                    <option>UTC</option>
                    <option>EST</option>
                    <option>PST</option>
                  </select>
                </div>
              </CardContent>
            </Card>

            {/* Agent Configuration */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>AI Agent Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {[
                  { name: "Inventory Management", status: "active", updateInterval: "5 minutes" },
                  { name: "Demand Forecasting", status: "active", updateInterval: "1 hour" },
                  { name: "Route Optimization", status: "active", updateInterval: "15 minutes" },
                  { name: "Supplier Coordination", status: "idle", updateInterval: "30 minutes" },
                ].map((agent) => (
                  <div key={agent.name} className="border border-border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <p className="font-semibold">{agent.name}</p>
                      <Badge className="bg-green-500/20 text-green-400">{agent.status}</Badge>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground block mb-2">Update Interval</label>
                      <select className="w-full px-4 py-2 bg-muted border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary">
                        <option>{agent.updateInterval}</option>
                        <option>5 minutes</option>
                        <option>15 minutes</option>
                        <option>30 minutes</option>
                        <option>1 hour</option>
                      </select>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Notification Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { label: "Email Notifications", enabled: true },
                  { label: "SMS Alerts", enabled: false },
                  { label: "In-App Notifications", enabled: true },
                  { label: "Slack Integration", enabled: true },
                ].map((notif) => (
                  <div key={notif.label} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                    <p className="font-semibold text-sm">{notif.label}</p>
                    <input type="checkbox" defaultChecked={notif.enabled} className="w-4 h-4" />
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* API & Integrations */}
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>API & Integrations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-semibold block mb-2">API Key</label>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value="sk_live_••••••••••••••••"
                      readOnly
                      className="flex-1 px-4 py-2 bg-muted border border-border rounded-lg text-sm"
                    />
                    <Button variant="outline" className="bg-transparent">
                      Copy
                    </Button>
                  </div>
                </div>
                <div className="pt-4 border-t border-border">
                  <p className="text-sm font-semibold mb-3">Connected Services</p>
                  <div className="space-y-2">
                    {[
                      { name: "Solana Blockchain", status: "connected" },
                      { name: "Stripe Payments", status: "connected" },
                      { name: "Slack", status: "connected" },
                    ].map((service) => (
                      <div key={service.name} className="flex items-center justify-between p-2">
                        <p className="text-sm">{service.name}</p>
                        <Badge className="bg-green-500/20 text-green-400">{service.status}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button className="bg-primary hover:bg-primary/90">
                <Save className="w-4 h-4 mr-2" />
                Save Settings
              </Button>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
