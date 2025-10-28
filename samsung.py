import os
import asyncio
from samsungtvws import SamsungTVWS
from api_key import TV_IP_ADDRESS

# Configuration
TV_IP = TV_IP_ADDRESS
TOKEN_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "samsung_tv_token.txt")
APP_NAME = "HomFlow"

class SamsungController:
    '''TO MANAGE THE CONNECTION AND COMMANDS FROM THE SAMSUNG TV'''

    def __init__(self, host=TV_IP, port=8002, token_file=TOKEN_FILE, name=APP_NAME):
        self.tv = SamsungTVWS(host=host, port=port, token_file=token_file, name=name)

    async def connect(self):
        '''Attempting to connect and recieve device info'''
        try:
            self.tv.send_key("KEY_SOURCE")
            print("Connection established!🎊 \n Launched Netflix") 
            return True
        except Exception as e:
            print(f"TV Controller: Connection error: {e}")     
            if "Authentication denied" in str(e):
                print("\n ACTION REQUIRED: Accept the prompt on the TV to allow the connection.")
            return False
        
    async def volume_up(self):
        '''Increases the volume by 1 step'''
        try:
            self.tv.send_key("KEY_VOLUP") 
            print("Command sent: Volume Up.")
        except Exception as e:
            print(f"🚨 TV Controller: Failed to send volume command: {e}")

    async def volume_down(self):
        '''Decreases the volume by 1 step'''
        try:
            self.tv.send_key("KEY_VOLDOWN") 
            print("Command sent: Volume Down.")
        except Exception as e:
            print(f"🚨 TV Controller: Failed to send volume command: {e}")

    
    async def sleep(self, seconds=2):
        try:
            await asyncio.sleep(seconds)
            print(f"Command sent: Paused for {seconds} seconds.")
        except Exception as e:
            print(f"🚨 TV Controller: Failed to send sleep command: {e}")






