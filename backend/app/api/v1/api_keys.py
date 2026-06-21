from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.api_key import ApiKeyCreate, ApiKeyRead, ApiKeyReveal
from app.schemas.user import User
from app.services.api_key_service import ApiKeyService


router = APIRouter()


@router.get("", response_model=list[ApiKeyRead])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiKeyService(db).list(current_user.id)


@router.post("", response_model=ApiKeyRead, status_code=status.HTTP_201_CREATED)
def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiKeyService(db).create(
        user_id=current_user.id,
        label=payload.label,
        provider=payload.provider,
        api_key=payload.api_key,
    )


@router.get("/{api_key_id}/reveal", response_model=ApiKeyReveal)
def reveal_api_key(
    api_key_id: int,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return {
        "id": api_key_id,
        "api_key": ApiKeyService(db).reveal(
            user_id=current_user.id,
            api_key_id=api_key_id,
        ),
    }


@router.put("/{api_key_id}/select", response_model=ApiKeyRead)
def select_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiKeyService(db).select(
        user_id=current_user.id,
        api_key_id=api_key_id,
    )


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ApiKeyService(db).delete(
        user_id=current_user.id,
        api_key_id=api_key_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
