import uvicorn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))

if __name__ == "__main__":
    print("🚀 SolEngineer starting...")
    print("📡 Backend  → http://localhost:8000")
    print("📄 API docs → http://localhost:8000/docs")
    print("🌐 UI       → http://localhost:3000  (run npm start in ui folder)")
    uvicorn.run(
        "solengineer.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )


## 14 — Initialize data files

# Run in Command Prompt:
# ```
# echo [] > src\solengineer\data\profiles.json
# echo [] > src\solengineer\data\history.json