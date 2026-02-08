import asyncio
from robot_base import RobotBase

robot = RobotBase(
    robot_id="robot_1",
    manager_url="ws://127.0.0.1:8000/ws/robot?robot_id=robot_1&key=MY_SECRET_KEY_123"

)

asyncio.run(robot.run())
