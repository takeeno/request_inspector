from fastapi import FastAPI, Request
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def get_all_info(request: Request):
    return {
        "client": {
            "host": request.client.host,
            "port": request.client.port
        },
        "url": str(request.url),
        "method": request.method,
        "base_url": str(request.base_url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "cookies": request.cookies,
        "path_params": request.path_params
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
