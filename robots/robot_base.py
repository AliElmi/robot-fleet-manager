import asyncio
import websockets
import json

class RobotBase:
    def __init__(self, robot_id, manager_url):
        self.robot_id = robot_id
        self.manager_url = manager_url

    async def connect(self):
        while True:
            try:
                print(f"{self.robot_id} trying to connect...")
                ws = await websockets.connect(self.manager_url)
                print(f"{self.robot_id} connected to manager")
                return ws

            except Exception as e:
                print(f"{self.robot_id} connection failed: {e}")
                print("Retrying in 3 seconds...")
                await asyncio.sleep(3)

    async def run(self):
        while True:
            ws = await self.connect()

            try:
                while True:
                    message = await ws.recv()
                    data = json.loads(message)

                    # -------------------------
                    # RESET COMMAND
                    # -------------------------
                    if "command" in data and data["command"] == "reset":
                        print(f"{self.robot_id} received RESET command")
                        await asyncio.sleep(1)
                        print(f"{self.robot_id} reset complete")

                        # ارسال پیام reset_done
                        await ws.send(json.dumps({
                            "event": "reset_done"
                        }))
                        continue

                    # -------------------------
                    # TASK RECEIVED
                    # -------------------------
                    if "task_id" in data:
                        task_id = data["task_id"]
                        task = data["task"]

                        print(f"{self.robot_id} received task: {task}")

                        # شبیه‌سازی انجام کار
                        await asyncio.sleep(2)

                        result = {
                            "task_id": task_id,
                            "status": "done",
                            "output": f"{self.robot_id} executed: {task}"
                        }

                        await ws.send(json.dumps(result))
                        continue

            except Exception as e:
                print(f"{self.robot_id} lost connection: {e}")
                print("Reconnecting...")
                await asyncio.sleep(2)
