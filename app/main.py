from contextlib import asynccontextmanager
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import json
import threading
import time
from queue import PriorityQueue
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

# Database and Web Framework
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import redis
import jwt
from passlib.context import CryptContext

from app.api.endpoints import auth, organizations, clusters, deployments, monitoring
from app.db.base import Base, engine
from app.services.scheduler import scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://root:root@postgres:5432/ml_ops_db")
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis Setup for Queue Management
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", "redis_password"),
    decode_responses=True
)

# Create FastAPI app
app = FastAPI(
    title="MLOps Platform",
    description="Hypervisor-like service for ML deployments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(clusters.router, prefix="/clusters", tags=["Clusters"])
app.include_router(deployments.router, prefix="/deployments", tags=["Deployments"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    scheduler.start_scheduler()
    logger.info("Application startup complete")
    yield
    # Shutdown
    scheduler.stop_scheduler()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)