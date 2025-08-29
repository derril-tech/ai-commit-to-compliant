"""
ProdSprints AI Workers
Event-driven agents for repo analysis, IaC, CI/CD, and release orchestration.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import nats
import structlog
from fastapi import FastAPI

from agents import (
    RepoAuditorAgent,
    IaCAgent,
    CICDAgent,
    TestAgent,
    SecurityAgent,
    PerfAgent,
    ReleaseOrchestratorAgent,
    RollbackAgent,
)
from core.config import settings
from core.events import EventBus


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("🚀 ProdSprints AI Workers starting...")
    
    # Initialize NATS connection
    nc = await nats.connect(settings.NATS_URL)
    event_bus = EventBus(nc)
    
    # Initialize and start agents
    agents = [
        RepoAuditorAgent(event_bus),
        IaCAgent(event_bus),
        CICDAgent(event_bus),
        TestAgent(event_bus),
        SecurityAgent(event_bus),
        PerfAgent(event_bus),
        ReleaseOrchestratorAgent(event_bus),
        RollbackAgent(event_bus),
    ]
    
    # Start all agents
    tasks = []
    for agent in agents:
        task = asyncio.create_task(agent.start())
        tasks.append(task)
        logger.info("Started agent", agent=agent.__class__.__name__)
    
    app.state.event_bus = event_bus
    app.state.agents = agents
    app.state.tasks = tasks
    
    yield
    
    # Shutdown
    logger.info("🛑 ProdSprints AI Workers shutting down...")
    
    # Stop agents
    for agent in agents:
        await agent.stop()
    
    # Cancel tasks
    for task in tasks:
        task.cancel()
    
    # Close NATS connection
    await nc.close()


app = FastAPI(
    title="ProdSprints AI Workers",
    description="Event-driven agents for deployment orchestration",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "prodsprints-workers",
        "agents": len(app.state.agents) if hasattr(app.state, "agents") else 0,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ProdSprints AI Workers",
        "version": "0.1.0",
        "agents": [
            agent.__class__.__name__ for agent in app.state.agents
        ] if hasattr(app.state, "agents") else [],
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
