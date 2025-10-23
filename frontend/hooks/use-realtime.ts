"use client"

import { useEffect, useRef, useCallback } from "react"

interface RealtimeMessage {
  type: string
  data: any
  timestamp: number
}

interface UseRealtimeOptions {
  onMessage?: (message: RealtimeMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Error) => void
  autoReconnect?: boolean
}

export function useRealtime(options: UseRealtimeOptions = {}) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:"
      const wsUrl = `${protocol}//${window.location.host}/api/ws`

      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        console.log("[v0] WebSocket connected")
        reconnectAttemptsRef.current = 0
        options.onConnect?.()
      }

      wsRef.current.onmessage = (event) => {
        try {
          const message: RealtimeMessage = JSON.parse(event.data)
          options.onMessage?.(message)
        } catch (error) {
          console.error("[v0] Failed to parse message:", error)
        }
      }

      wsRef.current.onerror = (error) => {
        console.error("[v0] WebSocket error:", error)
        options.onError?.(new Error("WebSocket error"))
      }

      wsRef.current.onclose = () => {
        console.log("[v0] WebSocket disconnected")
        options.onDisconnect?.()

        if (options.autoReconnect && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          reconnectTimeoutRef.current = setTimeout(connect, delay)
        }
      }
    } catch (error) {
      console.error("[v0] Failed to connect:", error)
      options.onError?.(error as Error)
    }
  }, [options])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
    }
  }, [])

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn("[v0] WebSocket not connected")
    }
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { send, disconnect, isConnected: wsRef.current?.readyState === WebSocket.OPEN }
}
