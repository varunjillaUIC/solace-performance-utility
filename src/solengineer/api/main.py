from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from solengineer.api import state
from solengineer.api.routers import publish, subscribe, queue, profiles, perf
import os

app = FastAPI(title="SolEngineer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(publish.router)
app.include_router(subscribe.router)
app.include_router(queue.router)
app.include_router(profiles.router)
app.include_router(perf.router)


class ConnectRequest(BaseModel):
    host: str
    vpn: str
    username: str
    password: str


@app.post("/api/connect")
def connect(req: ConnectRequest):
    try:
        state.init_service(req.host, req.vpn, req.username, req.password)
        return {"status": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
def status():
    return {"connected": state.get_service() is not None}


from solengineer.api.routers.publish import reset_publisher

@app.post("/api/disconnect")
def disconnect():
    reset_publisher()
    state.disconnect()
    return {"status": "disconnected"}


# Serve React build after: cd ui && npm run build
# ui_dist = os.path.join(os.path.dirname(__file__), "../../solengineer/ui/dist")
# if os.path.exists(ui_dist):
#     app.mount("/", StaticFiles(directory=ui_dist, html=True), name="ui")

# Serve React production build

ui_build = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "ui",
        "build"
    )
)

if os.path.exists(ui_build):
    app.mount(
        "/",
        StaticFiles(directory=ui_build, html=True),
        name="ui"
    )