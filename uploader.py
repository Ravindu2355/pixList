import os
import time
import subprocess
import shlex
from utils import progress_callback

MAX_PART_SIZE = 1.9 * 1024 * 1024 * 1024  # ~1.9GB in bytes

def run_cmd(cmd):
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode(), err.decode(), process.returncode

def get_video_duration(file_path):
    cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{file_path}"'
    out, _, _ = run_cmd(cmd)
    try:
        return int(float(out.strip()))
    except:
        return 0

def generate_thumbnail(video_path, thumb_path):
    cmd = f'ffmpeg -y -i "{video_path}" -ss 00:00:01 -vframes 1 "{thumb_path}"'
    run_cmd(cmd)

def ensure_mp4(file_path):
    if file_path.lower().endswith(".mp4"):
        return file_path
    new_path = os.path.splitext(file_path)[0] + ".mp4"
    cmd = f'ffmpeg -y -i "{file_path}" -c copy "{new_path}"'
    run_cmd(cmd)
    return new_path

def split_large_video(file_path):
    parts = []
    file_size = os.path.getsize(file_path)
    if file_size <= MAX_PART_SIZE:
        return [file_path]

    # Get duration to split proportionally
    duration = get_video_duration(file_path)
    bytes_per_sec = file_size / duration
    split_duration = int(MAX_PART_SIZE / bytes_per_sec)

    base_name = os.path.splitext(file_path)[0]
    cmd = f'ffmpeg -y -i "{file_path}" -c copy -map 0 -f segment -segment_time {split_duration} -reset_timestamps 1 "{base_name}_part%03d.mp4"'
    run_cmd(cmd)

    for f in sorted(os.listdir(os.path.dirname(file_path) or ".")):
        if f.startswith(os.path.basename(base_name) + "_part") and f.endswith(".mp4"):
            parts.append(os.path.join(os.path.dirname(file_path), f))

    return parts

async def upload_to_telegram(app, chat_id, file_path, file_name, msg_id):
    try:
        mp4_path = ensure_mp4(file_path)
        parts = split_large_video(mp4_path)

        for idx, part_path in enumerate(parts, start=1):
            part_name = f"{file_name} (Part {idx})" if len(parts) > 1 else file_name
            thumb_path = part_path + ".jpg"
            generate_thumbnail(part_path, thumb_path)
            duration = get_video_duration(part_path)

            start_time = time.time()
            await app.send_video(
                chat_id,
                part_path,
                caption=part_name,
                duration=duration,
                thumb=thumb_path,
                supports_streaming=True,
                progress=progress_callback,
                progress_args=(None, start_time, "Uploading", part_name, chat_id, msg_id, app)
            )

            os.remove(part_path)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)

    except Exception as e:
        await app.edit_message_text(chat_id, msg_id, f"❌ Upload failed for `{file_name}`\nError: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
