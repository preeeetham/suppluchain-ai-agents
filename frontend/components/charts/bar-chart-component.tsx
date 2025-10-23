"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface BarChartComponentProps {
  data: Array<Record<string, any>>
  bars: Array<{ key: string; fill: string; name: string }>
  title?: string
}

export function BarChartComponent({ data, bars, title }: BarChartComponentProps) {
  return (
    <div className="w-full h-80">
      {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis stroke="rgba(255,255,255,0.5)" />
          <YAxis stroke="rgba(255,255,255,0.5)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(20, 20, 40, 0.9)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: "8px",
            }}
          />
          <Legend />
          {bars.map((bar) => (
            <Bar key={bar.key} dataKey={bar.key} fill={bar.fill} name={bar.name} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
