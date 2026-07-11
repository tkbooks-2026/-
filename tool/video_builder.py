import argparse
import subprocess
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="自動化影片生成工具")
    parser.add_argument("--text", required=True, help="要唸出來的劇本文字")
    parser.add_argument("--bg", required=True, help="背景影片路徑 (例如 tool/background.mp4)")
    parser.add_argument("--outdir", required=True, help="輸出的資料夾路徑")
    parser.add_argument("--voice", default="zh-CN-YunxiNeural", help="Edge TTS 語音角色")
    args = parser.parse_args()

    # 1. 建立輸出資料夾
    os.makedirs(args.outdir, exist_ok=True)
    
    audio_path = os.path.join(args.outdir, "audio.mp3")
    vtt_path = os.path.join(args.outdir, "subs.vtt")
    output_path = os.path.join(args.outdir, "output.mp4")

    print(f"[*] 正在生成語音與字幕 (角色: {args.voice})...")
    # 2. 呼叫 edge-tts
    edge_tts_bin = os.path.join(os.path.dirname(sys.executable), "edge-tts")
    edge_cmd = [
        edge_tts_bin,
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
    # -stream_loop -1 讓背景影片無限循環，直到聲音結束 (-shortest)
    # vtt 路徑在 Windows 的 ffmpeg subtitles filter 中需要處理跳脫字元，
    # 為了安全，我們先將 vtt 內容的引號處理好，或使用絕對路徑。
    # 最安全的做法是將工作目錄切換到 outdir，這樣 subtitles filter 只需要檔名。
    
    ffmpeg_bin = r"C:\Users\asus-pc\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
    ffmpeg_cmd = [
        ffmpeg_bin,
        "-y", # 覆寫檔案
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
        subprocess.run(ffmpeg_cmd, cwd=args.outdir, check=True, shell=True)
        print(f"[+] 影片合成成功！成品位於: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"[-] FFmpeg 合成失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
