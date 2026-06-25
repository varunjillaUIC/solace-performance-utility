from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from solengineer.api import state
from solengineer.queue.queue_consumer import QueueConsumer
import asyncio

router = APIRouter()


@router.websocket("/ws/queue")
async def queue_ws(websocket: WebSocket, queue_name: str):
    await websocket.accept()
    service = state.get_service()
    if not service:
        await websocket.send_json({"error": "Not connected"})
        await websocket.close()
        return

    consumer = QueueConsumer(service)
    consumer.start(queue_name)
    await websocket.send_json({"status": f"Listening on {queue_name}"})

    try:
        loop = asyncio.get_event_loop()
        while True:
            msg = await loop.run_in_executor(
                None, lambda: consumer.receive(timeout=3000)
            )
            if msg:
                await websocket.send_json({
                    "queue": queue_name,
                    "message": msg.get_payload_as_string()
                })
                consumer.ack(msg)
    except WebSocketDisconnect:
        pass
    finally:
        consumer.stop()