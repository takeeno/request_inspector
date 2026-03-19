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
>bash
pip install fastapi uvicorn
