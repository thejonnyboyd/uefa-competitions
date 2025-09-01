from fastapi import FastAPI, WebSocket
from engine.schemas import DrawRequest, DrawResult
from engine.config.reader import load_config
from engine.service import run_draw

app = FastAPI(title="UEFA Draw Engine")

@app.get("/config/{competition}")
def get_config(competition: str):
    return load_config(competition).model_dump()

@app.post("/draw", response_model=DrawResult)
def draw(req: DrawRequest):
    return run_draw(req)

@app.websocket("/live")
async def live(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"type": "todo", "payload":"wire playback with a pre-solved draw"})
    await ws.close()