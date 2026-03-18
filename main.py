from fastapi import FastAPI, Request
import uvicorn
import os
import json

app = FastAPI()

@app.get("/")
async def dump_all_details(request: Request):
  # 1. 標準的なヘッダーをすべて辞書化
  headers = dict(request.headers)
  
  # 2. ASGIスコープ（FastAPIの裏側の全生データ）を取得
  # ここには接続元のIP、プロトコル、サーバー情報などが未加工で入っています
  scope = request.scope
  
  # シリアライズ可能なものだけ抽出
  scope_details = {}
  for k, v in scope.items():
    if isinstance(v, (str, int, float, bool, list, dict)):
      scope_details[k] = v
    elif isinstance(v, bytes):
      scope_details[k] = v.decode('utf-8', errors='ignore')

  result = {
    "--- ALL_HEADERS ---": headers,
    "--- RAW_SCOPE_DETAILS ---": scope_details,
    "--- CLIENT_INFO ---": {
      "host": request.client.host,
      "port": request.client.port,
    },
    "--- REQUEST_METADATA ---": {
      "method": request.method,
      "url": str(request.url),
      "path": request.url.path,
      "query_string": request.url.query,
    }
  }

  # Body（POSTなどの場合）
  try:
    body = await request.body()
    if body:
      result["--- RAW_BODY ---"] = body.decode('utf-8', errors='ignore')
  except Exception as e:
    result["body_error"] = str(e)
    
  return result

if __name__ == "__main__":
  # ポートは環境変数から取得（デプロイ先対応）
  port = int(os.environ.get("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
