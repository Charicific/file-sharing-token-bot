# https://www.youtube.com/channel/UC7tAa4hho37iNv731_6RIOg
import asyncio
import base64
import logging
import os
import random
import re
import string
import time

from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from pyrogram.raw.functions.contacts import ResolveUsername

from bot import Bot
from config import (
    ADMINS,
    FORCE_MSG,
    START_MSG,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT,
    OWNER_ID,
    CHANNEL_1_ID,
    CHANNEL_2_ID,
    CHANNEL_3_ID,
    CHANNEL_1_LINK,
    CHANNEL_2_LINK,
    CHANNEL_3_LINK,
)
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

"""add time in seconds for waiting before delete 
1 min = 60, 2 min = 60 × 2 = 120, 5 min = 60 × 5 = 300"""
# SECONDS = int(os.getenv("SECONDS", "1200"))

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    owner_id = ADMINS  # Fetch the owner's ID from config

    # Check if the user is the owner
    if id == owner_id:
        # Owner-specific actions
        # You can add any additional actions specific to the owner here
        await message.reply("You are the owner! Additional actions can be added here.")

    else:
        if not await present_user(id):
            try:
                await add_user(id)
            except:
                pass


        elif len(message.text) > 7:
            try:
                base64_string = message.text.split(" ", 1)[1]
            except:
                return
            _string = await decode(base64_string)
            argument = _string.split("-")
            if len(argument) == 3:
                try:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                except:
                    return
                if start <= end:
                    ids = range(start, end+1)
                else:
                    ids = []
                    i = start
                    while True:
                        ids.append(i)
                        i -= 1
                        if i < end:
                            break
            elif len(argument) == 2:
                try:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                except:
                    return
            temp_msg = await message.reply("Please wait...")
            try:
                messages = await get_messages(client, ids)
            except:
                await message.reply_text("Something went wrong..!")
                return
            await temp_msg.delete()
            
            snt_msgs = []
            
            for msg in messages:
                if bool(CUSTOM_CAPTION) & bool(msg.document):
                    caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
                else:
                    caption = "" if not msg.caption else msg.caption.html

                if DISABLE_CHANNEL_BUTTON:
                    reply_markup = msg.reply_markup
                else:
                    reply_markup = None

                try:
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)
                    snt_msgs.append(snt_msg)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    snt_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    snt_msgs.append(snt_msg)
                except:
                    pass

            SD = await message.reply_text("Baka! Files will be deleted After 30 minutes. Save them to the Saved Message now!")
            await asyncio.sleep(1800)

            for snt_msg in snt_msgs:
                try:
                    await snt_msg.delete()
                    await SD.delete()
                except:
                    pass

        else:
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("😊 About Me", callback_data = "about"),
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
                    ]
                ]
            )
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )
            return



    
        
#=====================================================================================##

WAIT_MSG = """"<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

#=====================================================================================##

    
    
async def is_user_in_channels(client: Client, user_id: int) -> bool:
    try:
        print(f"Checking membership for user {user_id} in channel {CHANNEL_1_ID}")
        member_1 = await client.get_chat_member(chat_id=int(CHANNEL_1_ID), user_id=user_id)
        member_2 = await client.get_chat_member(chat_id=int(CHANNEL_2_ID), user_id=user_id)
        member_3 = await client.get_chat_member(chat_id=int(CHANNEL_3_ID), user_id=user_id)
        if member_1.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return False
        if member_2.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return False
        if member_3.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return False
        return True
    except UserNotParticipant:
        print(f"User {user_id} is not a participant in one of the channels.")
        return False
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False


@Client.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_user_in_channels(client, user_id):
        buttons = [
            [
                InlineKeyboardButton(
                    "THE STERN LEGION",
                    url=CHANNEL_1_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    "Anime Plaza ||「𝚂𝚃𝚁」",
                    url=CHANNEL_2_LINK
                ),
                InlineKeyboardButton(
                    "Cinema Stack",
                    url=CHANNEL_3_LINK
                )
            ]
        ]
        try:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text='Try Again',
                        url=f"https://t.me/{client.username}?start={message.command[1]}"
                    )
                ]
            )
        except IndexError:
            pass
        await message.reply_text(
            "Please join the channels below to use the bot:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text("You have access to use the bot now.")
        
@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0
        
        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()
