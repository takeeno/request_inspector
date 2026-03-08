from fastapi import FastAPI, Request
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def check_proxy(request: Request):
    return {
        "client_ip": request.client.host,
        "headers": dict(request.headers)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)