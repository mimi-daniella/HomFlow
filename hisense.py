from hisensetv import HisenseTv, HisenseTvAuthorizationError

MQTT_USER = "hisenseservice"
MQTT_PASS = "multimqttservice"
TV_IP_ADDRESS = "172.20.10.2"

class HisenseController:
    def __init__(self, host=TV_IP_ADDRESS, username=MQTT_USER, password=MQTT_PASS):
        self.host = host
        self.username = username
        self.password = password

    def send_power_toggle(self):
        try:
            with HisenseTv(hostname=self.host, username=self.username, password=self.password, port=36669) as tv:
                tv.send_key("power")
                print("✅ Power toggled.")
        except Exception as e:
            print(f"🚨 Failed to send power command: {e}")

    def set_source_hdmi1(self):
        try:
            with HisenseTv(hostname=self.host, username=self.username, password=self.password, port=36669) as tv:
                tv.send_key("source_1")
                print("✅ Source set to HDMI 1.")
        except Exception as e:
            print(f"🚨 Failed to set source: {e}")

    def authorize_tv(self):
        try:
            with HisenseTv(hostname=self.host, username=self.username, password=self.password, port=36669) as tv:
                print("Starting authorization flow...")
                tv.start_authorization()
                pin_code = input("Enter the 4-digit code displayed on the TV: ")
                tv.send_authorization_code(pin_code)
                print("✅ Authorization successful!")
        except HisenseTvAuthorizationError as e:
            print(f"Authorization failed: {e}")
        except Exception as e:
            print(f"🚨 Error during authorization: {e}")