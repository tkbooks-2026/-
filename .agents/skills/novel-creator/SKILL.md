---
name: novel-creator
description: 網路小說與有聲書影片生成標準流程，包含神明考究、平行編劇與 15fps 無縫影音渲染 SOP。
---

# 網路小說與有聲書製作技能 (Novel Creator)

當使用者呼叫此技能時，你必須嚴格遵守以下製作規範，不可隨意更改影音合成的關鍵參數，以確保最終影片能做到「字體清晰、字幕同步、零秒無縫換場」。

## 1. 核心規範 (嚴格執行)

### 1.1 絕對禁止事項
- **禁止使用外部 API 金鑰生成劇本**：劇本必須由 AI 助理（Subagent）直接代筆撰寫。絕對不可撰寫 Python 腳本去呼叫 Gemini API、OpenAI API 或任何外部 LLM API 來生成劇本內容。違反此規則會導致使用者的 API 配額被無謂消耗。
- **禁止使用 `stop_periods=-1`**：音訊去靜音時，禁止直接使用此參數，以免誤切語音段落中的短暫停頓。

### 1.2 強制技術參數
- **專案目錄命名**：產出的小說目錄名稱必須採用 `日期_標題_簡略說明` 格式（如：`2026-07-15_神明乩身_乩身助人`），**絕對不可遺漏**日期與簡略說明。
- **影片幀率**：必須使用 `15 fps` 以確保字幕同步無延遲。
- **音訊去靜音**：必須使用 `areverse` 倒帶技巧去除語音結尾靜音。
- **字幕樣式**：必須使用 `FontSize=40,Outline=2,Shadow=1,MarginV=30`，確保在手機上清晰可見。

## 2. 故事與世界觀建立
- 確認主題與長度。依主題需求彈性調整集數，每集 350-500 字，一般長度為 45-120 集。
- 若涉及神明、歷史人物，**必須基於真實可考究的來源**（如《三教搜神大全》、道藏、地方廟宇誌），不可憑空捏造。
- 撰寫詳細的 `story_bible.md`，內容應包含：
  - **世界觀設定**：時代背景、地理環境、超自然規則
  - **主要角色**：姓名、年齡、性格、能力、彼此關係
  - **劇情大綱**：分幕概述、每幕的核心衝突與轉折
  - **考究來源**：涉及的神明或歷史人物的文獻出處

## 3. 劇本創作 (平行處理)

### 3.1 定義專屬代理
在開始寫作前，**必須**先使用 `define_subagent` 定義名為 `novel_writer` 的專屬代理。其 System Prompt 須包含以下要求：
- 寫實都市劇風格、貼近現實與民間信仰、無修仙、無魔法
- 每集 350-500 字、純對白與動作描述
- 禁止導演指示、鏡頭語言、機位描述、角色旁白標籤
- 每集結尾必須附上 `[IMAGE_PROMPT: <英文描述>, traditional Chinese colored ink painting style, cinematic lighting, highly detailed]`
- 使用 `write_to_file` 工具將劇本存入指定的 `chapters/` 目錄

### 3.2 平行派發
- 使用 `invoke_subagent` 呼叫多個 `novel_writer` **同時**寫作。
- 例如將 45 集分為 3-5 個幕，每個幕由一位 `novel_writer` 負責。
- 每位代理須收到：前情提要、負責的集數範圍、該幕的劇情大綱、以及下一幕的開頭銜接點。

## 4. 影音渲染
- 執行 `render_local_story.py` 進行全自動渲染，包含：
  1. **TTS 配音**：使用 Edge-TTS（`zh-CN-YunxiNeural`）生成語音與 VTT 字幕
  2. **去尾端靜音**：使用 `areverse` 倒帶技巧精準裁切（詳見專案 `novel_video_SOP.md`）
  3. **AI 圖片生成**：使用 Pollinations.ai 免費 API 生成 1280×720 場景圖片（免金鑰）
  4. **單集合成**：15fps 靜態圖 + 去靜音語音 + VTT 字幕燒錄
  5. **最終合併**：使用 `concat` 無損合併所有章節為 `FINAL_MOVIE_15fps.mp4`
- 詳細的 FFmpeg 指令參數請參閱專案根目錄的 `novel_video_SOP.md`。

## 5. 上架資訊生成 (必須執行)
在完成渲染後，必須在專案目錄下生成 `youtube_info.txt`。
內容必須包含：
- **SEO 標題** (例如：【小說標題】第一季全集 | 簡略說明有聲書)
- **劇情簡介** (包含故事背景與各單元重點介紹)
- **Hashtag 標籤** (例如 #有聲書 #爽文 等)

## 6. 故障修復與斷點續跑
- 渲染腳本已內建跳過機制：若 `audio_X.mp3`、`image_X.jpg`、`chapter_X.mp4` 已存在，會自動跳過該步驟。
- **修復流程**：只需刪除出問題的特定集數的媒體檔（`audio_X.mp3`、`trimmed_audio_X.mp3`、`image_X.jpg`、`subs_X.vtt`、`chapter_X.mp4`），以及最終的 `list.txt` 與 `FINAL_MOVIE_15fps.mp4`，然後重新執行 `render_local_story.py` 即可自動補齊。
- **禁止全砍重建**：除非使用者明確要求，否則不可刪除所有已正確生成的檔案。
- **劇本修復**：若需要補齊或重寫特定集數的劇本，同樣必須使用 `novel_writer` Subagent 代筆，禁止使用外部 API。

## 7. 品質驗收標準 (QA 必查)
在產出最終影片後，AI 助理必須**自動執行**以下檢查，並將結果回報給使用者：

### 7.1 自動化檢查指令
1. **幀率確認**：
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 FINAL_MOVIE_15fps.mp4
   ```
   預期結果：`15/1`

2. **靜音偵測**（抽查交界處章節）：
   ```bash
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio_X.mp3
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 trimmed_audio_X.mp3
   ```
   預期結果：trimmed 版本應比原始版本短約 0.5-1.5 秒

3. **總時長確認**：確認最終影片時長與所有章節數量相符。

### 7.2 提醒使用者人工確認
1. **字幕同步性**：由於使用了 15fps，字幕應緊緊跟隨語速，不該有延遲或沒跟上的問題。
2. **零秒無縫確認**：各章節切換時，語音段落銜接必須完全連續，不能有一絲空白停頓。
