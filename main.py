from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import socket
import tldextract
import geoip2.database
from contextlib import asynccontextmanager

# --- GeoLite2 セットアップ ---
DB_PATH = "GeoLite2-Country.mmdb"
reader = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリ起動時にDBをロード
    global reader
    if os.path.exists(DB_PATH):
        try:
            reader = geoip2.database.Reader(DB_PATH)
        except Exception as e:
            print(f"Error loading GeoLite2 DB: {e}")
    yield
    # アプリ終了時にリソースを解放
    if reader:
        reader.close()

app = FastAPI(lifespan=lifespan)

# --- ユーティリティ関数 ---

def get_hostname(ip):
    """IPアドレスからホスト名を逆引きする"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception:
        return "Unknown / No PTR record"

def get_root_domain(hostname):
    """ホスト名からルートドメインを抽出する"""
    if not hostname or "Unknown" in hostname:
        return "N/A"
    ext = tldextract.extract(hostname)
    if ext.domain and ext.suffix:
        return f"{ext.domain}.{ext.suffix}"
    return "N/A"

def get_country_code(ip):
    """GeoLite2を使用して国コード(ISO 2文字)を取得する"""
    if not reader:
        return "DB Error"
    try:
        if ip in ("127.0.0.1", "0.0.0.0", "localhost"):
            return "Local"
        response = reader.country(ip)
        # 2文字の国コード（JP, US等）を返す
        return response.country.iso_code if response.country.iso_code else "Unknown"
    except Exception:
        return "Unknown"

def check_proxy_evidence(headers, client_ip):
    """
    HTTPヘッダーをスキャンし、プロキシ利用の「事実（形跡）」を判定する
    """
    # 判定に使用するプロキシ特有のヘッダー
    proxy_headers = [
        "via", "proxy-connection", "forwarded", 
        "x-forwarded-for", "x-real-ip", "x-proxyuser-ip",
        "cf-connecting-ip", "true-client-ip"
    ]
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # 1. IPインジェクションの形跡（最も強い証拠）
    # ヘッダー内に、現在の接続元(client_ip)以外のIPが含まれている、またはclient_ip自体が含まれている場合
    for h_name in proxy_headers:
        h_value = headers_lower.get(h_name, "")
        if h_value and (client_ip in h_value or "," in h_value):
            return "Confirmed (IP Trace Detected)"
    
    # 2. ヘッダーの存在（プロキシが自己申告している形跡）
    if any(h in headers_lower for h in proxy_headers):
        return "Likely (Proxy Headers Present)"
    
    # 3. 痕跡なし（直接接続、または高度に隠蔽されたプロキシ）
    return "None Detected"

def force_serializable(obj):
    """JSON変換不可能なオブジェクトを文字列に変換する"""
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

# --- メインルート ---

@app.get("/")
async def ultra_check_with_hostname(request: Request):
    try:
        # 直接の接続元（プロキシのIP）を優先取得
        client_ip = request.client.host if request.client else "0.0.0.0"

        # 国コード（JP等）の取得
        country_code = get_country_code(client_ip)
        
        # 逆引き実行
        reverse_dns = get_hostname(client_ip)
        # ドメイン抽出
        root_domain = get_root_domain(reverse_dns)
        
        # 【修正】「匿名性」ではなく「プロキシの痕跡」を判定
        proxy_evidence = check_proxy_evidence(request.headers, client_ip)

        scope = request.scope

        content = {
            "summary": {
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "client_country_iso": country_code,
                "client_hostname": reverse_dns,
                "client_domainname": root_domain,
                "proxy_evidence": proxy_evidence, # 項目名を変更
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
