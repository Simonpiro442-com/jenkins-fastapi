from fastapi import FastAPI 

app = FastAPI(title="Jenkins FastAPI Demo")

@app.get("/")
def home():
    return {
        "message": "Hello from FastAPI!", 
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }