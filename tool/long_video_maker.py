"""
long_video_maker.py — 全自動長片生成引擎
使用 Gemini API 自動撰寫連載劇本，搭配 Edge-TTS 配音與 Pollinations 生圖，
持續產出影片直到達成目標時長。
"""

import os
import sys
import time
import argparse
import subprocess
from dotenv import load_dotenv
from google import genai

from utils import (
    get_ffmpeg_bin, get_edge_tts_bin,
    get_mp3_duration, generate_image
)


def main():
    parser = argparse.ArgumentParser(description="全自動長片生成引擎")
    parser.add_argument("--prompt", required=True, help="故事主題")
    parser.add_argument("--outdir", required=True, help="輸出資料夾")
    parser.add_argument("--duration", type=int, default=3600, help="目標總時長(秒)")
    args = parser.parse_args()

    load_dotenv()
    api_keys_str = os.getenv("GEMINI_API_KEYS")
    if not api_keys_str:
        print("請在 .env 設定 GEMINI_API_KEYS (使用逗號分隔多組金鑰)")
        sys.exit(1)

    api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    key_idx = 0
    client = genai.Client(api_key=api_keys[key_idx])

    os.makedirs(args.outdir, exist_ok=True)

    ffmpeg = get_ffmpeg_bin()
    edge_tts = get_edge_tts_bin()

    total_duration = 0.0
    chapter = 1
    chapter_files = []

    # 手動維護劇情歷史，方便切換 API 金鑰時不會遺失脈絡
    story_history = ""

    print(f"開始生成長篇影片，目標長度：{args.duration} 秒")

    with open(os.path.join(args.outdir, "story.txt"), "w", encoding="utf-8") as f_story:
        f_story.write(f"主題：{args.prompt}\n\n")

    while total_duration < args.duration:
        print(f"\n--- 正在生成第 {chapter} 集 ---")

        system_prompt = (
            f"你是一個專職寫作寫實都市劇的短劇編劇。我們正在連載一部長篇影片，主題是：{args.prompt}。\n"
            f"這是到目前為止的劇情：\n{story_history[-3000:] if story_history else '（目前是第一集，請直接開頭）'}\n\n"
            "請緊接著上述情節，寫出「下一集」的劇本。每一集字數約 300~400 字。\n"
            "要求：\n"
            "1. 劇情必須貼近現實，無修仙、無魔法，著重商戰、人際、情感與逆襲。結尾要留懸念。\n"
            "2. 不要任何導演指示、旁白標籤，只輸出純文字對白與動作描述，因為這會直接轉為語音。\n"
            "3. 在劇本最後面，請加上一行專屬指令： [IMAGE_PROMPT: 這裡寫一段英文的畫面描述，用來生成符合本集核心場景的圖片。]"
        )

        # 1. 生成劇本 (加入 API 金鑰輪替機制)
        content = ""
        while not content:
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=system_prompt
                )
                content = response.text
            except Exception as e:
                err_msg = str(e)
                print(f"Gemini API 錯誤: {err_msg}")
                if "429" in err_msg or "quota" in err_msg.lower():
                    print("    [!] 速率限制，切換金鑰並嘗試 WARP 換 IP...")
                    key_idx = (key_idx + 1) % len(api_keys)
                    client = genai.Client(api_key=api_keys[key_idx])

                    try:
                        subprocess.run(["warp-cli", "disconnect"], check=False,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(2)
                        subprocess.run(["warp-cli", "connect"], check=False,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print("    [!] IP 切換指令已送出，等待 8 秒...")
                        time.sleep(8)
                    except FileNotFoundError:
                        print("    [!] warp-cli 未安裝，等待 60 秒後重試...")
                        time.sleep(60)
                else:
                    time.sleep(5)

        # 解析文字與 Image Prompt
        image_prompt = "A cinematic realistic shot of an urban city"
        script_text = content
        if "[IMAGE_PROMPT:" in content:
            parts = content.split("[IMAGE_PROMPT:")
            script_text = parts[0].strip()
            image_prompt = parts[1].replace("]", "").strip()

        # 更新歷史紀錄
        story_history += f"\n第 {chapter} 集：\n{script_text}\n"

        print(f"    [編劇] 完成。字數：{len(script_text)}")
        with open(os.path.join(args.outdir, "story.txt"), "a", encoding="utf-8") as f_story:
            f_story.write(f"\n--- 第 {chapter} 集 ---\n{script_text}\n")

        # 2. 生成配音與字幕
        audio_path = os.path.join(args.outdir, f"audio_{chapter}.mp3")
        vtt_path = os.path.join(args.outdir, f"subs_{chapter}.vtt")

        edge_cmd = [edge_tts, "--voice", "zh-CN-YunxiNeural",
                    "--text", script_text,
                    "--write-media", audio_path,
                    "--write-subtitles", vtt_path]
        subprocess.run(edge_cmd, check=True, stdout=subprocess.DEVNULL)

        # 改用 ffprobe 精確時長（統一使用 utils 模組）
        duration = get_mp3_duration(audio_path)
        total_duration += duration
        print(f"    [配音] 完成。本集長度：{duration:.1f} 秒 (總進度: {total_duration:.1f}/{args.duration} 秒)")

        # 3. 生成圖片
        img_path = os.path.join(args.outdir, f"image_{chapter}.jpg")
        generate_image(image_prompt, img_path)

        # 4. 合成本集影片 (靜態圖片 + 音軌 + 字幕)
        vid_path = os.path.join(args.outdir, f"chapter_{chapter}.mp4")
        ffmpeg_cmd = [
            ffmpeg, "-y",
            "-loop", "1", "-framerate", "2",
            "-i", img_path,
            "-i", audio_path,
            "-vf", f"subtitles=subs_{chapter}.vtt",
            "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
            "-b:a", "192k", "-pix_fmt", "yuv420p",
            "-shortest", vid_path
        ]
        print("    [合成] 正在打包本集影片...")
        subprocess.run(ffmpeg_cmd, cwd=args.outdir, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        chapter_files.append(f"chapter_{chapter}.mp4")

        chapter += 1
        time.sleep(2)  # 避免 API 頻率限制

    # 5. 合併所有章節
    print("\n所有章節生成完畢，正在合併成最終長片...")
    list_path = os.path.join(args.outdir, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for cf in chapter_files:
            f.write(f"file '{cf}'\n")

    final_vid = os.path.join(args.outdir, "FINAL_MOVIE.mp4")
    concat_cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", "list.txt",
        "-c", "copy", final_vid
    ]
    subprocess.run(concat_cmd, cwd=args.outdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"恭喜！影片合併完成。最終檔案位於：{final_vid}")


if __name__ == "__main__":
    main()
