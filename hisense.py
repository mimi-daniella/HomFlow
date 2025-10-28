from hisensetv import HisenseTv, HisenseTvAuthorizationError
from api_key import TV_IP_ADDRESS

# configuration
HISENSE_IP = TV_IP_ADDRESS
# default credentials
MQTT_USER = "hisenseservice"
MQTT_PASS = "multimqttservice"

class HisenseController:
    def __init__(self, host=HISENSE_IP, username=MQTT_USER, password=MQTT_PASS):
        self.tv = HisenseTv(hostname=host, username=username, password=password, port=36669)

    def connect(self):
        try:
            print("Connecting to Hisense TV...")
            self.tv.connect()
            print("Connection successful!")
        except Exception as e:
            print(f"🚨 Failed to connect to TV: {e}")


    def authorize_tv(self):
        try:
            print("Starting authorization flow...")
            self.tv.start_authorization()
            pin_code = input("\nEnter the 4-digit code displayed on the TV: ")
            self.tv.send_authorization_code(pin_code)
            print("Authorization successful!")
        except HisenseTvAuthorizationError as e:
            print(f"Authorization failed. Please try again. {e}")
        except Exception as e:
            print(f"An error occurred while authorizing the TV: {e}")

    def send_power_toggle(self):
        try:
            self.tv.send_key("KEY_POWER")
            print("Command sent: Power Toggled.")
        except Exception as e:
            print(f"🚨 Failed to send power command: {e}")

    def set_source_hdmi1(self):
        try:
            self.tv.send_key("KEY_SOURCE_1")
            print("Command sent: Set source to HDMI 1.")
        except Exception as e:
            print(f"🚨 Failed to set source: {e}")