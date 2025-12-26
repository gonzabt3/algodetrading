"""
FastAPI Application - Clean Architecture
Main entry point following SOLID principles
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import Base, engine
from api.services import register_default_strategies
from api.routers import brokers, strategies as strategy_router
from api.routers import pair_data, backtests, market_data


def create_app() -> FastAPI:
    """
    Application factory pattern - creates and configures FastAPI app
    Follows Dependency Inversion Principle
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize app
    app = FastAPI(
        title="Algorithmic Trading Dashboard",
        description="API for backtesting trading strategies",
        version="2.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register strategies
    register_default_strategies()
    
    # Include routers (Interface Segregation Principle)
    app.include_router(strategy_router.router)
    app.include_router(brokers.router)
    app.include_router(pair_data.router)
    app.include_router(backtests.router)
    app.include_router(market_data.router)
    
    return app


# Create app instance
app = create_app()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Trading API started")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Trading API shutting down")


@app.get("/")
async def root():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "online",
        "message": "Trading API is running",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }
