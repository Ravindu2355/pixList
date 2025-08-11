import math
import time

last_update_time = {}

def human_readable_size(size):
    if size is None:
        return "0B"
    power = 1024
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {Dic_powerN[n]}"

def human_readable_time(seconds):
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

def progress_callback(current, total, message, start_time, action, file_name, chat_id, message_id, app):
    now = time.time()
    if current != total and now - last_update_time.get(message_id, 0) < 5:
        return

    last_update_time[message_id] = now
    elapsed = now - start_time
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    percent = (current * 100) / total if total != 0 else 0

    text = (
        f"📂 **File:** `{file_name}`\n"
        f"⚙️ **Status:** {action}\n"
        f"📊 **Progress:** {percent:.2f}%\n"
        f"📥 **Downloaded:** {human_readable_size(current)} / {human_readable_size(total)}\n"
        f"🚀 **Speed:** {human_readable_size(speed)}/s\n"
        f"⏳ **ETA:** {human_readable_time(eta)}"
    )

    app.loop.create_task(app.edit_message_text(chat_id, message_id, text))
