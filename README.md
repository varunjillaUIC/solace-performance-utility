# SolEngineer

A browser-based developer tool for publishing, subscribing, consuming queues, and benchmarking **Solace PubSub+ Event Broker** using the official **Solace Python SDK**.

---

## Overview

SolEngineer helps developers quickly validate message flows, troubleshoot broker connectivity, and run SDK-level performance benchmarks without writing custom scripts.

It provides a modern web interface to:

- Publish messages to topics
- Subscribe to topics in real time
- Consume messages from queues
- Save and reuse broker profiles
- Replay published messages
- Run SDK-level performance tests
- Measure throughput and latency metrics

All from a single dashboard.

---

## Features

| Feature | Description |
|----------|-------------|
| 🔌 Connect | Connect to Solace brokers over TLS or TCP using saved profiles |
| 📤 Publish | Send messages instantly to any topic with history and one-click replay |
| 📡 Subscribe | Live WebSocket feed for topics and wildcard subscriptions |
| 📥 Queue Consumer | Consume messages from durable queues with automatic acknowledgment |
| 💾 Profiles | Save and reuse broker connection profiles |
| 🔄 History & Replay | View last 100 published messages and replay instantly |
| 🚀 Performance Testing | Measure throughput and latency using the Solace Python SDK |
| 📊 Metrics | P95 and P99 latency statistics |
| 📈 Charts | Real-time throughput visualization |
| 📁 Export | Export performance results as JSON |
| ♻️ Auto-Reconnect | Automatically reconnect if the broker connection drops |

---

## Performance Testing

Configure and run SDK performance tests with the following parameters:

### Configuration

- Target Type — Topic or Queue
- Delivery Mode — Direct or Persistent
- Message Count
- Message Size (bytes)
- Rate Limit (messages per second)
- Window Size (Persistent mode only)
- Message Mode:
  - Raw Bytes
  - JSON Template
  - CSV
  - Custom Fixed Payload

### Results

- Throughput (msg/sec)
- Average Latency
- P95 Latency
- P99 Latency
- Minimum Latency
- Maximum Latency
- Messages Sent
- Messages Received
- Error Count
- Total Test Duration
- Live Progress Bar
- Real-Time Throughput Counter
- Throughput Over Time Chart
- Export Results as JSON

---

## Architecture

```text
┌───────────────────────────┐
│ React UI (TypeScript)     │
└─────────────┬─────────────┘
              │ REST + WebSocket
              ▼
┌───────────────────────────┐
│ FastAPI Backend (Python)  │
└─────────────┬─────────────┘
              │ Solace Python SDK
              ▼
┌───────────────────────────┐
│ Solace PubSub+ Broker     │
└───────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---------|------------|
| Backend | Python, FastAPI, Uvicorn |
| Messaging | Solace PubSub+ Python SDK |
| Frontend | React 18, TypeScript |
| Real-Time Communication | WebSockets |
| Storage | Local JSON Files |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 8+
- Solace PubSub+ Cloud Account or On-Prem Broker

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/varunjillaUIC/solace-performance-utility.git
cd solace-performance-utility
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

```bash
pip install fastapi uvicorn websockets solace-pubsubplus pydantic
```

### 4. Install Frontend Dependencies

```bash
cd src/solengineer/ui
npm install
cd ../../..
```

### 5. Initialize Data Files (First Time Only)

```bash
cd src/solengineer/data

python -c "open('profiles.json','w').write('[]')"
python -c "open('history.json','w').write('[]')"

cd ../../..
```

---

## Running SolEngineer

### Development Mode

Open two terminals.

### Terminal 1 — Backend

```bash
venv\Scripts\activate
cd src

python -m solengineer.launch
```

Backend API:

```text
http://localhost:8000
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

### Terminal 2 — Frontend

```bash
cd src/solengineer/ui
npm start
```

Open:

```text
http://localhost:3000
```

---

## Production Mode

### Build Frontend

```bash
cd src/solengineer/ui

npm run build

cd ../../..
```

### Start Backend

```bash
venv\Scripts\activate
cd src

python -m solengineer.launch
```

Open:

```text
http://localhost:8000
```

---

## Connecting to a Broker

Enter your broker details on the connection screen.

| Field | Example |
|---------|---------|
| Broker Host | tcps://mr-connection-xxx.messaging.solace.cloud:55443 |
| Message VPN | your-vpn-name |
| Username | solace-cloud-client |
| Password | your-password |

---

## Project Structure

```text
SolEngineer/
│
├── src/
│   └── solengineer/
│       │
│       ├── api/
│       │   ├── main.py
│       │   ├── state.py
│       │   └── routers/
│       │       ├── publish.py
│       │       ├── subscribe.py
│       │       ├── queue.py
│       │       ├── profiles.py
│       │       └── perf.py
│       │
│       ├── core/
│       │   └── connection_manager.py
│       │
│       ├── publisher/
│       │   └── topic_publisher.py
│       │
│       ├── subscriber/
│       │   └── topic_subscriber.py
│       │
│       ├── queue/
│       │   └── queue_consumer.py
│       │
│       ├── perf/
│       │   └── perf_tester.py
│       │
│       ├── data/
│       │   ├── profiles.json
│       │   └── history.json
│       │
│       ├── ui/
│       │   └── src/
│       │       └── components/
│       │
│       └── launch.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Typical Workflow

1. Connect to a Solace broker
2. Publish a message to a topic
3. Subscribe and monitor live message traffic
4. Consume messages from a durable queue
5. Run a performance test
6. Analyze throughput and latency metrics
7. Export benchmark results as JSON

---

## Implemented Features

- Connect to Solace Cloud over TLS
- Save and load connection profiles
- Publish to topics
- Publish history and replay
- Live topic subscriber via WebSocket
- Queue consumer via WebSocket
- Clear messages anytime
- SDK performance testing for topics and queues
- Custom message templates
- Live progress bar during performance tests
- P95 and P99 latency metrics
- Throughput chart
- Export performance results as JSON
- Auto-reconnect on idle connection drops

---

## Current Limitations

- Direct subscribers only receive messages published after subscription begins
- One topic subscription and one queue consumer active at a time per session
- Average latency includes SDK and TCP warm-up effects
- Designed primarily for single-user usage
- Broker credentials are stored locally in JSON files

---

## Roadmap

- Portable executable build using PyInstaller
- Warm-up message exclusion from latency calculations
- Multi-topic simultaneous subscriptions
- JSON message inspector with pretty-print support
- Side-by-side performance test comparison
- CSV export for benchmark results
- Dark mode UI
- Multi-user profile support

---

## Dependencies

```text
fastapi
uvicorn
websockets
solace-pubsubplus
pydantic
react
typescript
```

