from fastapi import FastAPI, WebSocket, WebSocketDisconnect,HTTPException
from typing import Dict
from datetime import datetime
from fastapi.responses import HTMLResponse
import asyncio
from manager.config import API_KEY
import json



dashboard_connections = []


app = FastAPI()

connected_robots: Dict[str, WebSocket] = {}
robot_status: Dict[str, dict] = {}

@app.websocket("/ws/robot")
async def robot_connection(ws: WebSocket):
    robot_id = ws.query_params.get("robot_id")
    key = ws.query_params.get("key")

    
    if key != API_KEY:
        await ws.close()
        return

    await ws.accept()

    connected_robots[robot_id] = ws
    robot_status[robot_id] = {
        "status": "connected",
        "last_seen": datetime.utcnow(),
        "current_task": None
    }

    try:
        while True:
            message = await ws.receive_text()
            print(f"Result from {robot_id}: {message}")
            data = json.loads(message) 
            # اگر پیام reset_done بود 
            if "event" in data and data["event"] == "reset_done":
                robot_status[robot_id]["status"] = "idle" 
                robot_status[robot_id]["current_task"] = None 
                continue

            # اگر پیام نتیجهٔ task بود 
            if "task_id" in data: 
                robot_status[robot_id]["status"] = "idle" 
                robot_status[robot_id]["current_task"] = None 
                print(f"Result from {robot_id}: {data}") 
                continue

    except WebSocketDisconnect:
        print(f"{robot_id} disconnected")
        robot_status[robot_id]["status"] = "disconnected" 
        robot_status[robot_id]["current_task"] = None 
        robot_status[robot_id]["last_seen"] = datetime.utcnow() 
        if robot_id in connected_robots: 
            del connected_robots[robot_id]

@app.post("/assign")
async def assign_task(robot_id: str, task: dict, key: str):
    if key != API_KEY:
        return {"error": "Invalid key"}

    if robot_id not in connected_robots:
        return {"error": "Robot not connected"}

    ws = connected_robots[robot_id]

    await ws.send_json({
        "task_id": f"task_{datetime.utcnow().timestamp()}",
        "task": task
    })

    robot_status[robot_id]["status"] = "busy"
    robot_status[robot_id]["current_task"] = task

    return {"message": "Task sent to robot"}


@app.get("/robots")
def get_status():
    return robot_status





@app.get("/dashboard")
def dashboard_page():
    with open("manager/dashboard.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/dashboard")
async def dashboard_ws(ws: WebSocket, key: str):
    if key != API_KEY: 
        await ws.close() 
        return
    await ws.accept()
    dashboard_connections.append(ws)

    try:
        while True:
            await asyncio.sleep(1)
            await ws.send_json(serialize_status(robot_status))

    except WebSocketDisconnect:
        dashboard_connections.remove(ws)


def serialize_status(data):
    result = {}
    for robot_id, info in data.items():
        result[robot_id] = {
            "status": info["status"],
            "last_seen": info["last_seen"].isoformat() if info["last_seen"] else None,
            "current_task": info["current_task"]
        }
    return result


@app.post("/reset")
async def reset_robot(robot_id: str, key: str):
    if key != API_KEY: 
        return {"error": "Invalid key"}
    if robot_id not in connected_robots:
        return {"error": "Robot not connected"}

    ws = connected_robots[robot_id]

    await ws.send_json({
        "command": "reset"
    })

    robot_status[robot_id]["status"] = "resetting"
    robot_status[robot_id]["current_task"] = None

    return {"message": f"{robot_id} reset command sent"}
