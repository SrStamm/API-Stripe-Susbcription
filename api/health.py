"""Health check endpoints for monitoring."""
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from celery import Celery
import redis
import os
from dotenv import load_dotenv

from db.session import engine, get_session
from core.logger import logger

load_dotenv()

router = APIRouter(prefix="", tags=["health"])


def get_redis_client() -> redis.Redis:
    """Get Redis client for health checks."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)


def get_celery_app() -> Celery:
    """Get Celery app for health checks."""
    from tasks.app import celery_app
    return celery_app


async def check_database() -> Dict[str, str]:
    """Check database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "message": "Database connected"}
    except Exception as e:
        logger.error("health_check_db_error", error=str(e))
        return {"status": "unhealthy", "message": f"Database error: {str(e)}"}


async def check_redis() -> Dict[str, str]:
    """Check Redis (Celery broker) connectivity."""
    try:
        r = get_redis_client()
        r.ping()
        return {"status": "healthy", "message": "Redis connected"}
    except Exception as e:
        logger.error("health_check_redis_error", error=str(e))
        return {"status": "unhealthy", "message": f"Redis error: {str(e)}"}


async def check_celery_workers() -> Dict[str, Any]:
    """Check Celery workers availability."""
    try:
        app = get_celery_app()
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats is None:
            return {"status": "unhealthy", "message": "No workers available"}
        
        # Get active workers
        active = inspect.active()
        registered = inspect.registered()
        
        return {
            "status": "healthy",
            "message": "Workers available",
            "worker_count": len(stats) if stats else 0,
            "active_tasks": len(active) if active else 0,
        }
    except Exception as e:
        logger.error("health_check_celery_error", error=str(e))
        return {"status": "unhealthy", "message": f"Celery error: {str(e)}"}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint.
    
    Returns overall health status based on all checks.
    """
    # Run all checks
    db_check = await check_database()
    redis_check = await check_redis()
    
    # Determine overall status
    all_healthy = (
        db_check["status"] == "healthy"
        and redis_check["status"] == "healthy"
    )
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": {
            "database": db_check,
            "redis": redis_check,
        },
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check - for Kubernetes readinessProbe.
    
    Must pass ALL checks to be ready.
    """
    db_check = await check_database()
    redis_check = await check_redis()
    celery_check = await check_celery_workers()
    
    all_healthy = (
        db_check["status"] == "healthy"
        and redis_check["status"] == "healthy"
        and celery_check["status"] == "healthy"
    )
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": {
            "database": db_check,
            "redis": redis_check,
            "celery": celery_check,
        },
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check - for Kubernetes livenessProbe.
    
    Simple check - app is running.
    """
    return {
        "status": "alive",
        "message": "Service is running",
    }


@router.get("/health/database")
async def database_health() -> Dict[str, str]:
    """Database-specific health check."""
    return await check_database()


@router.get("/health/celery")
async def celery_health() -> Dict[str, Any]:
    """Celery workers health check."""
    return await check_celery_workers()