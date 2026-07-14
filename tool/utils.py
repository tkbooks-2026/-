"""
utils.py — 共用工具模組
提供 FFmpeg 路徑解析、音訊時長偵測、AI 圖片生成等共用功能。
"""

import os
import sys
import shutil
import subprocess
import urllib.parse
import urllib.request
from dotenv import load_dotenv

# 載入 .env（支援從 tool/ 或專案根目錄執行）
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(_env_path)


# ──────────────────────────────────────
# FFmpeg / ffprobe 路徑解析
# ──────────────────────────────────────

def _resolve_bin(env_key: str, bin_name: str) -> str:
    """
    依序嘗試：
    1. 環境變數指定的路徑 (例如 FFMPEG_BIN)
    2. 系統 PATH 中自動偵測
    3. 舊版硬編碼路徑 (向下相容)
    找不到則拋出 FileNotFoundError。
    """
    # 1. 從 .env 或系統環境變數讀取
    env_val = os.getenv(env_key, "").strip()
    if env_val and os.path.isfile(env_val):
        return env_val

    # 2. 自動偵測 PATH
    found = shutil.which(bin_name)
    if found:
        return found

    # 3. 舊版硬編碼路徑 (向下相容 WinGet 安裝)
    legacy = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        r"Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
        r"ffmpeg-8.1.2-full_build\bin",
        f"{bin_name}.exe"
    )
    if os.path.isfile(legacy):
        return legacy

    raise FileNotFoundError(
        f"找不到 {bin_name}！請透過以下任一方式設定：\n"
        f"  1. 在 .env 中設定 {env_key}=<完整路徑>\n"
        f"  2. 將 {bin_name} 加入系統 PATH"
    )


def get_ffmpeg_bin() -> str:
    """取得 ffmpeg 執行檔路徑。"""
    return _resolve_bin("FFMPEG_BIN", "ffmpeg")


def get_ffprobe_bin() -> str:
    """取得 ffprobe 執行檔路徑。"""
    return _resolve_bin("FFPROBE_BIN", "ffprobe")


def get_edge_tts_bin() -> str:
    """取得 edge-tts 執行檔路徑。"""
    return os.path.join(os.path.dirname(sys.executable), "edge-tts")


# ──────────────────────────────────────
# 音訊時長偵測
# ──────────────────────────────────────

def get_mp3_duration(mp3_path: str) -> float:
    """
    使用 ffprobe 精確取得 MP3 檔案的時長（秒）。
    若偵測失敗，回傳預設值 30.0 秒並印出警告。
    """
    try:
        ffprobe = get_ffprobe_bin()
        cmd = [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            mp3_path
        ]
        result = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        return float(result.strip())
    except FileNotFoundError:
        print(f"  [警告] ffprobe 未安裝，無法精確偵測 {mp3_path} 的時長，使用預設值 30 秒。")
        return 30.0
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"  [警告] ffprobe 偵測時長失敗 ({e})，使用預設值 30 秒。")
        return 30.0


# ──────────────────────────────────────
# AI 圖片生成 (Pollinations.ai)
# ──────────────────────────────────────

def generate_image(prompt: str, save_path: str, style_suffix: str = "") -> bool:
    """
    使用 Pollinations.ai 產生免金鑰 AI 圖片。

    Args:
        prompt: 英文圖片描述
        save_path: 圖片儲存路徑
        style_suffix: 額外風格描述（例如 "traditional chinese ink painting"）

    Returns:
        True 表示成功，False 表示失敗（會自動建立黑底替代圖）。
    """
    print(f"    [圖] 正在生成圖片，關鍵字: {prompt[:40]}...")

    full_prompt = prompt
    if style_suffix:
        full_prompt += " " + style_suffix

    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=True"

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        with urllib.request.urlopen(req, timeout=120) as response, \
             open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print("    [圖] 圖片下載成功。")
        return True
    except Exception as e:
        print(f"    [圖] 圖片下載失敗: {e}，建立黑底替代圖。")
        try:
            ffmpeg = get_ffmpeg_bin()
            subprocess.run(
                [ffmpeg, "-y", "-f", "lavfi", "-i",
                 "color=c=black:s=1280x720:d=1", "-vframes", "1", save_path],
                check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            print("    [圖] ffmpeg 也找不到，無法建立替代圖。")
        return False
