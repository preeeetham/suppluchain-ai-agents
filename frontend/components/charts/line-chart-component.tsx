"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface LineChartComponentProps {
  data: Array<Record<string, any>>
  lines: Array<{ key: string; stroke: string; name: string }>
  title?: string
}

export function LineChartComponent({ data, lines, title }: LineChartComponentProps) {
  return (
    <div className="w-full h-80">
      {title && <h3 className="text-lg font-bold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
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
          {lines.map((line) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              stroke={line.stroke}
              name={line.name}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
