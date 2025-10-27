

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
async def add_quiz_command(ctx, id: int, quiz_ids: str, starts: str, amounts: str):
    """
    Thêm dữ liệu quiz vào quiz_list.json.

    Cách dùng (ví dụ):
    !add_quiz 150 "[1001,1002,1003]" "[0,0,1]" "[4,4,2]"
    hoặc dùng danh sách phân tách bởi dấu phẩy:
    !add_quiz 150 1001,1002,1003 0,0,1 4,4,2
    """

    def parse_int_list(s: str):
        # Cho phép cả JSON array ("[1,2,3]") hoặc danh sách phân tách bằng dấu phẩy ("1,2,3")
        s = s.strip()
        try:
            if s.startswith("[") and s.endswith("]"):
                data = json.loads(s)
                if not isinstance(data, list):
                    raise ValueError("Giá trị không phải là danh sách")
                return [int(x) for x in data]
        except Exception as e:
            raise ValueError(f"Không thể phân tích danh sách từ chuỗi JSON: {e}")

        # Fallback: comma-separated
        try:
            items = [p.strip() for p in s.split(",") if p.strip() != ""]
            if not items:
                return []
            return [int(x) for x in items]
        except Exception as e:
            raise ValueError(f"Không thể phân tích danh sách từ chuỗi phân tách dấu phẩy: {e}")

    logging.info(
        f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh add_quiz với id: {id}, quiz_ids: {quiz_ids}, starts: {starts}, amounts: {amounts}."
    )

    # Trì hoãn phản hồi để tránh timeout nếu parsing/cập nhật mất thời gian
    await ctx.send("Đang xử lý thêm dữ liệu quiz...")

    import json  # đảm bảo có json cho parse_int_list JSON branch

    try:
        quiz_id_list = parse_int_list(quiz_ids)
        question_answer_start = parse_int_list(starts)
        question_amount = parse_int_list(amounts)
    except ValueError as e:
        await ctx.send(f"❌ Lỗi định dạng tham số: {e}")
        return

    # Kiểm tra độ dài danh sách
    if not (len(quiz_id_list) == len(question_answer_start) == len(question_amount)):
        await ctx.send(
            "❌ Độ dài các danh sách không khớp. Cần đảm bảo quiz_ids, starts và amounts có cùng số phần tử."
        )
        return

    # Gọi hàm thêm dữ liệu
    try:
        msg = SEND_PACKET.ADD_QUIZ_DATA(id, quiz_id_list, question_answer_start, question_amount)
        await ctx.send(f"✅ {msg}")
    except Exception as e:
        logging.exception("Lỗi khi thêm dữ liệu quiz")
        await ctx.send(f"❌ Không thể thêm dữ liệu quiz: {e}")

@bot.command(name='show_quiz')
async def show_quiz_command(ctx, id: int):
    """
    Hiển thị danh sách quiz liên kết với ID đã cho.

    Ví dụ: !show_quiz 150
    """
    logging.info(
        f"User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh show_quiz với id: {id}."
    )
    await ctx.send(f"Đang kiểm tra dữ liệu quiz `{id}`...")

    loop = asyncio.get_running_loop()
    try:
        quiz_id_list, starts, amounts = await loop.run_in_executor(None, SEND_PACKET.QUIZ_DATA, id)
        if not quiz_id_list:
            await ctx.send("❌ Không tìm thấy dữ liệu quiz cho ID này.")
            return

        max_show = 25
        shown = min(len(quiz_id_list), max_show)
        lines = []
        for i in range(shown):
            lines.append(f"- {quiz_id_list[i]}: start={starts[i]}, amount={amounts[i]}")
        if len(quiz_id_list) > shown:
            lines.append(f"... và {len(quiz_id_list) - shown} mục nữa.")

        message = "\n".join([
            f"📋 Dữ liệu quiz cho ID {id}:",
            f"Số lượng: {len(quiz_id_list)}",
            "Chi tiết:",
            *lines
        ])
        # Tránh vượt quá giới hạn 2000 ký tự của Discord
        if len(message) > 1900:
            message = "\n".join([
                f"📋 Dữ liệu quiz cho ID {id}:",
                f"Số lượng: {len(quiz_id_list)}",
                "Chi tiết (rút gọn):",
                *lines[:20],
                "... (đã rút gọn)"
            ])
        await ctx.send(message)
    except Exception as e:
        logging.exception("Lỗi khi đọc QUIZ_DATA, chuyển sang đọc thô từ file")
        # Fallback: chỉ hiển thị danh sách quiz_ids từ file nếu có
        try:
            import json
            import os
            from dotenv import load_dotenv
            load_dotenv()
            quiz_list_path = os.getenv("QUIZ_LIST")
            if not quiz_list_path:
                await ctx.send(f"❌ Không đọc được đường dẫn QUIZ_LIST từ .env: {e}")
                return
            with open(quiz_list_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            quiz_ids_map = data.get("quiz_ids", {})
            quiz_id_list = quiz_ids_map.get(str(id), [])
            if not quiz_id_list:
                await ctx.send("❌ Không tìm thấy dữ liệu quiz cho ID này.")
                return
            max_show = 50
            shown = min(len(quiz_id_list), max_show)
            ids_str = ", ".join(map(str, quiz_id_list[:shown]))
            suffix = f"... (+{len(quiz_id_list) - shown})" if len(quiz_id_list) > shown else ""
            await ctx.send(f"📋 ID {id} có {len(quiz_id_list)} quiz: {ids_str} {suffix}".strip())
        except Exception as e2:
            await ctx.send(f"❌ Không thể đọc dữ liệu quiz: {e2}")


