from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os

app = FastAPI()

def safe_serialize(obj):
  """JSONに変換できない型を安全に文字列化するヘルパー"""
  if isinstance(obj, (str, int, float, bool, type(None))):
    return obj
  if isinstance(obj, bytes):
    return obj.decode('latin-1', errors='ignore')
  if isinstance(obj, (list, tuple)):
    return [safe_serialize(item) for item in obj]
  if isinstance(obj, dict):
    return {str(k): safe_serialize(v) for k, v in obj.items()}
  return str(obj)

@app.get("/")
async def ultra_check_proxy(request: Request):
  try:
    scope = request.scope
    
    # 1. 生のヘッダーリスト（bytesのペア）を確実に取得
    raw_headers = []
    for key, value in scope.get("headers", []):
      raw_headers.append({
        "key": key.decode('latin-1', errors='ignore'),
        "value": value.decode('latin-1', errors='ignore')
      })

    # 2. ボディの読み取り（タイムアウトやエラーを考慮）
    body_content = ""
    try:
      body_bytes = await request.body()
      if body_bytes:
        body_content = body_bytes.decode('utf-8', errors='ignore')
    except Exception:
      body_content = "Could not read body"

    # 3. すべての情報を安全に辞書にまとめる
    content = {
      "summary": {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else None,
        "client_port": request.client.port if request.client else None,
      },
      "parsed_headers": dict(request.headers),
      "raw_headers": raw_headers,
      "cookies": dict(request.cookies),
      "query_params": dict(request.query_params),
      "asgi_scope": {
        "type": scope.get("type"),
        "http_version": scope.get("http_version"),
        "scheme": scope.get("scheme"),
        "root_path": scope.get("root_path"),
        # ここで safe_serialize を使い、タプル等の型エラーを回避
        "client": safe_serialize(scope.get("client")),
        "server": safe_serialize(scope.get("server")),
      },
      "body": body_content
    }

    return JSONResponse(content=content)

  except Exception as e:
    # 万が一エラーが起きても、その内容自体をJSONで返す
    return JSONResponse(
      status_code=500,
      content={"error": "Internal Server Error", "details": str(e)}
    )

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
