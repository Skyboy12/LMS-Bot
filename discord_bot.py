

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from send_packet import SEND_PACKET
import asyncio
import logging

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


class DiscordBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        logging.info(f"Logged in as {self.user.name} ({self.user.id})")
        logging.info("--------------------")
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Bạn đã nhập thiếu tham số cần thiết cho lệnh này. 😟')
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            logging.error(f"Lỗi không xác định: {error}")
            await ctx.send('Đã có lỗi xảy ra trong lúc thực thi lệnh. 😵')

bot = DiscordBot()

@bot.command(name='ping')
async def ping_command(ctx):
    logging.info(f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh ping.")
    await ctx.send("Pong!")

@bot.command(name='slide')
async def slide_command(ctx, session_id: str, slide_id: int):
    logging.info(f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh slide với session_id: {session_id} và slide_id: {slide_id}.")
    await ctx.send(f"Đang xử lý slide `{slide_id}`...")
    loop = asyncio.get_running_loop()
    
    result = await loop.run_in_executor(
        None, SEND_PACKET.SLIDE, session_id, slide_id)
    await ctx.send(result[0])
    logging.info(result[1])
    await ctx.send(result[2])

@bot.command(name='quiz')
async def quiz_command(ctx, session_id: str, quiz_id: int):
    logging.info(f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh quiz với session_id: {session_id} và quiz_id: {quiz_id}.")
    await ctx.send(f"Đang tìm đáp án quiz `{quiz_id}`... Việc này có thể mất một lúc.")
    loop = asyncio.get_running_loop()
    
    result = await loop.run_in_executor(
        None, SEND_PACKET.QUIZ, session_id, quiz_id)
    await ctx.send(result)

@bot.command(name='add_quiz')
async def add_quiz_command(ctx, quiz_id: int, start: int, amount: int):
    logging.info(f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh add_quiz với quiz_id: {quiz_id}, start: {start}, amount: {amount}.")
    SEND_PACKET.ADD_QUIZ_DATA(quiz_id, start, amount)
    await ctx.send(f"Đã thêm quiz `{quiz_id}` với start: {start} và amount: {amount}.")

@bot.command(name='fix_quiz')
async def fix_quiz_command(ctx, quiz_id: int, list_str):
    logging.info(f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh fix_quiz với quiz_id: {quiz_id}.")
    list_ = list(map(int, list_str.split(",")))
    SEND_PACKET.FIX_QUIZ_DATA_LIST(quiz_id, list_)
    await ctx.send(f"Đã sửa dữ liệu quiz `{quiz_id}`.")
if __name__ == "__main__":
    bot.run(TOKEN)
