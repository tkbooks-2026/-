# 🎬 網路小說爽文創造

> 全自動化的「小說轉有聲書影片」產線。從 AI 寫劇本、語音配音、生成水墨畫風配圖，到 FFmpeg 無縫合成長片，一鍵搞定。

## ✨ 功能特色

- 🤖 **AI 平行編劇** — 使用多個 Subagent 同時寫作，45 集劇本數分鐘完成
- 🎙️ **Edge-TTS 配音** — 微軟高品質中文語音，完全免費
- 🖼️ **AI 水墨畫配圖** — Pollinations.ai 免費生成 1280×720 場景圖（免金鑰）
- 🎞️ **15fps 字幕精準同步** — 解決語速快時字幕延遲的業界痛點
- 🔇 **areverse 倒帶去靜音** — 一行 FFmpeg 指令，消除 TTS 尾端空白
- 📼 **零秒無縫拼接** — 120 集長片各段銜接無一絲停頓

## 📋 環境需求

| 軟體 | 版本 | 說明 |
|------|------|------|
| Python | 3.10+ | 主要執行語言 |
| FFmpeg | 8.x+ | 影片編碼與合成（[下載頁面](https://www.gyan.dev/ffmpeg/builds/)） |
| Edge-TTS | 7.x+ | 微軟語音合成（透過 pip 安裝） |
| Git | 2.x+ | 版本控制（選用） |

## 🚀 快速安裝（在其他電腦上復現）

### Step 1：Clone 專案

```bash
git clone https://github.com/tkbooks-2026/-.git
cd -
```

### Step 2：安裝 FFmpeg

**Windows（使用 WinGet）：**
```powershell
winget install Gyan.FFmpeg
```

**macOS（使用 Homebrew）：**
```bash
brew install ffmpeg
```

**Linux（Ubuntu/Debian）：**
```bash
sudo apt update && sudo apt install ffmpeg
```

安裝完成後，確認 FFmpeg 可用：
```bash
ffmpeg -version
```

### Step 3：建立 Python 虛擬環境並安裝依賴

```bash
cd tool
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate

# 安裝所有 Python 套件
pip install -r requirements.txt
```

### Step 4：設定環境變數

```bash
# 複製範本
cp .env.example .env     # macOS/Linux
copy .env.example .env   # Windows
```

編輯 `.env` 檔案：
```env
# Gemini API 金鑰（多組以逗號分隔，僅 long_video_maker.py 需要）
GEMINI_API_KEYS=your_api_key_1,your_api_key_2

# FFmpeg / ffprobe 執行檔路徑（留空則自動偵測 PATH）
FFMPEG_BIN=
FFPROBE_BIN=
```

> **💡 提示**：如果 FFmpeg 已加入系統 PATH，`FFMPEG_BIN` 和 `FFPROBE_BIN` 可以留空，腳本會自動偵測。

### Step 5：驗證安裝

```bash
# 確認 Python 虛擬環境已啟動
python -c "import edge_tts; print('edge-tts OK')"
python -c "from dotenv import load_dotenv; print('dotenv OK')"

# 確認 FFmpeg
ffmpeg -version
ffprobe -version
```

## 📖 使用方式

### 方式 A：搭配 AI 編輯器（推薦）

在支援 AI 代理的編輯器（如 Gemini Code Assist、Cursor、OpenCode 等）中開啟本專案，AI 助理會自動讀取 `novel-creator` SKILL 與 `novel_video_SOP.md`，依照標準作業流程為您：

1. 建立故事聖經 (`story_bible.md`)
2. 派發多個 `novel_writer` Subagent 平行撰寫劇本
3. 執行 `render_local_story.py` 渲染影片
4. 自動執行 QA 品質驗收

只需告訴 AI：「幫我寫一部關於 OOO 的有聲書影片」即可。

### 方式 B：手動渲染已有劇本

如果您已經有劇本檔案（`chapter_1.txt`, `chapter_2.txt`...），可以直接渲染：

```bash
cd tool

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1   # Windows
source venv/bin/activate       # macOS/Linux

# 執行渲染
python render_local_story.py --outdir "../小說產出庫/2026-07-15_我的故事_簡略說明"
```

渲染引擎會自動執行：
1. 📢 TTS 配音（Edge-TTS `zh-CN-YunxiNeural`）
2. ✂️ 去尾端靜音（`areverse` 倒帶技巧）
3. 🖼️ AI 圖片生成（Pollinations.ai）
4. 🎬 單集影片合成（15fps + 字幕燒錄）
5. 📼 全集無縫合併 → `FINAL_MOVIE_15fps.mp4`

### 方式 C：全自動 AI 生成（劇本 + 渲染一條龍）

```bash
cd tool
python long_video_maker.py \
  --prompt "一個底層員工逆襲成商業帝國霸主的故事" \
  --outdir "../小說產出庫/2026-07-16_商業帝國_逆襲人生" \
  --duration 3600
```

> ⚠️ 此方式需要設定 `GEMINI_API_KEYS`（Gemini API 金鑰）。

## 📁 目錄結構

```
網路小說爽文創造/
├── .env                      # API 金鑰與 FFmpeg 路徑（不進版控）
├── .env.example              # 環境變數範本
├── .gitignore
├── README.md                 # 本檔案
├── PROJECT.md                # 專案進度追蹤
├── novel_video_SOP.md        # 影音合成技術規範（FFmpeg 參數詳解）
├── tool/
│   ├── requirements.txt      # Python 依賴清單
│   ├── utils.py              # 共用模組（路徑解析、時長偵測、圖片生成）
│   ├── render_local_story.py # 本機渲染引擎（推薦使用）
│   ├── long_video_maker.py   # 全自動長片生成引擎
│   ├── background.mp4        # 預設背景影片
│   └── venv/                 # Python 虛擬環境（不進版控）
└── 小說產出庫/                # 影片與劇本產出資料夾
    └── <日期>_<標題>_<說明>/
        ├── chapters/         # 劇本純文字檔（chapter_1.txt...）
        ├── story_bible.md    # 故事聖經（角色、世界觀）
        ├── youtube_info.txt  # YouTube 上架資訊
        ├── FINAL_MOVIE_15fps.mp4  # 最終完成品
        └── ...               # 中間產物（音訊、圖片、字幕）
```

## 🛠️ 工具說明

| 腳本 | 用途 |
|------|------|
| `render_local_story.py` | ⭐ **推薦** — 讀取現有劇本 → 配音 → 生圖 → 合成 → 拼接長片 |
| `long_video_maker.py` | 全自動：AI 寫劇本 → 配音 → 生圖 → 合成 → 拼接長片（需 API Key） |
| `utils.py` | 共用模組：FFmpeg 路徑解析、音訊時長偵測、Pollinations.ai 圖片生成 |

## 🔧 在 AI 編輯器中安裝 SKILL

如果您想在其他電腦的 AI 編輯器中啟用 `novel-creator` 技能，請將 SKILL 檔案複製到編輯器的全域技能目錄：

**Gemini Code Assist (Antigravity)：**
```powershell
# 建立技能目錄
mkdir "$env:USERPROFILE\.gemini\config\skills\novel-creator"

# 複製 SKILL.md（從專案內的 .agents 或手動複製）
# SKILL.md 的內容定義了 AI 助理在製作有聲書時的行為規範
```

SKILL 檔案的作用是告訴 AI 助理：
- 禁止使用外部 API 金鑰寫劇本（由 Subagent 代筆）
- 必須使用 `novel_writer` 平行編劇
- 影片必須 15fps、areverse 去靜音、FontSize=40 字幕
- 斷點續跑與故障修復流程

## ❓ 常見問題

### Q: FFmpeg 找不到？
腳本會依序嘗試：① `.env` 中的 `FFMPEG_BIN` → ② 系統 PATH → ③ WinGet 預設安裝路徑。三者皆無則報錯。

### Q: 渲染中斷了，怎麼辦？
直接重新執行 `render_local_story.py`。腳本有內建跳過機制，已存在的音訊/圖片/影片會自動略過，只處理缺少的部分。

### Q: 要修某幾集的劇本？
刪除那幾集的媒體檔（`audio_X.mp3`、`trimmed_audio_X.mp3`、`image_X.jpg`、`subs_X.vtt`、`chapter_X.mp4`），以及 `list.txt` 與 `FINAL_MOVIE_15fps.mp4`，然後重跑渲染。

### Q: 圖片全黑？
Pollinations.ai 暫時無法連線時會自動建立黑底替代圖。刪除該圖片後重跑即可重新生成。

## 📄 授權

本專案僅供個人學習與研究使用。
