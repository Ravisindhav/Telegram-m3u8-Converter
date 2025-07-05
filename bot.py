from pyrogram import Client, filters import os import asyncio from traceback import print_exc from subprocess import PIPE, STDOUT from time import time

api_id = os.environ['API_ID'] api_hash = os.environ['API_HASH'] bot_token = os.environ['BOT_TOKEN']

app = Client('m3u8', api_id, api_hash, bot_token=bot_token)

@app.on_message(filters.command('start')) async def start(_, message): await message.reply(f'''Kullanım: /convert TXT dosyası gönderin. Github Repo: Click to go. ''')

@app.on_message(filters.command(['convert', 'cevir'])) async def convert(client, message): await message.reply("📄 Lütfen içinde m3u8 linkleri olan .txt dosyasını gönderin.") try: incoming = await client.listen(message.chat.id, timeout=60) if incoming.document and incoming.document.file_name.endswith(".txt"): file_path = await client.download_media(incoming.document) with open(file_path, 'r') as f: links = f.read().splitlines()

for link in links:
            if link.strip():
                await process_link(client, message, link.strip())
    else:
        await message.reply("❌ Lütfen doğru .txt dosya gönderin.")
except asyncio.TimeoutError:
    await message.reply("⌛ Zamanaşımı. Lütfen tekrar deneyin.")
except Exception as e:
    print_exc()
    await message.reply("🚫 Bir hata oluştu.")

async def process_link(client, message, link): info = await message.reply(f'🔗 İşleniyor: {link}') filename = f'{message.from_user.id}{int(time())}' proc = await asyncio.create_subprocess_shell( f'ffmpeg -i "{link}" -c copy -bsf:a aac_adtstoasc {filename}.mp4', stdout=PIPE, stderr=PIPE ) await _info.edit("📦 MP4'e dönüştürülüyor...") out, err = await proc.communicate() print('\n\n\n', out, err, sep='\n') try: await _info.edit('🖼️ Thumbnail ekleniyor...') proc2 = await asyncio.create_subprocess_shell( f'ffmpeg -i {filename}.mp4 -ss 00:00:30.000 -vframes 5 {filename}.jpg', stdout=PIPE, stderr=PIPE ) await proc2.communicate()

await _info.edit('⏳ Süre alınıyor...')
    proc3 = await asyncio.create_subprocess_shell(
        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}.mp4',
        stdout=PIPE,
        stderr=STDOUT
    )
    duration, _ = await proc3.communicate()

    await _info.edit("📤 Telegram'a yükleniyor...")
    def progress(current, total):
        print(message.from_user.first_name, ' -> ', current, '/', total, sep='')

    await client.send_video(
        message.chat.id,
        f'{filename}.mp4',
        duration=int(float(duration.decode())),
        thumb=f'{filename}.jpg',
        caption=f'{filename}',
        progress=progress
    )
    os.remove(f'{filename}.mp4')
    os.remove(f'{filename}.jpg')
except Exception:
    print_exc()
    await _info.edit('❌ Bir hata oluştu.')

app.run()

