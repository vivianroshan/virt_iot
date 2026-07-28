import argparse
import json
import os
import sys
import time
import uuid

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_PUBLISH_TOPIC = os.getenv("MQTT_PUBLISH_TOPIC", "vulkan/rfid/titanium/tag")
MQTT_CLIENT_ID = os.getenv("MQTT_PRODUCER_CLIENT_ID", "virt_iot_producer")


def build_payload(uid: str | None, payload: str | None) -> str:
    if payload is not None:
        return payload
    tag = uid or uuid.uuid4().hex[:8].upper()
    return json.dumps({"uid": tag, "source": "virt_iot_producer"}, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a test MQTT message (Vulkan RFID Titanium).")
    parser.add_argument("--topic", default=MQTT_PUBLISH_TOPIC, help="Publish topic")
    parser.add_argument("--payload", default=None, help="Raw payload string")
    parser.add_argument("--uid", default=None, help="Tag uid; builds JSON if --payload omitted")
    parser.add_argument("--qos", type=int, default=1, choices=(0, 1, 2))
    args = parser.parse_args()

    body = build_payload(args.uid, args.payload)
    client_id = f"{MQTT_CLIENT_ID}-{uuid.uuid4().hex[:6]}"
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=client_id,
    )

    print(f"connecting to {MQTT_HOST}:{MQTT_PORT} as {client_id} ...")
    try:
        client.connect(MQTT_HOST, MQTT_PORT, keepalive=30)
    except OSError as exc:
        print(f"cannot reach broker: {exc}", file=sys.stderr)
        print("is mosquitto running on this host?", file=sys.stderr)
        return 1

    client.loop_start()
    info = client.publish(args.topic, body, qos=args.qos)
    info.wait_for_publish(timeout=5)
    # brief wait so the network write finishes before disconnect
    time.sleep(0.1)
    client.loop_stop()
    client.disconnect()

    if not info.is_published():
        print("publish failed or timed out", file=sys.stderr)
        return 1

    print(f"published topic={args.topic} qos={args.qos} payload={body}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
