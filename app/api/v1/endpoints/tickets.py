from fastapi import APIRouter

router = APIRouter()


@router.post('/generate')
def generate_ticket() -> dict:
    return {'message': 'TODO: generate ticket'}


@router.post('/verify')
def verify_ticket() -> dict:
    return {'message': 'TODO: verify ticket'}
