# 網路小說爽文與有聲書影音合成 SOP

此文件記錄了從純文本劇本到最終長影片（YouTube 適用）的標準自動化流程與**技術細節**。
本文件定位為「怎麼做」的技術參考，與 `novel-creator` SKILL（定位為「做什麼」的行為規範）互為搭配。

## 1. 核心需求與痛點解決
- **字幕不同步**：由於語速快，若影片幀率過低，字幕更新會延遲。**必須設定為 15 fps**。
- **段落銜接空白**：TTS 工具產生的音檔尾端通常有 ~0.8 秒的靜音，導致段落切換時畫面定格。**必須預先精準裁切語音尾端的靜音**。
- **字幕字體過小**：預設 VTT 字幕在 720p 畫面上過小。**必須強制放大字體並加粗邊框**。

## 2. 合成腳本核心參數 (FFmpeg)

### 2.1 音訊預處理 (去尾端靜音)
為了達成「零秒無縫接軌」，每一集由 TTS 產生的 MP3 檔案，必須先透過 FFmpeg 進行倒帶去靜音，產生 `trimmed_audio_X.mp3`。
```bash
ffmpeg -y -i audio_{X}.mp3 -af "areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=-50dB,areverse" trimmed_audio_{X}.mp3
```

**原理說明**：
1. `areverse` — 先將音訊倒轉，使原本的「尾端靜音」變成「開頭靜音」。
2. `silenceremove=start_periods=1:start_silence=0:start_threshold=-50dB` — 移除開頭低於 -50dB 的靜音段。
3. `areverse` — 再倒轉回正常方向。

**禁止事項**：絕對不要使用 `stop_periods=-1` 等參數，以免誤切語音段落中的短暫停頓（如角色的自然換氣或戲劇性停頓）。

### 2.2 單集影片合成 (幀率與字幕樣式)
合成每集影片時，必須使用以下參數，確保畫面刷新率足夠且字幕清晰：
```bash
ffmpeg -y -loop 1 -framerate 15 -i image_{X}.jpg -i trimmed_audio_{X}.mp3 -vf "subtitles=subs_{X}.vtt:force_style='FontSize=40,Outline=2,Shadow=1,MarginV=30'" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest chapter_{X}.mp4
```

**參數說明**：
| 參數 | 值 | 用途 |
|------|-----|------|
| `-loop 1` | — | 靜態圖片無限循環 |
| `-framerate` | `15` | 確保字幕同步精度（每 66ms 刷新一次） |
| `-tune` | `stillimage` | 針對靜態圖片最佳化 H.264 編碼效率 |
| `-c:a` | `aac` | 音訊編碼格式 |
| `-b:a` | `192k` | 音訊位元率（YouTube 建議值） |
| `-pix_fmt` | `yuv420p` | 最大相容性像素格式 |
| `-shortest` | — | 以最短軌道（音訊）決定影片長度 |
| `FontSize` | `40` | 字幕字體大小（手機友善） |
| `Outline` | `2` | 字幕輪廓粗細（提升對比度） |
| `Shadow` | `1` | 字幕陰影（增加立體感） |
| `MarginV` | `30` | 字幕距底部邊距（避免被裁切） |

### 2.3 最終合併 (防檔案鎖定)
合併所有 MP4 檔案時，為避免輸出檔案被正在預覽的播放器鎖定導致失敗，建議在檔名加上後綴。
```bash
ffmpeg -y -f concat -safe 0 -i list.txt -c copy FINAL_MOVIE_15fps.mp4
```

`list.txt` 格式（每行一集）：
```
file 'chapter_1.mp4'
file 'chapter_2.mp4'
...
```

### 2.4 圖片生成
- 使用 **Pollinations.ai** 免費 API 生成 1280×720 的場景圖片（免金鑰）。
- 若生成失敗，腳本會自動建立黑底替代圖（1280×720）以確保渲染不中斷。
- 圖片風格後綴統一使用：
  ```
  traditional chinese ink painting, ancient style, classical chinese art, masterpiece
  ```

## 3. 創作流程規範
1. **專案建檔與命名 (嚴格執行)**：
   - 所有的產出目錄必須以「`日期_標題_簡略說明`」的格式命名。
   - 例如：`2026-07-15_神明乩身_乩身助人`。**絕不可省略日期或簡略說明**。
2. **故事聖經**：建立詳盡的故事設定、人物與世界觀。若包含真實歷史或神明，需註明考究來源。
3. **平行編劇**：將集數均分為數個單元，啟動 3-5 個 `novel_writer` Subagent 進行平行創作。每集字數約 350-500 字，末端附上圖像生成 Prompt。（詳見 `novel-creator` SKILL 的第 3 節）
4. **影音渲染**：執行 `render_local_story.py`，完成 TTS 語音生成、去靜音、圖片生成與 15fps 無縫合成。
5. **YouTube 資訊**：同步產出 `youtube_info.txt`，包含 SEO 標題、故事情節說明與 Hashtag 標籤。

## 4. 品質驗收標準 (QA 必查)
在生成最終影片後，必須抽查確認以下項目：

### 4.1 AI 助理自動檢查
| 檢查項目 | 指令 | 預期結果 |
|----------|------|----------|
| 幀率確認 | `ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 FINAL_MOVIE_15fps.mp4` | `15/1` |
| 靜音偵測 | 比較 `audio_X.mp3` 與 `trimmed_audio_X.mp3` 的時長差異 | 差距約 0.5-1.5 秒 |
| 總時長確認 | `ffprobe -v error -show_entries format=duration ...` | 與章節數量相符 |

### 4.2 使用者人工確認
1. **字幕同步性**：請確認使用了 15fps 幀率後，字幕能緊緊跟隨語速，不該有延遲、沒跟上或跳幀的問題。
2. **零秒無縫確認**：各集切換時，語音必須連續不中斷。因為已在指令中設定 `start_silence=0`，所以不能有哪怕 0.1 秒的空白停頓。

## 5. 故障修復與斷點續跑

### 5.1 渲染腳本的跳過機制
`render_local_story.py` 對每一集的每個步驟（音訊、圖片、影片）都會先檢查檔案是否存在。若已存在則自動跳過。因此，中斷後重新執行即可從斷點繼續。

### 5.2 修復特定集數
若某幾集出現問題（如劇本重複、圖片損壞），只需：
1. 刪除該集數的相關媒體檔：`audio_X.mp3`、`trimmed_audio_X.mp3`、`subs_X.vtt`、`image_X.jpg`、`chapter_X.mp4`
2. 刪除 `list.txt` 與 `FINAL_MOVIE_15fps.mp4`
3. 重新執行 `render_local_story.py`

**禁止全砍重建**：除非使用者明確要求，否則不可刪除所有已正確生成的檔案。

### 5.3 劇本修復
若需要補齊或重寫特定集數的劇本，必須使用 `novel_writer` Subagent 代筆（參見 SKILL 第 3 節），**禁止使用外部 API 金鑰**。

### 5.4 常見問題
| 問題 | 原因 | 解決方式 |
|------|------|----------|
| 合併時提示檔案鎖定 | 播放器正在預覽 | 關閉播放器後重試 |
| 圖片全黑 | Pollinations.ai 暫時無法連線 | 刪除該黑底圖片，重新執行腳本 |
| 字幕時間偏移 | VTT 檔與去靜音後的音訊不匹配 | 刪除該集的 `subs_X.vtt` 與 `audio_X.mp3`，重新生成 |
| TTS 產生亂碼 | 劇本中包含特殊符號 | 檢查並清理劇本中的非法字元 |
