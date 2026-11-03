import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import WebSocket
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


class CollaborationConnectionManager:
    """
    Manages active WebSocket connections for live resume collaboration.
    Integrates Redis Pub/Sub for horizontal multi-worker scaling with
    in-process broadcast fallback for local resilience.
    """

    def __init__(self):
        # resume_id -> {connection_id: WebSocket}
        self._rooms: Dict[str, Dict[str, WebSocket]] = {}
        # resume_id -> {connection_id: {"user_id": ..., "email": ...}}
        self._user_metadata: Dict[str, Dict[str, Dict[str, str]]] = {}
        # resume_id -> asyncio.Task (for Redis pub/sub listener)
        self._redis_listeners: Dict[str, asyncio.Task] = {}

    async def connect(
        self, resume_id: str, user_id: str, user_email: str, websocket: WebSocket
    ) -> str:
        await websocket.accept()
        connection_id = str(uuid.uuid4())

        if resume_id not in self._rooms:
            self._rooms[resume_id] = {}
            self._user_metadata[resume_id] = {}
            # Start Redis listener for this resume room if Redis is active
            self._start_redis_listener(resume_id)

        self._rooms[resume_id][connection_id] = websocket
        self._user_metadata[resume_id][connection_id] = {
            "connection_id": connection_id,
            "user_id": user_id,
            "user_email": user_email,
            "joined_at": datetime.now(timezone.utc).isoformat(),
        }

        # Broadcast collaborator joined
        join_event = {
            "type": "collaborator_joined",
            "user_id": user_id,
            "user_email": user_email,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.broadcast(resume_id, join_event)

        # Send current active collaborators to new connection
        active_collaborators = self.get_active_collaborators(resume_id)
        await websocket.send_json({
            "type": "active_collaborators",
            "collaborators": active_collaborators,
        })

        logger.info(f"User {user_email} connected to resume {resume_id} (conn: {connection_id})")
        return connection_id

    async def disconnect(self, resume_id: str, connection_id: str) -> None:
        user_meta = None
        if resume_id in self._user_metadata and connection_id in self._user_metadata[resume_id]:
            user_meta = self._user_metadata[resume_id].pop(connection_id)

        if resume_id in self._rooms and connection_id in self._rooms[resume_id]:
            self._rooms[resume_id].pop(connection_id, None)

        if resume_id in self._rooms and not self._rooms[resume_id]:
            del self._rooms[resume_id]
            del self._user_metadata[resume_id]
            # Stop Redis listener if room is empty
            if resume_id in self._redis_listeners:
                self._redis_listeners[resume_id].cancel()
                del self._redis_listeners[resume_id]

        if user_meta:
            leave_event = {
                "type": "collaborator_left",
                "user_id": user_meta["user_id"],
                "user_email": user_meta["user_email"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await self.broadcast(resume_id, leave_event)

        logger.info(f"Connection {connection_id} disconnected from resume {resume_id}")

    async def broadcast(
        self,
        resume_id: str,
        message: Dict[str, Any],
        exclude_connection_id: Optional[str] = None,
    ) -> None:
        """
        Broadcasts message to local WebSocket connections and publishes to Redis.
        """
        raw_msg = json.dumps(message)

        # 1. Publish to Redis for multi-instance distribution
        try:
            r = await get_redis()
            if r:
                await r.publish(f"resume:{resume_id}:events", raw_msg)
        except Exception as e:
            logger.warning(f"Failed to publish to Redis Pub/Sub: {e}")

        # 2. Local broadcast
        await self._broadcast_local(resume_id, message, exclude_connection_id)

    async def _broadcast_local(
        self,
        resume_id: str,
        message: Dict[str, Any],
        exclude_connection_id: Optional[str] = None,
    ) -> None:
        if resume_id not in self._rooms:
            return

        dead_connections = []
        for conn_id, ws in self._rooms[resume_id].items():
            if exclude_connection_id and conn_id == exclude_connection_id:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(conn_id)

        for dead_id in dead_connections:
            await self.disconnect(resume_id, dead_id)

    def get_active_collaborators(self, resume_id: str) -> List[Dict[str, str]]:
        if resume_id not in self._user_metadata:
            return []
        # Return unique users by user_id
        seen = set()
        collaborators = []
        for meta in self._user_metadata[resume_id].values():
            uid = meta["user_id"]
            if uid not in seen:
                seen.add(uid)
                collaborators.append({
                    "user_id": uid,
                    "user_email": meta["user_email"],
                    "joined_at": meta["joined_at"],
                })
        return collaborators

    def _start_redis_listener(self, resume_id: str) -> None:
        task = asyncio.create_task(self._listen_redis_channel(resume_id))
        self._redis_listeners[resume_id] = task

    async def _listen_redis_channel(self, resume_id: str) -> None:
        """
        Listens to Redis Pub/Sub channel for cross-instance broadcasts.
        """
        try:
            r = await get_redis()
            if not r:
                return
            pubsub = r.pubsub()
            await pubsub.subscribe(f"resume:{resume_id}:events")
            async for raw_message in pubsub.listen():
                if raw_message and raw_message.get("type") == "message":
                    data = raw_message.get("data")
                    if isinstance(data, str):
                        try:
                            msg_dict = json.loads(data)
                            await self._broadcast_local(resume_id, msg_dict)
                        except Exception as e:
                            logger.error(f"Error handling Redis Pub/Sub message: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.warning(f"Redis Pub/Sub listener ended for resume {resume_id}: {e}")


# Global connection manager singleton
collaboration_ws_manager = CollaborationConnectionManager()

