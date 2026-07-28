import os
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "vulkan/rfid/titanium/#")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "virt_iot_consumer")


def format_payload(payload: bytes) -> str:
    try:
        text = payload.decode("utf-8")
        if text.isprintable() or all(c in "\r\n\t" or c.isprintable() for c in text):
            return text
    except UnicodeDecodeError:
        pass
    return payload.hex()


def on_connect(client: mqtt.Client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"connected to {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"subscribed to {MQTT_TOPIC}")
    else:
        print(f"connect failed: {reason_code}", file=sys.stderr)


def on_disconnect(client: mqtt.Client, userdata, flags, reason_code, properties=None):
    print(f"disconnected: {reason_code}")


def on_message(client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    body = format_payload(msg.payload)
    print(f"[{ts}] topic={msg.topic} qos={msg.qos} payload={body}")


def main() -> int:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=MQTT_CLIENT_ID,
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    print(f"connecting to {MQTT_HOST}:{MQTT_PORT} as {MQTT_CLIENT_ID} ...")
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    except OSError as exc:
        print(f"cannot reach broker: {exc}", file=sys.stderr)
        print("is mosquitto running on this host?", file=sys.stderr)
        return 1

    client.loop_start()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        client.loop_stop()
        client.disconnect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
