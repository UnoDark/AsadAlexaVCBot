import os
import re
import asyncio
from pyrogram import Client
from AsadAlexaVCBot.queues import QUEUE, add_to_queue
from config import bot, call_py, HNDLR, contact_filter, GRPPLAY
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


def ytsearch(query):
   try:
      search = VideosSearch(query, limit=1)
      for r in search.result()["result"]:
         ytid = r['id']
         if len(r['title']) > 34:
            songname = r['title'][:35] + "..."
         else:
            songname = r['title']
         url = f"https://www.youtube.com/watch?v={ytid}"
      return [songname, url]
   except Exception as e:
      print(e)
      return 0

# YTDL
# https://github.com/pytgcalls/pytgcalls/blob/dev/example/youtube_dl/youtube_dl_example.py
async def ytdl(link):
   proc = await asyncio.create_subprocess_exec(
       'youtube-dl',
       '-g',
       '-f',
       # CHANGE THIS BASED ON WHAT YOU WANT
       'bestaudio',
       f'{link}',
       stdout=asyncio.subprocess.PIPE,
       stderr=asyncio.subprocess.PIPE,
   )
   stdout, stderr = await proc.communicate()
   if stdout:
      return 1, stdout.decode().split('\n')[0]
   else:
      return 0, stderr.decode()


