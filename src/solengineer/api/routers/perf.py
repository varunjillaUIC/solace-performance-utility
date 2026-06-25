# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from solengineer.api import state
# from solengineer.perf.perf_tester import PerfTester

# router = APIRouter(prefix="/api")


# class PerfRequest(BaseModel):
#     topic: str
#     message_count: int = 1000
#     message_size: int = 256


# @router.post("/perf")
# def run_perf(req: PerfRequest):
#     service = state.get_service()
#     if not service:
#         raise HTTPException(status_code=400, detail="Not connected to broker")
#     tester = PerfTester(service)
#     results = tester.run(req.topic, req.message_count, req.message_size)
#     return results


#updated with some extra featueres


# from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
# from pydantic import BaseModel
# from solengineer.api import state
# from solengineer.perf.perf_tester import PerfTester
# import asyncio
# import threading
# import json
# from datetime import datetime

# # HTTP routes use /api prefix, WebSocket does NOT
# router = APIRouter()

# _current_tester: PerfTester | None = None


# class PerfRequest(BaseModel):
#     target: str
#     target_type: str = "topic"
#     message_count: int = 1000
#     message_size: int = 256
#     message_template: str = ""


# @router.post("/api/perf")
# def run_perf(req: PerfRequest):
#     service = state.get_service()
#     if not service:
#         raise HTTPException(status_code=400, detail="Not connected to broker")
#     tester = PerfTester(service)
#     results = tester.run(
#         target=req.target,
#         target_type=req.target_type,
#         message_count=req.message_count,
#         message_size=req.message_size,
#         message_template=req.message_template
#     )
#     return results


# @router.post("/api/perf/stop")
# def stop_perf():
#     global _current_tester
#     if _current_tester:
#         _current_tester.stop()
#     return {"status": "stopped"}


# @router.websocket("/ws/perf")
# async def perf_ws(websocket: WebSocket):
#     global _current_tester
#     await websocket.accept()

#     service = state.get_service()
#     if not service:
#         await websocket.send_json({"error": "Not connected to broker"})
#         await websocket.close()
#         return

#     try:
#         config = await asyncio.wait_for(websocket.receive_text(), timeout=10)
#         req = json.loads(config)
#     except Exception:
#         await websocket.close()
#         return

#     tester = PerfTester(service)
#     _current_tester = tester
#     results_holder = {}
#     loop = asyncio.get_event_loop()

#     def on_progress(received, total, elapsed, tps):
#         asyncio.run_coroutine_threadsafe(
#             websocket.send_json({
#                 "type": "progress",
#                 "received": received,
#                 "total": total,
#                 "elapsed": elapsed,
#                 "tps": tps,
#                 "percent": round(received / total * 100, 1)
#             }),
#             loop
#         )

#     def run_test():
#         try:
#             results_holder["data"] = tester.run(
#                 target=req.get("target", "perf/test"),
#                 target_type=req.get("target_type", "topic"),
#                 message_count=req.get("message_count", 1000),
#                 message_size=req.get("message_size", 256),
#                 message_template=req.get("message_template", ""),
#                 on_progress=on_progress
#             )
#         except Exception as e:
#             results_holder["error"] = str(e)

#     thread = threading.Thread(target=run_test)
#     thread.start()

#     try:
#         while thread.is_alive():
#             await asyncio.sleep(0.3)
#         thread.join()

#         if "error" in results_holder:
#             await websocket.send_json({
#                 "type": "error",
#                 "error": results_holder["error"]
#             })
#         elif "data" in results_holder:
#             await websocket.send_json({
#                 "type": "complete",
#                 "results": results_holder["data"],
#                 "timestamp": datetime.now().isoformat()
#             })
#     except WebSocketDisconnect:
#         tester.stop()
#     finally:
#         try:
#             await websocket.close()
#         except Exception:
#             pass


# 21-06-2026

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from solengineer.api import state
from solengineer.perf.perf_tester import PerfTester
import asyncio
import threading
import json
from datetime import datetime

router = APIRouter()

_current_tester: PerfTester | None = None


class PerfRequest(BaseModel):
    target: str
    target_type: str = "topic"
    message_count: int = 1000
    message_size: int = 256
    message_template: str = ""
    delivery_mode: str = "direct"
    rate_limit: int = 0
    window_size: int = 50


@router.post("/api/perf")
def run_perf(req: PerfRequest):
    service = state.get_service()
    if not service:
        raise HTTPException(status_code=400, detail="Not connected to broker")
    tester = PerfTester(service)
    results = tester.run(
        target=req.target,
        target_type=req.target_type,
        message_count=req.message_count,
        message_size=req.message_size,
        message_template=req.message_template,
        delivery_mode=req.delivery_mode,
        rate_limit=req.rate_limit,
        window_size=req.window_size
    )
    return results


@router.post("/api/perf/stop")
def stop_perf():
    global _current_tester
    if _current_tester:
        _current_tester.stop()
    return {"status": "stopped"}


@router.websocket("/ws/perf")
async def perf_ws(websocket: WebSocket):
    global _current_tester
    await websocket.accept()

    service = state.get_service()
    if not service:
        await websocket.send_json({"error": "Not connected to broker"})
        await websocket.close()
        return

    try:
        config = await asyncio.wait_for(websocket.receive_text(), timeout=10)
        req = json.loads(config)
    except Exception:
        await websocket.close()
        return

    tester = PerfTester(service)
    _current_tester = tester
    results_holder = {}
    loop = asyncio.get_event_loop()

    def on_progress(received, total, elapsed, tps):
        asyncio.run_coroutine_threadsafe(
            websocket.send_json({
                "type": "progress",
                "received": received,
                "total": total,
                "elapsed": elapsed,
                "tps": tps,
                "percent": round(received / total * 100, 1)
            }),
            loop
        )

    def run_test():
        try:
            results_holder["data"] = tester.run(
                target=req.get("target", "perf/test"),
                target_type=req.get("target_type", "topic"),
                message_count=req.get("message_count", 1000),
                message_size=req.get("message_size", 256),
                message_template=req.get("message_template", ""),
                delivery_mode=req.get("delivery_mode", "direct"),
                rate_limit=req.get("rate_limit", 0),
                window_size=req.get("window_size", 50),
                on_progress=on_progress
            )
        except Exception as e:
            results_holder["error"] = str(e)

    thread = threading.Thread(target=run_test)
    thread.start()

    try:
        while thread.is_alive():
            await asyncio.sleep(0.3)
        thread.join()

        if "error" in results_holder:
            await websocket.send_json({"type": "error", "error": results_holder["error"]})
        elif "data" in results_holder:
            await websocket.send_json({
                "type": "complete",
                "results": results_holder["data"],
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        tester.stop()
    finally:
        try:
            await websocket.close()
        except Exception:
            pass