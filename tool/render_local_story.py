import os
import sys
import glob
import argparse
import subprocess
import urllib.parse
import urllib.request
import re

def get_mp3_duration(mp3_path):
    ffprobe_bin = r"C:\Users\asus-pc\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe"
    try:
        cmd = [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", mp3_path]
        result = subprocess.check_output(cmd, text=True)
        return float(result.strip())
    except:
        return 30.0 

def generate_image(prompt, save_path):
    print(f"    [圖] 正在生成圖片，關鍵字: {prompt[:30]}...")
    encoded_prompt = urllib.parse.quote(prompt + " traditional chinese ink painting, ancient style, classical chinese art, masterpiece")
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=True"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
            out_file.write(response.read())
        print("    [圖] 圖片下載成功。")
    except Exception as e:
        print(f"    [圖] 圖片下載失敗: {e}")
        ffmpeg_bin = r"C:\Users\asus-pc\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
        subprocess.run([ffmpeg_bin, "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=1", "-vframes", "1", save_path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True, help="輸出資料夾 (例如 小說產出庫\百萬鉅作_商業帝國)")
    args = parser.parse_args()

    ffmpeg_bin = r"C:\Users\asus-pc\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
    edge_tts_bin = os.path.join(os.path.dirname(sys.executable), "edge-tts")
    
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
            edge_cmd = [edge_tts_bin, "--voice", "zh-CN-YunxiNeural", "--text", script_text, "--write-media", audio_path, "--write-subtitles", vtt_path]
            subprocess.run(edge_cmd, check=True, stdout=subprocess.DEVNULL)
        
        duration = get_mp3_duration(audio_path)
        total_duration += duration
        print(f"    [配音] 準備完畢。長度: {duration:.1f} 秒")

        # 2. 處理圖片
        if not os.path.exists(img_path):
            generate_image(image_prompt, img_path)
        else:
            print("    [圖] 圖片已存在，跳過生成。")

        # 3. 合成影片
        if not os.path.exists(vid_path):
            fade_out_start = max(0, duration - 1.0)
            vf_filter = f"fade=t=in:st=0:d=1,fade=t=out:st={fade_out_start:.2f}:d=1,subtitles=subs_{chap_num}.vtt"
            
            ffmpeg_cmd = [
                ffmpeg_bin, "-y",
                "-loop", "1", "-framerate", "2",
                "-i", f"image_{chap_num}.jpg",
                "-i", f"audio_{chap_num}.mp3",
                "-vf", vf_filter,
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac",
                "-b:a", "192k", "-pix_fmt", "yuv420p",
                "-shortest", f"chapter_{chap_num}.mp4"
            ]
            print("    [合成] 正在打包本集影片...")
            subprocess.run(ffmpeg_cmd, cwd=args.outdir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("    [合成] 影片已存在，跳過合成。")
            
        chapter_vids.append(f"chapter_{chap_num}.mp4")

    # 4. 最終合併
    print(f"\n所有章節處理完畢，目前總時長: {total_duration:.1f} 秒。正在合併...")
    list_path = os.path.join(args.outdir, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for vid in chapter_vids:
            f.write(f"file '{vid}'\n")
            
    final_vid_base = "FINAL_MOVIE.mp4"
    concat_cmd = [
        ffmpeg_bin, "-y", "-f", "concat", "-safe", "0",
        "-i", "list.txt",
        "-c", "copy", final_vid_base
    ]
    subprocess.run(concat_cmd, cwd=args.outdir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"渲染完成！最終影片位於：{os.path.join(args.outdir, final_vid_base)}")

if __name__ == "__main__":
    main()
