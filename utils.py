import math
import time

last_update_time = {}

def human_readable_size(size):
    try:
        size = float(size or 0)
    except (ValueError, TypeError):
        return "0B"

    if size < 0:
        size = 0

    power = 1024
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < len(Dic_powerN) - 1:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}"

def human_readable_time(seconds):
    try:
        seconds = int(seconds or 0)
    except (ValueError, TypeError):
        return "0s"

    if seconds < 0:
        seconds = 0

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

async def progress_callback(current, total, message, start_time, action, file_name, chat_id, message_id, app):
    try:
        now = time.time()

        # prevent spam updates
        if current != total and now - last_update_time.get(message_id, 0) < 5:
            return

        last_update_time[message_id] = now

        # Sanitize inputs
        current = max(float(current or 0), 0)
        total = max(float(total or 0), 0)
        elapsed = max(now - (start_time or now), 0)

        # Safe calculations
        speed = current / elapsed if elapsed > 0 else 0
        eta = (total - current) / speed if speed > 0 else 0
        percent = (current * 100 / total) if total > 0 else 0
        percent = max(0, min(percent, 100))  # Clamp 0–100%

        # Build text
        text = (
            f"📂 **File:** `{file_name or 'Unknown'}`\n"
            f"⚙️ **Status:** {action or 'Processing'}\n"
            f"📊 **Progress:** {percent:.2f}%\n"
            f"📥 **Downloaded:** {human_readable_size(current)} / {human_readable_size(total)}\n"
            f"🚀 **Speed:** {human_readable_size(speed)}/s\n"
            f"⏳ **ETA:** {human_readable_time(eta)}"
        )

        #app.loop.create_task(app.edit_message_text(chat_id, message_id, text))
        await app.edit_message_text(chat_id, message_id, text)

    except Exception as e:
        print(f"[Progress Callback Error] {e}")
