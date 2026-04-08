import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime
import json

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class RealtimeMonitor:
    """Manages real-time monitoring and WebSocket connections."""
    
    def __init__(self):
        self.clients: Dict[str, WebSocket] = {}
        self.running = False
        self._tasks = []
    
    async def start(self):
        """Start the realtime monitor."""
        self.running = True
        
        # Start background tasks
        self._tasks.append(
            asyncio.create_task(self._monitor_alerts())
        )
        self._tasks.append(
            asyncio.create_task(self._monitor_scan_progress())
        )
        
        logger.info("Realtime monitor started")
    
    async def stop(self):
        """Stop the realtime monitor."""
        self.running = False
        
        for task in self._tasks:
            task.cancel()
        
        # Close all WebSocket connections
        for client_id, ws in self.clients.items():
            try:
                await ws.close()
            except:
                pass
        
        self.clients.clear()
        logger.info("Realtime monitor stopped")
    
    async def add_client(self, client_id: str, websocket: WebSocket):
        """Add a WebSocket client."""
        self.clients[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total clients: {len(self.clients)}")
    
    async def remove_client(self, client_id: str):
        """Remove a WebSocket client."""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.clients:
            return
        
        disconnected = []
        for client_id, ws in self.clients.items():
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            await self.remove_client(client_id)
    
    async def send_to_client(self, client_id: str, message: dict):
        """Send a message to a specific client."""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {e}")
                await self.remove_client(client_id)
    
    async def _monitor_alerts(self):
        """Monitor for new alerts and broadcast them."""
        while self.running:
            try:
                # Check for new alerts in database
                # This would query the MonitoringAlert table
                await asyncio.sleep(5)  # Check every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert monitor: {e}")
    
    async def _monitor_scan_progress(self):
        """Monitor running scans and broadcast progress updates."""
        while self.running:
            try:
                # Check for running scans and broadcast progress
                # This would query the ScanJob table
                await asyncio.sleep(2)  # Check every 2 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scan progress monitor: {e}")
    
    async def notify_scan_update(self, scan_id: str, status: str, progress: float):
        """Notify clients about scan progress."""
        await self.broadcast({
            "type": "scan_update",
            "data": {
                "scan_id": scan_id,
                "status": status,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_alert(self, alert_type: str, title: str, severity: str, data: dict):
        """Notify clients about a new alert."""
        await self.broadcast({
            "type": "alert",
            "data": {
                "alert_type": alert_type,
                "title": title,
                "severity": severity,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    async def notify_threat_detected(self, app_id: int, threat_type: str, details: dict):
        """Notify clients about a detected threat."""
        await self.broadcast({
            "type": "threat_detected",
            "data": {
                "app_id": app_id,
                "threat_type": threat_type,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
