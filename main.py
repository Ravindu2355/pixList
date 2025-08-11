import os
from pyrogram import Client, filters
from handlers import start_command, count_command, pixlist_command

apiid=os.getenv("apiid","")
apihash=os.getenv("apihash","")
btk=os.getenv("tk")


app = Client(
    "pixeldrain_bot",
    bot_token=btk,
    api_id=apiid,  # Replace with your API ID
    api_hash=apihash  # Replace with your API Hash
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    await start_command(client, message)

@app.on_message(filters.command("count"))
async def count_handler(client, message):
    await count_command(client, message)

@app.on_message(filters.command("pixlist"))
async def pixlist_handler(client, message):
    await pixlist_command(client, message)

app.run()
