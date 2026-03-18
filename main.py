from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def ultra_check_proxy(request: Request):
  # 1. ASGIスコープ（FastAPI/Uvicornが保持する全生データ）
  scope = request.scope
  
  # 2. 生のヘッダーリスト（bytesのペアとして保持されているもの）
  # これにより、大文字小文字の区別や、重複ヘッダーの生の状態が見える
  raw_headers = []
  for key, value in scope.get("headers", []):
    raw_headers.append({
      "raw_key": key.decode('latin-1'),
      "raw_value": value.decode('latin-1')
    })

  # 3. クライアント情報の深掘り
  client_host, client_port = scope.get("client", (None, None))

  # 4. JSON構造の構築
  content = {
    "summary": {
      "method": request.method,
      "url": str(request.url),
      "client_ip_detected": request.client.host,
    },
    # FastAPIがパースした後のヘッダー（小文字統一）
    "parsed_headers": dict(request.headers),
    # ネットワーク層から届いたままの生ヘッダー（重複やケースを保持）
    "raw_headers_list": raw_headers,
    # クッキー
    "cookies": dict(request.cookies),
    # ASGIスコープの全容（シリアライズ可能なもの）
    "asgi_raw_scope": {
      "type": scope.get("type"),
      "http_version": scope.get("http_version"),
      "scheme": scope.get("scheme"),
      "client": list(scope.get("client", [])),
      "server": list(scope.get("server", [])),
      "root_path": scope.get("root_path"),
    }
  }

  # Body（POSTなど）の読み取り
  try:
    body = await request.body()
    if body:
      content["body_content"] = body.decode('utf-8', errors='ignore')
      content["body_len"] = len(body)
  except Exception as e:
    content["body_error"] = str(e)

  return JSONResponse(content=content)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8000))
  # 外部接続を許可
  uvicorn.run(app, host="0.0.0.0", port=port)
