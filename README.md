# virt_iot

MQTT consumer for a **Vulkan RFID Titanium** reader. Connects to a local Mosquitto broker and logs messages (UTF-8 text or hex).

Works on **Windows**, **Linux**, and **macOS**.

## Prerequisites

- Python 3.10+
- Eclipse Mosquitto (local broker)

### Install Mosquitto

**Windows**

```text
winget install EclipseFoundation.Mosquitto
```

Or download the installer from https://mosquitto.org/download/

Start the Mosquitto service from Services, or run `mosquitto -v` from the install directory (often `C:\Program Files\mosquitto`).

**Linux (Debian/Ubuntu)**

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

**macOS**

```bash
brew install mosquitto
brew services start mosquitto
```

Broker listens on `localhost:1883` by default.

## Setup

```text
python -m venv .venv
```

Activate the venv:

- Windows (cmd): `.venv\Scripts\activate.bat`
- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Linux / macOS: `source .venv/bin/activate`

```text
pip install -r requirements.txt
```

Copy env defaults:

- Windows: `copy .env.example .env`
- Linux / macOS: `cp .env.example .env`

Edit `.env` if your topic or host differs.

| Variable | Default | Description |
|---|---|---|
| `MQTT_HOST` | `localhost` | Broker host |
| `MQTT_PORT` | `1883` | Broker port |
| `MQTT_TOPIC` | `vulkan/rfid/titanium/#` | Subscribe filter |
| `MQTT_CLIENT_ID` | `virt_iot_consumer` | MQTT client id |

## Run consumer

```text
python consumer.py
```

Stop with Ctrl+C.

## Smoke test

With the consumer running, publish a test message (requires `mosquitto_pub` on PATH):

```text
mosquitto_pub -h localhost -t vulkan/rfid/titanium/tag -m "{\"uid\":\"AABBCCDD\"}"
```

You should see a log line with topic and payload. Non-UTF-8 payloads are printed as hex.

## Payload format

The real Vulkan RFID Titanium message schema is not defined yet. The consumer logs raw payloads so you can capture samples and add parsing later.
