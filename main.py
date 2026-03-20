from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import socket
import tldextract  # ドメイン抽出用

app = FastAPI()

def get_hostname(ip):
    """IPアドレスからホスト名を逆引きする"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return "Unknown / No PTR record"

def get_root_domain(hostname):
    """ホスト名からルートドメイン(enabler.ne.jp等)を抽出する"""
    if not hostname or "Unknown" in hostname:
        return "N/A"
    ext = tldextract.extract(hostname)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return "N/A"

def check_anonymity(headers, client_ip):
    """プロキシの匿名性レベルを判定する"""
    # 判定に使用するヘッダー
    proxy_headers = ["via", "proxy-connection", "forwarded", "x-forwarded-for", "x-real-ip", "x-proxyuser-ip"]
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # 1. Transparent チェック (ヘッダーの中にクライアントIPが含まれているか)
    for h_value in headers_lower.values():
        if client_ip in h_value:
            return "L3 - Transparent (Low Anonymity)"
    
    # 2. Anonymous チェック (プロキシ特有のヘッダーがあるか)
    if any(h in headers_lower for h in proxy_headers):
        return "L2 - Anonymous (Medium Anonymity)"
    
    # 3. Elite
    return "L1 - Elite (High Anonymity)"

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
        # Render等の背後にいる場合、本来の接続元IPを取得
        # (request.client.host は Render のプロキシIPになる場合があるため注意)
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (request.client.host if request.client else "0.0.0.0")
        
        # 逆引き実行
        reverse_dns = get_hostname(client_ip)
        # ドメイン抽出
        root_domain = get_root_domain(reverse_dns)
        # 匿名性判定
        anonymity = check_anonymity(request.headers, client_ip)
        
        scope = request.scope
        
        content = {
            "summary": {
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "client_hostname": reverse_dns,
                "client_domainname": root_domain,  # ← 追加
                "anonymity_level": anonymity,     # ← 追加
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
