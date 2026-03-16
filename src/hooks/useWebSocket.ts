import { useState, useCallback, useEffect, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  timestamp: string;
  data?: unknown;
  message?: string;
  [key: string]: unknown;
}

interface UseWebSocketOptions {
  autoReconnect?: boolean;
  reconnectAttempts?: number;
  reconnectDelay?: number;
}

export const useWebSocket = (
  url: string,
  options: UseWebSocketOptions = {}
) => {
  const {
    autoReconnect = true,
    reconnectAttempts = 5,
    reconnectDelay = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const messageCallbacksRef = useRef<Map<string, (msg: WebSocketMessage) => void>>(new Map());
  const connectRef = useRef<() => void>(() => undefined);

  const connect = useCallback(() => {
    try {
      const wsUrl = url.startsWith('ws') ? url : `ws://${url}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setError(null);
        reconnectCountRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setMessages((prev) => [...prev, message]);
          setLastMessage(message);

          // Call type-specific callbacks
          const callback = messageCallbacksRef.current.get(message.type);
          if (callback) {
            callback(message);
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt to reconnect
        if (autoReconnect && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Reconnecting... (attempt ${reconnectCountRef.current})`);
            connectRef.current();
          }, reconnectDelay);
        }
      };

      wsRef.current = ws;
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Unknown error';
      setError(`Failed to connect: ${errorMsg}`);
    }
  }, [url, autoReconnect, reconnectAttempts, reconnectDelay]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    } else {
      setError('WebSocket not connected');
    }
  }, []);

  const subscribe = useCallback(
    (messageType: string, callback: (msg: WebSocketMessage) => void) => {
      messageCallbacksRef.current.set(messageType, callback);
      return () => {
        messageCallbacksRef.current.delete(messageType);
      };
    },
    []
  );

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  // Log health check
  const sendPing = useCallback(() => {
    send({ type: 'ping' });
  }, [send]);

  // Auto-connect on mount
  useEffect(() => {
    const initialConnectTimer = setTimeout(() => {
      connectRef.current();
    }, 0);

    return () => {
      clearTimeout(initialConnectTimer);
      disconnect();
    };
  }, [disconnect]);

  // Periodic ping to keep connection alive
  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      sendPing();
    }, 30000); // Every 30 seconds

    return () => clearInterval(pingInterval);
  }, [isConnected, sendPing]);

  return {
    isConnected,
    messages,
    lastMessage,
    error,
    send,
    subscribe,
    disconnect,
    connect,
    sendPing,
  };
};
