"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Bot,
  Package,
  TrendingUp,
  Truck,
  Users,
  Zap,
  BarChart3,
  Blocks,
  Network,
  Settings,
  Bell,
} from "lucide-react"

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/agents", label: "Agent Management", icon: Bot },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/demand", label: "Demand Forecasting", icon: TrendingUp },
  { href: "/routes", label: "Route Optimization", icon: Truck },
  { href: "/suppliers", label: "Supplier Management", icon: Users },
  { href: "/simulation", label: "Simulation", icon: Zap },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/blockchain", label: "Blockchain", icon: Blocks },
  { href: "/knowledge-graph", label: "Knowledge Graph", icon: Network },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-sidebar-border bg-sidebar text-sidebar-foreground flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
            <span className="text-sm font-bold text-primary-foreground">SC</span>
          </div>
          <span className="font-bold text-lg">Supply Chain</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-2 rounded-lg transition-colors",
                isActive
                  ? "bg-sidebar-primary text-sidebar-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/10",
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="text-xs text-sidebar-foreground/60">v1.0.0</div>
      </div>
    </aside>
  )
}
