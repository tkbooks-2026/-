"""
render_local_story.py — 本機渲染引擎
讀取已有的章節劇本 (chapters/chapter_X.txt)，依序進行配音、生圖、合成影片，
最後合併為一部完整的長片。
"""

import os
import sys
import glob
import argparse
import subprocess
import re

from utils import (
    get_ffmpeg_bin, get_ffprobe_bin, get_edge_tts_bin,
    get_mp3_duration, generate_image
)

# 水墨畫風格後綴
INK_STYLE = "traditional chinese ink painting, ancient style, classical chinese art, masterpiece"


def main():
    parser = argparse.ArgumentParser(description="本機小說影片渲染引擎")
    parser.add_argument("--outdir", required=True, help="輸出資料夾 (例如 小說產出庫/百萬鉅作_商業帝國)")
    args = parser.parse_args()

    ffmpeg = get_ffmpeg_bin()
    edge_tts = get_edge_tts_bin()

    chapters_dir = os.path.join(args.outdir, "chapters")
    if not os.path.exists(chapters_dir):
        print(f"找不到章節資料夾: {chapters_dir}")
        sys.exit(1)

    # 找出所有 chapter_X.txt
    txt_files = glob.glob(os.path.join(chapters_dir, "chapter_*.txt"))

    def extract_chapter_num(filename):
        match = re.search(r'chapter_(\d+)\.txt', filename)
        return int(match.group(1)) if match else 0

    txt_files.sort(key=extract_chapter_num)

    if not txt_files:
        print("沒有找到任何劇本檔！")
        return

    chapter_vids = []
    total_duration = 0.0

    print("--- 開始本機影片渲染引擎 ---")

    for txt_file in txt_files:
        chap_num = extract_chapter_num(txt_file)
        print(f"\n處理第 {chap_num} 集: {os.path.basename(txt_file)}")

        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()

        script_text = content
        image_prompt = "A cinematic realistic shot of an urban city"

        if "[IMAGE_PROMPT:" in content:
            parts = content.split("[IMAGE_PROMPT:")
            script_text = parts[0].strip()
            image_prompt = parts[1].replace("]", "").strip()

        audio_path = os.path.join(args.outdir, f"audio_{chap_num}.mp3")
        vtt_path = os.path.join(args.outdir, f"subs_{chap_num}.vtt")
        img_path = os.path.join(args.outdir, f"image_{chap_num}.jpg")
        vid_path = os.path.join(args.outdir, f"chapter_{chap_num}.mp4")

        # 1. 處理配音
        if not os.path.exists(audio_path):
            edge_cmd = [edge_tts, "--voice", "zh-CN-YunxiNeural",
                        "--text", script_text,
                        "--write-media", audio_path,
                        "--write-subtitles", vtt_path]
            subprocess.run(edge_cmd, check=True, stdout=subprocess.DEVNULL)

        trimmed_audio_path = os.path.join(args.outdir, f"trimmed_audio_{chap_num}.mp3")
        if not os.path.exists(trimmed_audio_path):
            trim_cmd = [
                ffmpeg, "-y", "-i", audio_path,
                "-af", "areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=-50dB,areverse",
                trimmed_audio_path
            ]
            subprocess.run(trim_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        duration = get_mp3_duration(trimmed_audio_path)
        total_duration += duration
        print(f"    [配音] 去靜音處理完畢。長度: {duration:.1f} 秒")

        # 2. 處理圖片
        if not os.path.exists(img_path):
            generate_image(image_prompt, img_path, style_suffix=INK_STYLE)
        else:
            print("    [圖] 圖片已存在，跳過生成。")

        # 3. 合成影片
        if not os.path.exists(vid_path):
            vf_filter = (
                f"subtitles=subs_{chap_num}.vtt:force_style='FontSize=40,Outline=2,Shadow=1,MarginV=30'"
            )

            # 使用 -t 精準截斷影片長度（取代不可靠的 -shortest）
            # -shortest 在 loop+stillimage 模式下會因編碼器 buffer
            # 導致影像軌比音訊軌多出約 3 秒的空白尾巴
            ffmpeg_cmd = [
                ffmpeg, "-y",
                "-loop", "1", "-framerate", "15",
                "-i", f"image_{chap_num}.jpg",
                "-i", f"trimmed_audio_{chap_num}.mp3",
                "-t", f"{duration:.3f}",
                "-vf", vf_filter,
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
                "-b:a", "192k", "-pix_fmt", "yuv420p",
                f"chapter_{chap_num}.mp4"
            ]
            print("    [合成] 正在打包本集影片...")
            subprocess.run(ffmpeg_cmd, cwd=args.outdir, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("    [合成] 影片已存在，跳過合成。")

        chapter_vids.append(f"chapter_{chap_num}.mp4")

    # 4. 最終合併
    print(f"\n所有章節處理完畢，目前總時長: {total_duration:.1f} 秒。正在合併...")
    list_path = os.path.join(args.outdir, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for vid in chapter_vids:
            f.write(f"file '{vid}'\n")

    final_vid_base = "FINAL_MOVIE_15fps.mp4"
    concat_cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", "list.txt",
        "-c", "copy", final_vid_base
    ]
    subprocess.run(concat_cmd, cwd=args.outdir, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"渲染完成！最終影片位於：{os.path.join(args.outdir, final_vid_base)}")


if __name__ == "__main__":
    main()
