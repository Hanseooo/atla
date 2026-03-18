from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Union, Dict, Any, NoReturn

from app.api.deps import get_optional_user
from app.models.user import UserProfile
from app.services.chat_service import ChatService
from app.schemas.chat_api import ChatRequest, ClarificationResponse, ItineraryResponse, ChatSession, ErrorResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _raise_for_chat_error(response: ErrorResponse) -> NoReturn:
    if response.error_code == "SESSION_ACCESS_DENIED":
        raise HTTPException(status_code=403, detail=response.message)
    raise HTTPException(status_code=400, detail=response.message)

@router.post("/", response_model=Union[ClarificationResponse, ItineraryResponse])
async def chat(
    request: ChatRequest,
    current_user: Optional[UserProfile] = Depends(get_optional_user)
):
    """
    Process chat message and return response.
    
    Returns clarification questions if info missing,
    or complete itinerary if all info provided.
    """
    service = ChatService()
    
    user_id = current_user.id if current_user else None
    
    response = await service.process_message(
        message=request.message,
        session_id=request.session_id,
        user_id=user_id
    )
    
    if isinstance(response, ErrorResponse):
        _raise_for_chat_error(response)
    
    return response

@router.post("/{session_id}/clarify", response_model=Union[ClarificationResponse, ItineraryResponse])
async def submit_clarification(
    session_id: str,
    answers: Dict[str, Any] = Body(...),
    current_user: Optional[UserProfile] = Depends(get_optional_user)
):
    """Submit answers to clarification questions"""
    service = ChatService()
    user_id = current_user.id if current_user else None
    
    response = await service.process_clarification(
        session_id=session_id,
        answers=answers,
        user_id=user_id
    )
    
    if isinstance(response, ErrorResponse):
        _raise_for_chat_error(response)
        
    return response


@router.post("/{session_id}/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary_for_session(
    session_id: str,
    current_user: Optional[UserProfile] = Depends(get_optional_user)
):
    """Generate itinerary for an existing complete session intent."""
    service = ChatService()
    user_id = current_user.id if current_user else None

    response = await service.generate_itinerary_for_session(
        session_id=session_id,
        user_id=user_id,
    )

    if isinstance(response, ErrorResponse):
        _raise_for_chat_error(response)

    return response

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_history(
    session_id: str,
    current_user: Optional[UserProfile] = Depends(get_optional_user)
):
    """Get chat session history"""
    service = ChatService()
    user_id = current_user.id if current_user else None

    session = await service.get_session(session_id, user_id)
    if isinstance(session, ErrorResponse):
        _raise_for_chat_error(session)

    if session is None or (not session.current_intent and not session.last_clarification):
        raise HTTPException(status_code=404, detail="Session not found")
        
    return session
