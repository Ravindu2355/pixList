import os
import time
import subprocess
import shlex
from utils import progress_callback

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

async def upload_to_telegram(app, chat_id, file_path, file_name, msg_id):
    try:
        # Convert to mp4 if not already
        mp4_path = ensure_mp4(file_path)

        # Generate thumbnail & get duration
        thumb_path = mp4_path + ".jpg"
        generate_thumbnail(mp4_path, thumb_path)
        duration = get_video_duration(mp4_path)

        start_time = time.time()

        await app.send_video(
            chat_id,
            mp4_path,
            caption=file_name,
            duration=duration,
            thumb=thumb_path,
            supports_streaming=True,
            progress=progress_callback,
            progress_args=(None, start_time, "Uploading", file_name, chat_id, msg_id, app)
        )

    except Exception as e:
        await app.edit_message_text(chat_id, msg_id, f"❌ Upload failed for `{file_name}`\nError: {e}")

    finally:
        # Cleanup files
        if os.path.exists(file_path):
            os.remove(file_path)
        if mp4_path != file_path and os.path.exists(mp4_path):
            os.remove(mp4_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
