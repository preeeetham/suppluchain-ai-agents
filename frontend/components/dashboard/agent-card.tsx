import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface AgentCardProps {
  name: string
  status: "active" | "idle" | "error"
  efficiency: number
  tasksCompleted: number
  icon?: React.ReactNode
}

export function AgentCard({ name, status, efficiency, tasksCompleted, icon }: AgentCardProps) {
  const statusColors = {
    active: "bg-green-500/20 text-green-400",
    idle: "bg-yellow-500/20 text-yellow-400",
    error: "bg-red-500/20 text-red-400",
  }

  return (
    <Card className="bg-card border-border hover:border-primary/50 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-3">
          {icon && <div className="text-accent text-2xl">{icon}</div>}
          <CardTitle className="text-base">{name}</CardTitle>
        </div>
        <Badge className={statusColors[status]}>{status}</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm text-muted-foreground">Efficiency</span>
            <span className="text-sm font-semibold">{efficiency}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-gradient-to-r from-primary to-accent h-2 rounded-full"
              style={{ width: `${efficiency}%` }}
            />
          </div>
        </div>
        <div className="text-sm">
          <span className="text-muted-foreground">Tasks Completed: </span>
          <span className="font-semibold">{tasksCompleted}</span>
        </div>
      </CardContent>
    </Card>
  )
}
