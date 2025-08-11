import aiohttp
import os

PIXELDRAIN_API = "https://pixeldrain.com/api"

async def fetch_pixeldrain_list(folder_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{PIXELDRAIN_API}/list/{folder_id}") as resp:
            if resp.status != 200:
                raise Exception(f"Error fetching PixelDrain list: {resp.status}")
            data = await resp.json()
            return data.get("files", [])

async def download_pixeldrain_file(file_id, file_name, save_path, progress, file_message, app):
    url = f"{PIXELDRAIN_API}/file/{file_id}"
    headers = {
        "Referer": "https://pixeldrain.com/",
        "User-Agent": "Mozilla/5.0"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Error downloading file: {resp.status}")
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            start_time = progress["start_time"]
            with open(save_path, "wb") as f:
                async for chunk in resp.content.iter_chunked(1024 * 256):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress["callback"](downloaded, total, None, start_time, "Downloading", file_name, progress["chat_id"], progress["msg_id"], app)
