from fastapi import APIRouter

router = APIRouter()


@router.post('/groups/{group_id}/assign-bus')
def assign_bus(group_id: int) -> dict:
    return {'message': f'TODO: assign bus for group {group_id}'}
