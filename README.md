# 網路小說爽文創造

> 全自動化的「小說轉解說影片」流程，實現零成本大量產出高畫質、帶有語音與特效的長篇影片。

## ✨ 功能特色

- 🤖 **AI 自動撰寫劇本** — 使用 Gemini API 連載生成都市爽文
- 🎙️ **自動語音配音** — Edge-TTS 高品質中文語音合成
- 🎨 **AI 生成配圖** — Pollinations.ai 免費 AI 繪圖（支援水墨古畫風等多種風格）
- 🎬 **FFmpeg 影片合成** — 自動加入字幕、淡入淡出過場特效
- 📼 **長片拼接** — 多集自動合併為一部完整長影片

## 📋 環境需求

| 軟體 | 版本 | 說明 |
|------|------|------|
| Python | 3.10+ | 主要執行語言 |
| FFmpeg | 8.x+ | 影片編碼與合成 |
| Edge-TTS | 7.x+ | 微軟語音合成 (pip 安裝) |
| Cloudflare WARP | 選用 | API 速率限制時自動換 IP |

## 🚀 快速開始

### 1. 安裝 Python 依賴

```bash
cd tool
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 2. 設定環境變數

複製範本並填入你的 API 金鑰：

```bash
copy .env.example .env
# 編輯 .env，填入 Gemini API Key 和 FFmpeg 路徑
```

### 3. 執行影片生成

**方式 A：全自動 AI 生成（劇本 + 渲染一條龍）**

```bash
cd tool
python long_video_maker.py --prompt "一個底層員工逆襲成商業帝國霸主的故事" --outdir "../小說產出庫/我的新故事" --duration 3600
```

**方式 B：只渲染已有劇本**

先將劇本放入 `<outdir>/chapters/chapter_1.txt`, `chapter_2.txt`... 然後：

```bash
cd tool
python render_local_story.py --outdir "../小說產出庫/我的新故事"
```

## 📁 目錄結構

```
網路小說爽文創造/
├── .env                    # API 金鑰與 FFmpeg 路徑設定 (不進版控)
├── .env.example            # 環境變數範本
├── .gitignore
├── PROJECT.md              # 專案進度追蹤
├── README.md               # 本檔案
├── tool/
│   ├── requirements.txt    # Python 依賴清單
│   ├── utils.py            # 共用工具模組
│   ├── long_video_maker.py # 全自動長片生成引擎
│   ├── render_local_story.py # 本機渲染引擎
│   ├── video_builder.py    # [已廢棄] 舊版單集合成
│   ├── background.mp4      # 預設背景影片
│   ├── venv/               # Python 虛擬環境 (不進版控)
│   └── tests/              # 測試腳本
└── 小說產出庫/              # 影片與劇本產出
    └── 百萬鉅作_商業帝國/
        ├── chapters/       # 35 集劇本 (.txt)
        ├── FINAL_MOVIE.mp4 # 完成品 (~1h18m)
        └── ...             # 音訊、圖片、字幕等中間產物
```

## 🛠️ 工具說明

| 腳本 | 用途 |
|------|------|
| `long_video_maker.py` | 全自動：AI 寫劇本 → 配音 → 生圖 → 合成 → 拼接長片 |
| `render_local_story.py` | 半自動：讀取現有劇本 → 配音 → 生圖 → 合成 → 拼接長片 |
| `utils.py` | 共用模組：FFmpeg 路徑解析、時長偵測、圖片生成 |
| `video_builder.py` | ⚠️ 已廢棄，僅供歷史參考 |

## 📄 授權

本專案僅供個人學習與研究使用。
