"""
Base agent class for all worker agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

import structlog

from core.events import EventBus

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all worker agents."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.running = False
        self.logger = logger.bind(agent=self.__class__.__name__)
    
    async def start(self) -> None:
        """Start the agent."""
        self.running = True
        self.logger.info("Starting agent")
        await self.setup()
        await self.subscribe_to_events()
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.running = False
        self.logger.info("Stopping agent")
        await self.cleanup()
    
    @abstractmethod
    async def setup(self) -> None:
        """Setup the agent (override in subclasses)."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup the agent (override in subclasses)."""
        pass
    
    @abstractmethod
    async def subscribe_to_events(self) -> None:
        """Subscribe to relevant events (override in subclasses)."""
        pass
    
    async def publish_event(self, subject: str, data: Dict[str, Any]) -> None:
        """Publish an event."""
        await self.event_bus.publish(subject, data)
        self.logger.info("Published event", subject=subject)
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Handle errors and publish error events."""
        self.logger.error("Agent error", error=str(error), context=context)
        
        await self.publish_event("error.agent", {
            "agent": self.__class__.__name__,
            "error": str(error),
            "context": context,
        })
