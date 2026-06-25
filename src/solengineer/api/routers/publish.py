from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from solengineer.api import state
from solengineer.publisher.topic_publisher import TopicPublisher
import json, os
from datetime import datetime

router = APIRouter(prefix="/api")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "../../data/history.json")

_publisher: TopicPublisher | None = None


def get_publisher():
    global _publisher
    service = state.get_service()
    if not service:
        raise HTTPException(status_code=400, detail="Not connected to broker")
    if _publisher is None:
        _publisher = TopicPublisher(service)
    return _publisher


def reset_publisher():
    global _publisher
    _publisher = None


class PublishRequest(BaseModel):
    topic: str
    message: str


def save_history(topic: str, message: str):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                content = f.read().strip()
                history = json.loads(content) if content else []
        except (json.JSONDecodeError, IOError):
            history = []
    history.insert(0, {
        "topic": topic,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[:100], f, indent=2)


@router.post("/publish")
def publish(req: PublishRequest):
    publisher = get_publisher()
    publisher.publish(req.topic, req.message)
    save_history(req.topic, req.message)
    return {"status": "published", "topic": req.topic}


@router.get("/history")
def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE) as f:
            content = f.read().strip()
            return json.loads(content) if content else []
    except (json.JSONDecodeError, IOError):
        return []


@router.delete("/history")
def clear_history():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
    return {"status": "cleared"}