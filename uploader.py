import os
import time
import subprocess
import shlex
from utils import progress_callback

MAX_PART_SIZE = 1.9 * 1024 * 1024 * 1024  # ~1.9GB in bytes

def run_cmd(cmd):
    try:
        process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        return out.decode(errors="ignore"), err.decode(errors="ignore"), process.returncode
    except Exception as e:
        return "", str(e), 1

def get_video_duration(file_path):
    if not file_path or not os.path.exists(file_path):
        return 0
    cmd = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{file_path}"'
    out, _, _ = run_cmd(cmd)
    try:
        dur = float(out.strip())
        return int(dur if dur > 0 else 0)
    except (ValueError, TypeError):
        return 0

def generate_thumbnail(video_path, thumb_path):
    if not video_path or not os.path.exists(video_path):
        return
    cmd = f'ffmpeg -y -i "{video_path}" -ss 00:00:01 -vframes 1 "{thumb_path}"'
    run_cmd(cmd)

def ensure_mp4(file_path):
    if not file_path or not os.path.exists(file_path):
        return file_path
    if file_path.lower().endswith(".mp4"):
        return file_path
    new_path = os.path.splitext(file_path)[0] + ".mp4"
    cmd = f'ffmpeg -y -i "{file_path}" -c copy "{new_path}"'
    run_cmd(cmd)
    return new_path if os.path.exists(new_path) else file_path

def split_large_video(file_path):
    if not file_path or not os.path.exists(file_path):
        return []

    try:
        file_size = os.path.getsize(file_path)
    except OSError:
        return []

    if file_size <= MAX_PART_SIZE:
        return [file_path]

    duration = get_video_duration(file_path)
    if duration <= 0:
        return [file_path]  # Can't split without duration

    bytes_per_sec = file_size / duration
    if bytes_per_sec <= 0:
        return [file_path]

    split_duration = max(int(MAX_PART_SIZE / bytes_per_sec), 1)

    base_name = os.path.splitext(file_path)[0]
    cmd = f'ffmpeg -y -i "{file_path}" -c copy -map 0 -f segment -segment_time {split_duration} -reset_timestamps 1 "{base_name}_part%03d.mp4"'
    run_cmd(cmd)

    parts = []
    try:
        dir_path = os.path.dirname(file_path) or "."
        for f in sorted(os.listdir(dir_path)):
            if f.startswith(os.path.basename(base_name) + "_part") and f.endswith(".mp4"):
                parts.append(os.path.join(dir_path, f))
    except OSError:
        return [file_path]

    return parts or [file_path]

async def upload_to_telegram(app, chat_id, file_path, file_name, msg_id):
    try:
        if not file_path or not os.path.exists(file_path):
            await app.send_message(chat_id, f"❌ File `{file_name or 'Unknown'}` not found.")
            return

        mp4_path = ensure_mp4(file_path)
        parts = split_large_video(mp4_path)

        for idx, part_path in enumerate(parts, start=1):
            if not os.path.exists(part_path):
                continue

            part_name = f"{file_name} (Part {idx})" if len(parts) > 1 else (file_name or os.path.basename(part_path))
            thumb_path = part_path + ".jpg"
            generate_thumbnail(part_path, thumb_path)
            duration = get_video_duration(part_path)

            start_time = time.time()
            try:
                await app.send_video(
                    chat_id,
                    part_path,
                    caption=part_name,
                    duration=duration or None,
                    thumb=thumb_path if os.path.exists(thumb_path) else None,
                    supports_streaming=True,
                    progress=progress_callback,
                    progress_args=(None, start_time, "Uploading", part_name, chat_id, msg_id, app)
                )
            except Exception as send_err:
                await app.send_message(chat_id, f"❌ Failed to upload `{part_name}`\nError: {send_err}")

            # Safe cleanup
            for p in [part_path, thumb_path]:
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except OSError:
                    pass

    except Exception as e:
        await app.send_message(chat_id, f"❌ Upload failed for `{file_name or 'Unknown'}`\nError: {e}")

    finally:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass
