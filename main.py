from pyrogram import Client, filters
import subprocess
import os
import asyncio
from traceback import print_exc
from subprocess import PIPE, STDOUT
from time import time

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']
bot_token = os.environ['BOT_TOKEN']

app = Client('m3u8', api_id, api_hash, bot_token=bot_token)

@app.on_message(filters.command('start'))
async def start(_, message):
    await message.reply(
        '''Send me a `.txt` file with m3u8 links (one per line, like `Title:URL`). I’ll convert and send them as .mp4 videos.'''
    )

@app.on_message(filters.document)
async def txt_handler(client, message):
    try:
        doc = message.document
        if not doc.file_name.endswith('.txt'):
            return await message.reply("Please send a `.txt` file only.")

        downloading = await message.reply("Reading your TXT file...")  
        file_path = await client.download_media(message=message)  

        # ✅ Extract m3u8 URLs from "Title:URL" format  
        with open(file_path, 'r', encoding='utf-8') as f:  
            links = [line.strip().split(":", 1)[-1] for line in f if "http" in line]  

        if not links:  
            return await downloading.edit("No valid m3u8 links found in the file.")  

        for link in links:  
            try:  
                await downloading.edit(f"Downloading via yt-dlp:\n`{link}`")  
                filename = f'{message.from_user.id}_{int(time())}.mp4'  

                # ✅ Removed `-f best` to avoid 404 errors  
                proc = await asyncio.create_subprocess_exec(  
                    'yt-dlp', '-o', filename, link,  
                    stdout=PIPE,  
                    stderr=PIPE  
                )  
                out, err = await proc.communicate()  

                if not os.path.exists(filename):  
                    raise Exception(f"yt-dlp failed\n{err.decode()}\n{out.decode()}")  

                await downloading.edit("Generating thumbnail...")  
                await asyncio.create_subprocess_shell(  
                    f'ffmpeg -i "{filename}" -ss 00:00:30.000 -vframes 1 "{filename}.jpg"',  
                    stdout=PIPE,  
                    stderr=PIPE  
                )  

                await downloading.edit("Getting duration...")  
                proc = await asyncio.create_subprocess_shell(  
                    f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{filename}"',  
                    stdout=PIPE,  
                    stderr=STDOUT  
                )  
                duration, _ = await proc.communicate()  

                await downloading.edit("Uploading to Telegram...")  

                await client.send_video(  
                    message.chat.id,  
                    filename,  
                    duration=int(float(duration.decode())),  
                    thumb=f'{filename}.jpg',  
                    caption=f'{filename}'  
                )  

                os.remove(filename)  
                os.remove(f'{filename}.jpg')  

            except Exception as e:  
                print("Error with link:", link)  
                print(e)  
                await message.reply(f"❌ Failed to process link:\n`{link}`\n\n{e}")  

        await downloading.edit("✅ All done.")  

    except Exception as e:  
        print_exc()  
        await message.reply("Something went wrong while handling your file.")

app.run()