@Client.on_message(filters.command(['play'], prefixes=f"{HNDLR}"))
async def play(client, m: Message):
 if GRPPLAY or (m.from_user and m.from_user.is_contact) or m.outgoing:
   replied = m.reply_to_message
   chat_id = m.chat.id
   keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("❤️ ᴏᴡɴᴇʀ ❤️", url=f"https://t.me/OneUnoOnly"),
                InlineKeyboardButton("👨‍‍👧‍👦 ɢʀᴏᴜᴘ 👨‍👧‍👦", url=f"https://t.me/Hangawtss"),
            ]
        ]
    )
   if replied:
      if replied.audio or replied.voice:
         huehue = await replied.reply("👨‍⚖️ **Aɴᴀʟʏsɪɴɢ...**")
         dl = await replied.download()
         link = replied.link
         if replied.audio:
            if replied.audio.title:
               songname = replied.audio.title[:15] + "..."
            else:
               if replied.audio.file_name:
                  songname = replied.audio.file_name[:15] + "..."
               else:
                  songname = "Audio"
         elif replied.voice:
            songname = "Voice Note"
         if chat_id in QUEUE:
            pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
            await huehue.edit(f"Queued at **#{pos}**")
         else:
          try:
            await call_py.join_group_call(
               chat_id,
               AudioPiped(
                  dl,
               ),
               stream_type=StreamType().pulse_stream,
            )
            add_to_queue(chat_id, songname, dl, link, "Audio", 0)
            await huehue.edit(f"🎶 **sᴛᴀʀᴛᴇᴅ ᴘʟᴀʏɪɴɢ ᴀᴜᴅɪᴏ ▶** \n**🎧 sᴏɴɢ** : [{songname[:15]}] \n**💬 ᴄʜᴀᴛ** : `{chat_id}`")
          except Exception as hmme:
            await huehue.edit(hmme)
      else:
         if len(m.command) < 2:
            await m.reply("😜 **ʀᴇᴘʟᴀʏ ᴛᴏ ᴀɴ ᴀᴜᴅɪᴏ ᴏʀ ɢɪᴠᴇ ᴍᴇ ᴀ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ**")
         else:
            huehue = await m.reply("🔎 **Sᴇᴀʀᴄʜɪɴɢ...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search==0:
               await huehue.edit("🤔 **ɴᴏᴛʜɪɴɢ ғᴏᴜɴᴅ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴇᴀʀᴄʜ**")
            else:
               songname = search[0]
               url = search[1]
               hm, ytlink = await ytdl(url)
               if hm==0:
                  await huehue.edit(f"**YTDL ERROR ⚠️** ᴄᴏɴᴛᴀᴄᴛ ᴛᴏ ᴍʏ [ᴏᴡɴᴇʀ](t.me/OneUnoOnly)", disable_web_page_preview=True)
               else:
                  if chat_id in QUEUE:
                     pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                     await huehue.edit(f"**ʏᴏᴜʀ sᴏɴɢ ɪs ᴀᴛ ᴡᴀɪᴛɪɴɢ ᴘᴏsɪᴛɪᴏɴ** 👉 **#{pos}**")
                  else:
                     try:
                        await call_py.join_group_call(
                           chat_id,
                           AudioPiped(
                              ytlink,
                           ),
                           stream_type=StreamType().pulse_stream,
                        )
                        add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.edit(f"🎶 **sᴛᴀʀᴛᴇᴅ ᴘʟᴀʏɪɴɢ ᴀᴜᴅɪᴏ ▶** \n**🎧 sᴏɴɢ** : [{songname[:15]}] \n**💬 ᴄʜᴀᴛ** : `{chat_id}`")
                     except Exception as ep:
                        await huehue.edit(f"`{ep}`")
            
   else:
         if len(m.command) < 2:
            await m.reply("😜 **ʀᴇᴘʟᴀʏ ᴛᴏ ᴀɴ ᴀᴜᴅɪᴏ ᴏʀ ɢɪᴠᴇ ᴍᴇ ᴀ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ**")
         else:
            huehue = await m.reply("🔎 **Sᴇᴀʀᴄʜɪɴɢ...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search==0:
               await huehue.edit("🤔 **ɴᴏᴛʜɪɴɢ ғᴏᴜɴᴅ ᴛʀʏ ᴀɴᴏᴛʜᴇʀ sᴇᴀʀᴄʜ**")
            else:
               songname = search[0]
               url = search[1]
               hm, ytlink = await ytdl(url)
               if hm==0:
                  await huehue.edit(f"**YTDL ERROR ⚠️** ᴄᴏɴᴛᴀᴄᴛ ᴛᴏ ᴍʏ [ᴏᴡɴᴇʀ](t.me/Dr_Asad_Ali)", disable_web_page_preview=True)
               else:
                  if chat_id in QUEUE:
                     pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                     await huehue.edit(f"**ʏᴏᴜʀ sᴏɴɢ ɪs ᴀᴛ ᴡᴀɪᴛɪɴɢ ᴘᴏsɪᴛɪᴏɴ** 👉 **#{pos}**")
                  else:
                     try:
                        await call_py.join_group_call(
                           chat_id,
                           AudioPiped(
                              ytlink,
                           ),
                           stream_type=StreamType().pulse_stream,
                        )
                        add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.edit(f"🎶 **sᴛᴀʀᴛᴇᴅ ᴘʟᴀʏɪɴɢ ᴀᴜᴅɪᴏ ▶** \n**🎧 sᴏɴɢ** : [{songname[:15]}] \n**💬 ᴄʜᴀᴛ** : `{chat_id}`")
                     except Exception as ep:
                        await huehue.edit(f"`{ep}`")

@Client.on_message(filters.command(['stream'], prefixes=f"{HNDLR}"))
async def stream(client, m: Message):
 if GRPPLAY or (m.from_user and m.from_user.is_contact) or m.outgoing:
   chat_id = m.chat.id
   if len(m.command) < 2:
      await m.reply("`Give A Link/LiveLink/.m3u8 URL/YTLink to Play Audio from 🎶`")
   else: 
      link = m.text.split(None, 1)[1]
      huehue = await m.reply("`Trying to Play 📻`")

      # Filtering out YouTube URL's
      regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
      match = re.match(regex,link)
      if match:
         hm, livelink = await ytdl(link)
      else:
         livelink = link
         hm = 1
      
      if hm==0:
         await huehue.edit(f"**YTDL ERROR ⚠️** \n\n`{ytlink}`")
      else:
         if chat_id in QUEUE:
            pos = add_to_queue(chat_id, "Radio 📻", livelink, link, "Audio", 0)
            await huehue.edit(f"**ʏᴏᴜʀ sᴏɴɢ ɪs ᴀᴛ ᴡᴀɪᴛɪɴɢ ᴘᴏsɪᴛɪᴏɴ** 👉 **#{pos}**")
         else:
            try:
               await call_py.join_group_call(
                  chat_id,
                  AudioPiped(
                     livelink,
                  ),
                  stream_type=StreamType().pulse_stream,
               )
               add_to_queue(chat_id, "Radio 📻", livelink, link, "Audio", 0)
               await huehue.edit(f"Started Playing **[Radio 📻]({link})** in `{chat_id}`", disable_web_page_preview=True)
            except Exception as ep:
               await huehue.edit(f"`{ep}`")
