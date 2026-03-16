import os

#create new application in telegram.org
api_id = int(os.getenv("uditya_tg_api_id"))
api_hash = os.getenv("uditya_tg_api_hash")
# when crete newbot not fatherbot
bot_token = os.getenv("uditya_tg_bot_token")

import nest_asyncio
nest_asyncio.apply()

from pyrogram import Client


app = Client("my_session", api_id=api_id, api_hash=api_hash)

await app.start()

print("Login successful!")

await app.stop()

from pyrogram import Client, filters
import subprocess

app = Client("mkv_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

user_files = {}


def get_audio_tracks(file):
    cmd = ["ffmpeg", "-i", file]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    
    tracks = []
    for line in result.stderr.split("\n"):
        if "Audio:" in line:
            tracks.append(line.strip())
    
    return tracks



@app.on_message(filters.document)
async def handle_mkv(client, message):

    if not message.document.file_name.endswith(".mkv"):
        await message.reply("Send MKV file only.")
        return

    await message.reply("Downloading file...")

    path = await message.download()

    tracks = get_audio_tracks(path)

    user_files[message.from_user.id] = path

    msg = "Audio tracks found:\n\n"
    for i, t in enumerate(tracks):
        msg += f"{i} → {t}\n"

    msg += "\nSend track number to keep."

    await message.reply(msg)



@app.on_message(filters.text)
async def select_track(client, message):

    user_id = message.from_user.id

    if user_id not in user_files:
        return

    if not message.text.isdigit():
        await message.reply("Send a valid track number.")
        return

    track = int(message.text)

    input_file = user_files[user_id]
    output_file = f'trackremoved_{message.document.file_name}'

    await message.reply("Processing video...")

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-map", "0:v",
        "-map", f"0:a:{track}",
        "-c", "copy",
        output_file
    ]

    subprocess.run(cmd)

    await message.reply("Uploading processed file...")

    await message.reply_document(output_file)


if __name__ == '__main__':
    app.run()
