from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from solengineer.api import state
from solengineer.subscriber.topic_subscriber import TopicSubscriber
import asyncio

router = APIRouter()


@router.websocket("/ws/subscribe")
async def subscribe_ws(websocket: WebSocket, topic: str):
    await websocket.accept()
    service = state.get_service()
    if not service:
        await websocket.send_json({"error": "Not connected"})
        await websocket.close()
        return

    subscriber = TopicSubscriber(service)
    subscriber.start(topic)
    await websocket.send_json({"status": f"Subscribed to {topic}"})

    try:
        loop = asyncio.get_event_loop()
        while True:
            msg = await loop.run_in_executor(
                None, lambda: subscriber.receive(timeout=3000)
            )
            if msg:
                await websocket.send_json({
                    "topic": topic,
                    "message": msg.get_payload_as_string()
                })
    except WebSocketDisconnect:
        pass
    finally:
        subscriber.stop()