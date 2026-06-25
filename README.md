SolEngineer

A lightweight browser-based developer tool for testing, debugging, and benchmarking Solace PubSub+ Event Brokers using the official Solace Python SDK.

Overview

SolEngineer helps developers quickly validate message flows, troubleshoot broker connectivity, consume queues, and run SDK-level performance tests without writing custom scripts.

Built during real-world Solace integration projects, SolEngineer provides a simple web interface to publish messages, subscribe to topics, consume queues, and benchmark broker performance from a single dashboard.

Features
Feature	Description
🔌 Connect	Connect to any Solace broker using TLS or TCP with saved connection profiles
📤 Publish	Publish messages to any topic with history and one-click replay
📡 Subscribe	Live message feed via WebSocket with wildcard topic support
📦 Queue Consumer	Consume durable exclusive queues with automatic acknowledgment
⚡ Performance Testing	Benchmark throughput, latency, P95/P99 metrics, Direct and Persistent messaging
Performance Testing

Configure performance tests with:

Topic or Queue targets
Direct delivery mode
Persistent delivery mode
Message count
Message size
Rate limiting (messages/sec)
Window size (Persistent mode)
Custom payload templates
Performance Metrics
Throughput (msg/sec)
Average Latency
P95 Latency
P99 Latency
Minimum Latency
Maximum Latency
Messages Sent
Messages Received
Error Count
Architecture
React UI (TypeScript)
         │
         │ REST + WebSocket
         ▼
FastAPI Backend
         │
         │ Solace Python SDK
         ▼
Solace PubSub+ Event Broker
Tech Stack
Layer	Technology
Backend	Python, FastAPI, Uvicorn
Messaging	Solace PubSub+ Python SDK
Frontend	React 18, TypeScript
Real-Time	WebSockets
Storage	Local JSON Files
Prerequisites
Python 3.10+
Node.js 16+
npm 8+
Solace PubSub+ Cloud account or on-premise broker
Setup
1. Clone the Repository
git clone https://github.com/varunjillaUIC/solace-performance-utility.git
cd solace-performance-utility
2. Create Python Environment
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
3. Install Frontend Dependencies
cd src\solengineer\ui
npm install
cd ..\..\..
4. Initialize Data Files
python -c "open('src/solengineer/data/profiles.json','w').write('[]')"
python -c "open('src/solengineer/data/history.json','w').write('[]')"
Running SolEngineer

Open two terminals.

Terminal 1 — Backend
venv\Scripts\activate
cd src
python -m solengineer.launch

Backend API:

http://localhost:8000

Swagger Documentation:

http://localhost:8000/docs
Terminal 2 — Frontend
cd src\solengineer\ui
npm start

Open:

http://localhost:3000
Connecting to a Broker

Enter your broker details on the connection screen:

Field	Example
Broker Host	tcps://mr-connection-xxx.messaging.solace.cloud:55443
Message VPN	your-vpn-name
Username	solace-cloud-client
Password	your-password
Typical Workflow
Connect to a Solace broker.
Publish messages to a topic.
Subscribe and monitor live message traffic.
Consume messages from durable queues.
Run performance tests.
Analyze throughput and latency metrics.
Export benchmark results.
Use Cases
Solace PubSub+ development
Integration testing
Broker connectivity validation
Topic and queue troubleshooting
SDK performance benchmarking
Throughput and latency analysis
Proof-of-concept environments
Developer productivity workflows
Current Limitations
Direct subscribers only receive messages published after subscription begins.
Average latency includes SDK and TCP warmup effects.
Designed primarily for single-user usage.
Broker credentials are stored locally in JSON files.
Roadmap
 Portable executable build (PyInstaller)
 Warmup message exclusion from latency calculations
 JSON message inspector
 Side-by-side performance comparison
 CSV result export
 Enhanced message replay features

