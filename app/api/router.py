from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, discovery, dna, friends, groups, health, match, orders, payments, ratings, tickets, users, verification, votes

api_router = APIRouter()


def register_routes(router: APIRouter) -> None:
    router.include_router(health.router, tags=["health"])
    router.include_router(auth.router, prefix="/auth", tags=["auth"])
    router.include_router(users.router, prefix="/users", tags=["users"])
    router.include_router(friends.router, prefix="/friends", tags=["friends"])
    router.include_router(dna.router, prefix="/dna", tags=["dna"])
    router.include_router(match.router, prefix="/match", tags=["match"])
    router.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
    router.include_router(groups.router, prefix="/groups", tags=["groups"])
    router.include_router(votes.router, prefix="/votes", tags=["votes"])
    router.include_router(orders.router, prefix="/orders", tags=["orders"])
    router.include_router(payments.router, prefix="/payments", tags=["payments"])
    router.include_router(verification.router, prefix="/verification", tags=["verification"])
    router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
    router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
    router.include_router(admin.router, prefix="/admin", tags=["admin"])


tm_v1_router = APIRouter(prefix="/v1/tm")
register_routes(tm_v1_router)
api_router.include_router(tm_v1_router)
