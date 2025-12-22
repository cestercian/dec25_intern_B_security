from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from apps.api.services.auth import get_current_user
from packages.shared.models import User, UserRead
from packages.shared.database import get_session

router = APIRouter()

class SaveTokensRequest(BaseModel):
    email: str
    google_id: str
    name: str
    refresh_token: str
    access_token: str  # Not saved, just for validation


@router.post("/save-tokens")
async def save_tokens(
    request: SaveTokensRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create or update a user record with the provided refresh token and return the saved user's id.
    
    If a user with the given email exists, update its `refresh_token`, `google_id`, and `name`; otherwise create a new user with those fields. The `access_token` in the request is accepted for validation but is not persisted.
    
    Parameters:
        request: Incoming payload containing `email`, `google_id`, `name`, `refresh_token`, and `access_token`.
        session: Database session used to query and persist the user (injected dependency).
    
    Returns:
        dict: A JSON-serializable mapping with keys `"status"` (value `"success"`) and `"user_id"` (the saved user's id as a string).
    """
    # Find or create user
    query = select(User).where(User.email == request.email)
    result = await session.exec(query)
    user = result.first()
    
    if not user:
        # Create new user
        user = User(
            email=request.email,
            google_id=request.google_id,
            name=request.name,
            refresh_token=request.refresh_token
        )
        session.add(user)
    else:
        # Update existing user's refresh_token
        user.refresh_token = request.refresh_token
        user.google_id = request.google_id
        user.name = request.name
        session.add(user)
    
    await session.commit()
    await session.refresh(user)
    
    return {"status": "success", "user_id": str(user.id)}


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)) -> User:
    """
    Return the current authenticated user.
    
    Returns:
        user (User): The authenticated user's model instance.
    """
    return user