SolEngineer
A browser-based developer tool for publishing, subscribing, consuming queues, and benchmarking Solace PubSub+ Event Broker — built on the official Solace Python SDK.

Overview
SolEngineer helps developers quickly validate message flows, troubleshoot broker connectivity, and run SDK-level performance benchmarks without writing custom scripts. It provides a clean web interface to publish messages, subscribe to topics, consume queues, and measure broker performance from a single dashboard.

Features
FeatureDescriptionPublishSend messages instantly to any topic with history and one-click replaySubscribeLive WebSocket feed for topics and wildcard subscriptionsQueue ConsumerConsume messages from durable queues with automatic acknowledgmentProfilesSave and reuse broker connection profilesHistory and ReplayView last 100 published messages and replay instantlyPerformance TestingMeasure throughput and latency using the Solace Python SDKMetricsP95 and P99 latency statisticsChartsReal-time throughput visualizationExportExport performance results as JSONAuto-ReconnectAutomatically reconnect if the broker connection drops

Performance Testing
Configure and run SDK performance tests with the following parameters:
Configuration

Target type — Topic or Queue
Delivery mode — Direct or Persistent
Message count
Message size (bytes)
Rate limit (messages per second)
Window size (Persistent mode only)
Message mode — Raw bytes, JSON template, CSV, or custom fixed payload

Results

Throughput (msg/sec)
Average, P95, P99, Min, Max latency (ms)
Messages sent, received, and error count
Total test duration
Live progress bar with real-time msg/sec counter
Throughput over time chart
Export results as JSON


Architecture
React UI (TypeScript)
         |
         | REST + WebSocket
         v
FastAPI Backend (Python)
         |
         | Solace Python SDK
         v
Solace PubSub+ Event Broker

Tech Stack
LayerTechnologyBackendPython, FastAPI, UvicornMessagingSolace PubSub+ Python SDKFrontendReact 18, TypeScriptReal-timeWebSocketsStorageLocal JSON files

Prerequisites

Python 3.10 or higher
Node.js 18 or higher
npm 8 or higher
Solace PubSub+ Cloud account or on-premise broker


Setup
1 — Clone the repository
bashgit clone https://github.com/varunjillaUIC/solace-performance-utility.git
cd solace-performance-utility
2 — Create Python environment
bashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install fastapi uvicorn websockets solace-pubsubplus pydantic
3 — Install frontend dependencies
bashcd src\solengineer\ui
npm install
cd ..\..\..
4 — Initialize data files (first time only)
bashcd src\solengineer\data
python -c "open('profiles.json','w').write('[]')"
python -c "open('history.json','w').write('[]')"
cd ..\..\..

Running
Development Mode
Open two terminals.
Terminal 1 — Backend
bashvenv\Scripts\activate
cd src
python -m solengineer.launch

Backend API: http://localhost:8000
Swagger docs: http://localhost:8000/docs

Terminal 2 — Frontend
bashcd src\solengineer\ui
npm start

Open: http://localhost:3000


Production Mode (Single Port)
Step 1 — Build the UI
bashcd src\solengineer\ui
npm run build
cd ..\..\..
Step 2 — Start the backend
bashvenv\Scripts\activate
cd src
python -m solengineer.launch

Open: http://localhost:8000


Connecting to a Broker
Enter your broker details on the connection screen:
FieldExampleBroker Hosttcps://mr-connection-xxx.messaging.solace.cloud:55443Message VPNyour-vpn-nameUsernamesolace-cloud-clientPasswordyour-password

Project Structure
SolEngineer/
|
├── venv/
|
└── src/
     └── solengineer/
          |
          ├── api/
          |    ├── main.py
          |    ├── state.py
          |    └── routers/
          |         ├── publish.py
          |         ├── subscribe.py
          |         ├── queue.py
          |         ├── profiles.py
          |         └── perf.py
          |
          ├── core/
          |    └── connection_manager.py
          |
          ├── publisher/
          |    └── topic_publisher.py
          |
          ├── subscriber/
          |    └── topic_subscriber.py
          |
          ├── queue/
          |    └── queue_consumer.py
          |
          ├── perf/
          |    └── perf_tester.py
          |
          ├── data/
          |    ├── profiles.json
          |    └── history.json
          |
          ├── ui/
          |    └── src/
          |         └── components/
          |
          └── launch.py

Typical Workflow

Connect to a Solace broker
Publish a message to a topic
Subscribe and monitor live message traffic
Consume messages from a durable queue
Run a performance test
Analyze throughput and latency metrics
Export benchmark results as JSON


Implemented Features

Connect to Solace Cloud over TLS
Save and load connection profiles
Publish to topics
Publish history and replay
Live topic subscriber via WebSocket
Queue consumer via WebSocket
Clear messages anytime
SDK performance testing for topics and queues
Custom message templates
Live progress bar during performance tests
P95 and P99 latency metrics
Throughput chart
Export performance results as JSON
Auto-reconnect on idle connection drops


Current Limitations

Direct subscribers only receive messages published after subscription begins
One topic subscription and one queue consumer active at a time per session
Average latency includes SDK and TCP warmup effects — P95 and P99 are more representative for production analysis
Designed for single-user usage
Broker credentials stored locally in plain JSON files


Roadmap

Portable executable build via PyInstaller
Warmup message exclusion from latency calculations
Multi-topic simultaneous subscription
JSON message inspector with pretty-print
Side-by-side performance test comparison
CSV result export


Dependencies
fastapi
uvicorn
websockets
solace-pubsubplus
pydantic

Author
Varun Jilla — Built as a developer productivity tool for Solace PubSub+ integration engineering.