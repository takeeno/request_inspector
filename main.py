from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import socket # 逆引き用に追加

app = FastAPI()

def get_hostname(ip):
  """IPアドレスからホスト名を逆引きする"""
  try:
    # タイムアウトを考慮し、 gethostbyaddr で逆引きを実行
    hostname, _, _ = socket.gethostbyaddr(ip)
    return hostname
  except Exception:
    # 逆引きできない場合はNoneまたはエラー表示
    return "Unknown / No PTR record"

def force_serializable(obj):
  if isinstance(obj, bytes):
    return obj.decode('latin-1', errors='ignore')
  if isinstance(obj, (list, tuple, set)):
    return [force_serializable(item) for item in obj]
  if isinstance(obj, dict):
    return {
      (k.decode('latin-1', errors='ignore') if isinstance(k, bytes) else str(k)): force_serializable(v)
      for k, v in obj.items()
    }
  return obj if isinstance(obj, (str, int, float, bool, type(None))) else str(obj)

@app.get("/")
async def ultra_check_with_hostname(request: Request):
  try:
    client_ip = request.client.host if request.client else "0.0.0.0"
    # 逆引き実行
    reverse_dns = get_hostname(client_ip)
    
    scope = request.scope
    
    content = {
      "summary": {
        "method": request.method,
        "url": str(request.url),
        "client_ip": client_ip,
        "client_hostname": reverse_dns, # ここにドメインを表示
        "client_port": request.client.port if request.client else 0
      },
      "parsed_headers": dict(request.headers),
      "raw_headers": [
        {"key": k.decode('latin-1'), "value": v.decode('latin-1')} 
        for k, v in scope.get("headers", [])
      ],
      "asgi_scope": force_serializable(scope)
    }

    return JSONResponse(content=content)

  except Exception as e:
    return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8000))
  uvicorn.run(app, host="0.0.0.0", port=port)
