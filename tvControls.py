import asyncio
from flask import jsonify
from flask_login import current_user
from samsung import SamsungController 
from models import get_tv_ip


def run_tv_command(action_name: str):
    try:
        tv_ip = get_tv_ip(current_user.id)
        controller = SamsungController(host=tv_ip)

        action_map = {
            "power_toggle": controller.power_toggle,
            "volume_up": controller.volume_up,
            "volume_down": controller.volume_down,
            "sleep": controller.sleep,
            "channel_up": controller.channel_up,
            "channel_down": controller.channel_down,
        }
        
        if action_name not in action_map:
            return jsonify({"status": "errror", "message": f"Unknown action{action_name}"})
        
        asyncio.run(action_map[action_name]())
        return jsonify({"status": "success", "message": f"Action {action_name} executed successfully"}),200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
async def test_connection():
    tv_ip = get_tv_ip(current_user.id)
    controller = SamsungController(host=tv_ip)
    connected = await controller.connect()
    if connected:
        print("Sending commands to TV for testing connection...")
        await controller.volume_up()
        await controller.volume_down()
    else:
        print("Cannot proceed with the application. Please check your connection to the TV.")

