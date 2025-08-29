"""
Event bus for inter-agent communication.
"""

import json
from typing import Any, Callable, Dict

import nats
import structlog

logger = structlog.get_logger()


class EventBus:
    """NATS-based event bus for agent communication."""
    
    def __init__(self, nc: nats.NATS):
        self.nc = nc
        self.subscriptions: Dict[str, Any] = {}
    
    async def publish(self, subject: str, data: Dict[str, Any]) -> None:
        """Publish an event."""
        try:
            payload = json.dumps(data).encode()
            await self.nc.publish(subject, payload)
            logger.info("Published event", subject=subject, data=data)
        except Exception as e:
            logger.error("Failed to publish event", subject=subject, error=str(e))
            raise
    
    async def subscribe(self, subject: str, handler: Callable) -> None:
        """Subscribe to events on a subject."""
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                logger.info("Received event", subject=subject, data=data)
                await handler(data)
            except Exception as e:
                logger.error("Error handling event", subject=subject, error=str(e))
        
        sub = await self.nc.subscribe(subject, cb=message_handler)
        self.subscriptions[subject] = sub
        logger.info("Subscribed to subject", subject=subject)
    
    async def unsubscribe(self, subject: str) -> None:
        """Unsubscribe from a subject."""
        if subject in self.subscriptions:
            await self.subscriptions[subject].unsubscribe()
            del self.subscriptions[subject]
            logger.info("Unsubscribed from subject", subject=subject)
