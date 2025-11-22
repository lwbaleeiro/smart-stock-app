from fastapi import APIRouter

router = APIRouter()

@router.get("")
def health_check():
    """
    Verifica a saúde da aplicação.
    """
    return {"status": "ok"}
