import asyncio
import os
import time
from pixeldrain import fetch_pixeldrain_list, download_pixeldrain_file
from uploader import upload_to_telegram
from utils import progress_callback

active_tasks = []

async def start_command(client, message):
    await message.reply_text("Send `/pixlist <folder_id>` to start downloading from PixelDrain.")

async def count_command(client, message):
    await message.reply_text(f"Currently running tasks: {len(active_tasks)}")

async def pixlist_command(client, message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        return await message.reply_text("Usage: /pixlist <folder_id>")

    folder_id = args[1].strip()
    files = await fetch_pixeldrain_list(folder_id)
    if not files:
        return await message.reply_text("No files found in this PixelDrain folder.")

    status_msg = await message.reply_text(f"Found {len(files)} files. Starting download...")

    for file_info in files:
        file_name = file_info["name"]
        file_id = file_info["id"]
        save_path = f"/tmp/{file_name}"

        progress = {
            "start_time": time.time(),
            "callback": progress_callback,
            "chat_id": message.chat.id,
            "msg_id": status_msg.id
        }

        await download_pixeldrain_file(file_id, file_name, save_path, progress, status_msg, client)
        await upload_to_telegram(client, os.getenv("channel",message.chat.id), save_path, file_name, status_msg.id)
        await asyncio.sleep(5)
