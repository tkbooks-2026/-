"""
⚠️  此腳本已廢棄 (Deprecated)
請改用：
  - render_local_story.py  → 渲染已有的劇本
  - long_video_maker.py    → 全自動 AI 生成劇本 + 渲染

保留此檔案僅供歷史參考。
──────────────────────────────────────

video_builder.py — 最初版本的單集影片合成工具
使用背景影片 + Edge-TTS 配音 + 字幕疊加，產出單一集影片。
"""

import argparse
import subprocess
import os
import sys

from utils import get_ffmpeg_bin, get_edge_tts_bin


def main():
    parser = argparse.ArgumentParser(description="[已廢棄] 單集影片合成工具")
    parser.add_argument("--text", required=True, help="要唸出來的劇本文字")
    parser.add_argument("--bg", required=True, help="背景影片路徑 (例如 tool/background.mp4)")
    parser.add_argument("--outdir", required=True, help="輸出的資料夾路徑")
    parser.add_argument("--voice", default="zh-CN-YunxiNeural", help="Edge TTS 語音角色")
    args = parser.parse_args()

    print("⚠️  警告：此腳本已廢棄，建議改用 render_local_story.py 或 long_video_maker.py")

    # 1. 建立輸出資料夾
    os.makedirs(args.outdir, exist_ok=True)

    audio_path = os.path.join(args.outdir, "audio.mp3")
    vtt_path = os.path.join(args.outdir, "subs.vtt")
    output_path = os.path.join(args.outdir, "output.mp4")

    print(f"[*] 正在生成語音與字幕 (角色: {args.voice})...")
    # 2. 呼叫 edge-tts
    edge_tts = get_edge_tts_bin()
    edge_cmd = [
        edge_tts,
        "--voice", args.voice,
        "--text", args.text,
        "--write-media", audio_path,
        "--write-subtitles", vtt_path
    ]
    try:
        subprocess.run(edge_cmd, check=True)
        print("[+] 語音與字幕生成完成。")
    except subprocess.CalledProcessError as e:
        print(f"[-] edge-tts 執行失敗: {e}")
        sys.exit(1)

    print("[*] 正在使用 FFmpeg 合成影片...")
    # 3. 呼叫 ffmpeg 合成
    ffmpeg = get_ffmpeg_bin()
    ffmpeg_cmd = [
        ffmpeg,
        "-y",
        "-stream_loop", "-1",
        "-i", os.path.abspath(args.bg),
        "-i", "audio.mp3",
        "-filter_complex", "subtitles=subs.vtt",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "output.mp4"
    ]

    try:
        # 注意：移除了 shell=True，這在原版中是安全風險
        subprocess.run(ffmpeg_cmd, cwd=args.outdir, check=True)
        print(f"[+] 影片合成成功！成品位於: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[-] FFmpeg 合成失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
