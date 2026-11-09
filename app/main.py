from fastapi import FastAPI

app = FastAPI(title="Workflow Orchestrator")


@app.get("/health")
def health_check():
    return {"status": "healthy"}
