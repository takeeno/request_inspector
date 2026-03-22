#!/usr/bin/env bash
# エラーが発生したら停止
set -o errexit

# pipの更新とインストール
pip install -r requirements.txt

# GeoLite2データベースのダウンロード (P3TERX氏のリポジトリより)
# 国判定のみなら Country.mmdb で十分です
curl -L -o GeoLite2-Country.mmdb https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb
