import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import check_resume_access
from app.core import database as core_db
from app.core.collaboration_manager import collaboration_ws_manager
from app.core.security import decode_token
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-Time Collaboration WebSocket"])


@router.websocket("/ws/resumes/{resume_id}")
async def collaboration_websocket_endpoint(
    websocket: WebSocket,
    resume_id: str,
    token: str = Query(..., description="JWT Bearer token for WebSocket handshake"),
):
    # 1. Authenticate Token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        logger.warning(f"WebSocket rejected: Invalid token for resume {resume_id}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Authorize User Access to Resume
    session_factory = getattr(core_db, "async_session_maker", None)
    async with session_factory() as db:
        u_res = await db.execute(select(User).where(User.id == user_id))
        user = u_res.scalars().first()
        if not user or user.account_status != "active":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            resume, effective_role = await check_resume_access(
                resume_id=resume_id,
                current_user=user,
                db=db,
                min_role="viewer",
            )
        except Exception as e:
            logger.warning(f"WebSocket unauthorized: User {user.id} cannot access resume {resume_id}: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    # 3. Connect & Register in Collaboration Manager
    conn_id = await collaboration_ws_manager.connect(
        resume_id=resume_id,
        user_id=user.id,
        user_email=user.email,
        websocket=websocket,
    )

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                msg = json.loads(raw_text)
                msg_type = msg.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    })

                elif msg_type == "cursor_focus":
                    # Broadcast cursor focus section to other collaborators
                    await collaboration_ws_manager.broadcast(
                        resume_id=resume_id,
                        message={
                            "type": "collaborator_focus",
                            "user_id": user.id,
                            "user_email": user.email,
                            "section": msg.get("section"),
                            "selected_text": msg.get("selected_text"),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        exclude_connection_id=conn_id,
                    )

                elif msg_type in ["comment_created", "suggestion_created", "revision_committed"]:
                    # Distribute live updates
                    await collaboration_ws_manager.broadcast(
                        resume_id=resume_id,
                        message={
                            "type": msg_type,
                            "user_id": user.id,
                            "user_email": user.email,
                            "data": msg.get("data", {}),
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        exclude_connection_id=conn_id,
                    )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format."})

    except WebSocketDisconnect:
        await collaboration_ws_manager.disconnect(resume_id, conn_id)
    except Exception as e:
        logger.error(f"WebSocket exception in session {conn_id}: {e}")
        await collaboration_ws_manager.disconnect(resume_id, conn_id)
