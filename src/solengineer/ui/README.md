# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).





# ⚡ SolEngineer

A futuristic CLI + Web UI debugging tool for **Solace PubSub+ Event Broker**.  
Built with Python (FastAPI) + React (TypeScript).

Designed for developers who need to quickly publish, subscribe, consume, and performance-test message flows on Solace — without writing any code.

---

## 🖥️ Features

| Feature | Description |
|---|---|
| 📤 Publish | Send messages to any topic instantly |
| 📡 Subscribe | Live WebSocket feed for any topic or wildcard |
| 📦 Queue | Consume and auto-ack messages from queues |
| 💾 Profiles | Save and reuse broker connection profiles |
| 🔁 History & Replay | View last 100 published messages, replay any with one click |
| ⚡ Perf Test | Measure throughput and latency end-to-end via Solace SDK |

---

## 📁 Project Structure




# Varun Extra 

Here are all the commands for your README:

README — SolEngineer
Prerequisites
Python 3.10+
Node.js 18+

Installation
Clone / setup project:
cd D:\Solace-Varun\SolEngineer
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn websockets solace-pubsubplus pydantic
Install UI dependencies:
cd src\solengineer\ui
npm install

Running in Development
Terminal 1 — Backend:
cd D:\Solace-Varun\SolEngineer
venv\Scripts\activate
cd src
python -m solengineer.launch
Terminal 2 — Frontend:
cd D:\Solace-Varun\SolEngineer\src\solengineer\ui
npm start
Open browser:
http://localhost:3000
API docs:
http://localhost:8000/docs

Running in Production (single port)
Build the UI first:
cd D:\Solace-Varun\SolEngineer\src\solengineer\ui
npm run build
Then start backend only:
cd D:\Solace-Varun\SolEngineer
venv\Scripts\activate
cd src
python -m solengineer.launch
Open browser:
http://localhost:8000

Initialize data files (first time only)
cd D:\Solace-Varun\SolEngineer\src\solengineer\data
python -c "open('profiles.json','w').write('[]')"
python -c "open('history.json','w').write('[]')"

Project Structure
SolEngineer/
├── venv/
├── src/
│   └── solengineer/
│       ├── api/
│       │   ├── main.py
│       │   ├── state.py
│       │   └── routers/
│       │       ├── publish.py
│       │       ├── subscribe.py
│       │       ├── queue.py
│       │       ├── profiles.py
│       │       └── perf.py
│       ├── core/connection_manager.py
│       ├── publisher/topic_publisher.py
│       ├── subscriber/topic_subscriber.py
│       ├── queue/queue_consumer.py
│       ├── perf/perf_tester.py
│       ├── data/
│       │   ├── profiles.json
│       │   └── history.json
│       ├── ui/
│       └── launch.py

Features
✅ Connect to Solace PubSub+ broker (TLS supported)
✅ Publish messages to topics
✅ Subscribe to topics (live WebSocket feed)
✅ Consume from queues (live WebSocket feed)
✅ Save and load connection profiles
✅ Publish history and replay
✅ SDK performance testing (throughput + latency)



⚡ SolEngineer — Feature Summary
─────────────────────────────────
✅ Connect to Solace Cloud (TLS)
✅ Save / load connection profiles  
✅ Publish to topics
✅ Publish history + replay
✅ Live topic subscriber (WebSocket)
✅ Queue consumer (WebSocket)
✅ Clear messages anytime
✅ SDK Perf test — topic + queue
✅ Custom message templates
✅ Live progress bar during perf
✅ P95 / P99 latency stats
✅ Throughput chart
✅ Export perf results as JSON
✅ Auto-reconnect on idle drop