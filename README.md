# X-Ray-Request 🩻

FastAPI (ASGI) の `scope` を深層スキャンし、プロキシ背後に隠された「生の通信データ」を可視化するデバッグツール。

## 🌟 概要
**X-Ray-Request** は、FastAPI の裏側にある ASGI レイヤーに直接アクセスし、通常のフレームワークでは加工・隠蔽されてしまうリクエストの「真の姿」を解析します。
特に、Mysterium などのプロキシを経由した際の匿名性検証や、ISPドメイン（enabler.ne.jp等）の漏洩確認に特化しています。

## ✨ 主な機能
* **Raw Header Inspection**: 大文字小文字の区別や重複ヘッダーを、加工前の「生のバイト列」から復元。
* **Reverse DNS Lookup**: 接続元 IP からプロバイダのホスト名（例: `p123-ipngn...osaka.ocn.ne.jp`）を自動逆引き。
* **Domain Extraction**: 複雑なホスト名から組織ドメイン（ISP）を抽出してサマリー表示。
* **Full ASGI Scope Dump**: HTTP/2 や SSL/TLS、クライアントポート等の全メタデータを JSON で展開。
* **Safety Serialization**: `bytes` 型や `tuple` など、標準の JSON ライブラリでエラーになる型を安全に処理。

## 🚀 クイックスタート

### 1. 準備
```bash
pip install fastapi uvicorn

### 2. 起動
python main.py

### 3. 解析実行
ブラウザでアクセス、または curl で結果を取得します。
curl http://localhost:8000/

## 🛠 技術スタック
Language: Python 3.14+

Framework: FastAPI

Server: Uvicorn

Infrastructure: Render / Docker / Raspberry Pi (log2ram推奨)

## 🔍 匿名性チェックリスト
このツールを使用して、以下の項目に「自分の本当の情報」が載っていないか確認してください：

client_hostname: 自宅回線のプロバイダ名（OCN, So-net等）が出ていないか？

client_domain: enabler.ne.jp などの VNE ドメインから身元が推測されないか？

x-forwarded-for: プロキシが自分の真の IP を勝手に付け加えていないか？

## 📝 ライセンス
MIT License

Developed by Takeshi Enomoto
