"""
Real-time WebSocket Handler for Sentinel-Net
Provides live streaming of analysis results and system updates
"""

import json
import asyncio
from typing import Set, Dict, Any
from datetime import datetime
from dataclasses import asdict

try:
    from fastapi import WebSocket, WebSocketDisconnect
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Set[WebSocket] = set()
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if client_id:
            self.connection_metadata[client_id] = {
                'websocket': websocket,
                'connected_at': datetime.utcnow().isoformat(),
                'message_count': 0
            }
    
    async def disconnect(self, websocket: WebSocket, client_id: str = None):
        """Unregister a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.discard(websocket)
        
        if client_id and client_id in self.connection_metadata:
            del self.connection_metadata[client_id]
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_personal(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send message to specific client"""
        try:
            message_json = json.dumps(message, default=str)
            await websocket.send_text(message_json)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def send_update(self, 
                         message_type: str,
                         data: Dict[str, Any],
                         broadcast: bool = True):
        """
        Send a formatted update message
        
        Args:
            message_type: Type of message ('analysis', 'alert', 'status', etc.)
            data: Message data
            broadcast: Whether to broadcast to all or just store
        """
        message = {
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'data': data
        }
        
        if broadcast:
            await self.broadcast(message)
        
        return message


class RealtimeAnalyzer:
    """Real-time analysis handler"""
    
    def __init__(self, connection_manager: ConnectionManager):
        """Initialize real-time analyzer"""
        self.manager = connection_manager
        self.analysis_results = []
        self.max_history = 100
    
    async def process_and_stream(self, 
                                 repository: str,
                                 analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process analysis and stream results
        
        Args:
            repository: Repository being analyzed
            analysis_data: Analysis results to stream
        
        Returns:
            Formatted message
        """
        # Prepare data
        processed_data = {
            'repository': repository,
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'metrics': analysis_data.get('metrics'),
            'signal_count': len(analysis_data.get('signals', [])),
            'alerts': self._extract_alerts(analysis_data),
            'anomalies': analysis_data.get('anomalies', []),
            'ml_insights': analysis_data.get('ml_insights')
        }
        
        # Store in history
        self._add_to_history(processed_data)
        
        # Send update
        message = await self.manager.send_update(
            'analysis_complete',
            processed_data,
            broadcast=True
        )
        
        return message
    
    def _extract_alerts(self, analysis_data: Dict[str, Any]) -> list:
        """Extract high-priority alerts from analysis"""
        alerts = []
        signals = analysis_data.get('signals', [])
        
        # Get urgent signals
        urgent = [s for s in signals if s.get('status') == 'Urgent']
        
        for signal in urgent:
            alerts.append({
                'id': signal.get('id'),
                'message': signal.get('message'),
                'timestamp': signal.get('timestamp'),
                'severity': 'high' if signal.get('nlp', {}).get('is_bug') else 'medium'
            })
        
        return alerts
    
    def _add_to_history(self, data: Dict[str, Any]):
        """Add analysis to history (keep last N)"""
        self.analysis_results.append(data)
        if len(self.analysis_results) > self.max_history:
            self.analysis_results.pop(0)
    
    async def stream_signal(self, signal: Dict[str, Any]):
        """Stream a new signal in real-time"""
        message = {
            'type': 'new_signal',
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'data': signal
        }
        await self.manager.broadcast(message)
    
    async def stream_alert(self, alert: Dict[str, Any]):
        """Stream an alert in real-time"""
        message = {
            'type': 'alert',
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'severity': alert.get('severity', 'medium'),
            'data': alert
        }
        await self.manager.broadcast(message)
    
    async def stream_metric_update(self, metric_name: str, value: float):
        """Stream metric update"""
        message = {
            'type': 'metric_update',
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'metric': metric_name,
            'value': value
        }
        await self.manager.broadcast(message)


# Global connection manager and analyzer
_connection_manager = None
_realtime_analyzer = None


def get_connection_manager() -> ConnectionManager:
    """Get or create global connection manager"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_realtime_analyzer() -> RealtimeAnalyzer:
    """Get or create global realtime analyzer"""
    global _realtime_analyzer
    if _realtime_analyzer is None:
        manager = get_connection_manager()
        _realtime_analyzer = RealtimeAnalyzer(manager)
    return _realtime_analyzer
