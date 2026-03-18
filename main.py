from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def get_all_headers_json(request: Request):
  # 1. 全ヘッダーを取得
  headers = dict(request.headers)
  
  # 2. ASGIスコープからシリアライズ可能な情報を抽出
  scope = request.scope
  scope_serializable = {}
  for k, v in scope.items():
    if isinstance(v, (str, int, float, bool, list, dict)):
      scope_serializable[k] = v
    elif isinstance(v, bytes):
      scope_serializable[k] = v.decode('utf-8', errors='ignore')

  # 3. レスポンス用データの構築
  content = {
    "status": "success",
    "client": {
      "ip": request.client.host,
      "port": request.client.port,
    },
    "request": {
      "method": request.method,
      "url": str(request.url),
      "path": request.url.path,
      "query_params": dict(request.query_params),
    },
    "headers": headers,
    "cookies": dict(request.cookies),
    "asgi_scope": scope_serializable
  }

  # Bodyがある場合は追加
  try:
    body = await request.body()
    if body:
      content["body_raw"] = body.decode('utf-8', errors='ignore')
  except Exception:
    pass

  # JSONResponseを使い、インデントを整えて(JSON_AS_ASCII=False相当)返却
  return JSONResponse(content=content)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8000))
  # 0.0.0.0でホストすることで、外部（プロキシ）からのアクセスを待ち受け可能に
  uvicorn.run(app, host="0.0.0.0", port=port)
