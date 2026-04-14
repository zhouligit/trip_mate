from fastapi import APIRouter

router = APIRouter()


@router.post('')
def submit_rating() -> dict:
    return {'message': 'TODO: submit rating'}
