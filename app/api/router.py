from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, discovery, groups, health, orders, payments, ratings, tickets, users, votes

api_router = APIRouter()
v1_router = APIRouter(prefix="/v1")

v1_router.include_router(health.router, tags=["health"])
v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
v1_router.include_router(users.router, prefix="/users", tags=["users"])
v1_router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
v1_router.include_router(groups.router, prefix="/groups", tags=["groups"])
v1_router.include_router(votes.router, prefix="/votes", tags=["votes"])
v1_router.include_router(orders.router, prefix="/orders", tags=["orders"])
v1_router.include_router(payments.router, prefix="/payments", tags=["payments"])
v1_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
v1_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])

api_router.include_router(v1_router)
