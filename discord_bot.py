

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from send_packet import SEND_PACKET, CRAWL_DATA
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
    
    # Gửi embed đang kiểm tra
    embed = discord.Embed(
        title="🏓 Ping Server",
        description="Đang kiểm tra kết nối tới LMS server...",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
    status_msg = await ctx.send(embed=embed)
    
    loop = asyncio.get_running_loop()
    
    try:
        result = await loop.run_in_executor(None, SEND_PACKET.PING)
        
        # Xác định màu sắc dựa trên status
        if result["status"] == "online":
            color = discord.Color.green()
            icon = "✅"
        elif result["status"] == "warning":
            color = discord.Color.orange()
            icon = "⚠️"
        else:
            color = discord.Color.red()
            icon = "❌"
        
        # Tạo embed kết quả
        result_embed = discord.Embed(
            title=f"{icon} Server Status",
            description=result["message"],
            color=color
        )
        result_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        result_embed.add_field(name="📡 Status Code", value=f"`{result['status_code']}`", inline=True)
        result_embed.add_field(name="⏱️ Response Time", value=f"`{result['response_time']}ms`", inline=True)
        result_embed.add_field(name="🌐 Status", value=f"`{result['status'].upper()}`", inline=False)
        
        # Thêm bot latency
        bot_latency = round(ctx.bot.latency * 1000, 2)
        result_embed.add_field(name="🤖 Discord Bot Latency", value=f"`{bot_latency}ms`", inline=True)
        
        await status_msg.edit(embed=result_embed)
        
        logging.info(f"Ping result: {result['status']} - {result['response_time']}ms")
        
    except Exception as e:
        logging.error(f"Lỗi khi ping server: {e}")
        error_embed = discord.Embed(
            title="❌ Lỗi Ping",
            description=f"Không thể kiểm tra kết nối: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        await status_msg.edit(embed=error_embed)
        raise

@bot.command(name='slide')
async def slide_command(ctx, session_id: str, slide_id: int):
    # Tạo request ID để theo dõi
    import time
    request_id = f"{ctx.author.id}-{int(time.time())}"
    
    logging.info(f"[{request_id}] User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh slide với session_id: {session_id[:8]}... và slide_id: {slide_id}.")
    
    # Gửi embed thông tin bắt đầu
    embed = discord.Embed(
        title="🎯 Xử lý Slide",
        description=f"Đang xử lý slide `{slide_id}`...",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
    embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
    embed.add_field(name="📄 Slide ID", value=f"`{slide_id}`", inline=True)
    embed.set_footer(text=f"Session: {session_id[:8]}...")
    status_msg = await ctx.send(embed=embed)
    
    loop = asyncio.get_running_loop()
    
    try:
        result = await loop.run_in_executor(
            None, SEND_PACKET.SLIDE, session_id, slide_id)
        
        logging.info(f"[{request_id}] Response: {result[1]}")
        
        # Tạo embed kết quả
        result_embed = discord.Embed(
            title="✅ Hoàn thành" if "hoàn thành" in result[2].lower() else "⚠️ Kết quả",
            description=result[2],
            color=discord.Color.green() if "hoàn thành" in result[2].lower() else discord.Color.orange()
        )
        result_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        result_embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        result_embed.add_field(name="📄 Slide ID", value=f"`{slide_id}`", inline=True)
        result_embed.add_field(name="📊 Status", value=result[0], inline=False)
        result_embed.set_footer(text=f"Session: {session_id[:8]}...")
        
        await status_msg.edit(embed=result_embed)
    except Exception as e:
        logging.error(f"[{request_id}] Lỗi: {e}")
        error_embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã có lỗi xảy ra: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        error_embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        await status_msg.edit(embed=error_embed)
        raise

@bot.command(name='quiz')
async def quiz_command(ctx, session_id: str, quiz_id: int):
    # Tạo request ID để theo dõi
    import time
    request_id = f"{ctx.author.id}-{int(time.time())}"
    
    logging.info(f"[{request_id}] User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh quiz với session_id: {session_id[:8]}... và quiz_id: {quiz_id}.")
    
    # Kiểm tra xem có dữ liệu quiz không
    try:
        quiz_ids, starts, amounts = SEND_PACKET.QUIZ_DATA(quiz_id)
        num_questions = len(quiz_ids)
    except Exception as e:
        num_questions = "?"
        logging.warning(f"[{request_id}] Không thể đọc QUIZ_DATA: {e}")
    
    # Gửi embed thông tin bắt đầu
    embed = discord.Embed(
        title="📝 Xử lý Quiz",
        description=f"Đang tìm đáp án cho quiz `{quiz_id}`...\nViệc này có thể mất vài phút.",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
    embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
    embed.add_field(name="📝 Quiz ID", value=f"`{quiz_id}`", inline=True)
    embed.add_field(name="❓ Số câu hỏi", value=f"`{num_questions}`", inline=True)
    embed.set_footer(text=f"Session: {session_id[:8]}... | Đang xử lý...")
    status_msg = await ctx.send(embed=embed)
    
    loop = asyncio.get_running_loop()
    
    try:
        result = await loop.run_in_executor(
            None, SEND_PACKET.QUIZ, session_id, quiz_id)
        
        logging.info(f"[{request_id}] Quiz result: {result}")
        
        # Tạo embed kết quả
        if "Đã hoàn thành" in result:
            result_embed = discord.Embed(
                title="✅ Quiz hoàn thành",
                description=result,
                color=discord.Color.green()
            )
        elif "Có lỗi" in result:
            result_embed = discord.Embed(
                title="⚠️ Quiz có lỗi",
                description=result,
                color=discord.Color.orange()
            )
        elif "không có quyền" in result.lower():
            result_embed = discord.Embed(
                title="🔒 Không có quyền truy cập",
                description=result,
                color=discord.Color.red()
            )
        else:
            result_embed = discord.Embed(
                title="📋 Kết quả Quiz",
                description=result,
                color=discord.Color.blue()
            )
        
        result_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        result_embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        result_embed.add_field(name="📝 Quiz ID", value=f"`{quiz_id}`", inline=True)
        if num_questions != "?":
            result_embed.add_field(name="❓ Số câu hỏi", value=f"`{num_questions}`", inline=True)
        result_embed.set_footer(text=f"Session: {session_id[:8]}...")
        
        await status_msg.edit(embed=result_embed)
    except Exception as e:
        logging.error(f"[{request_id}] Lỗi quiz: {e}")
        error_embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã có lỗi xảy ra khi xử lý quiz: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        error_embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        error_embed.add_field(name="📝 Quiz ID", value=f"`{quiz_id}`", inline=True)
        await status_msg.edit(embed=error_embed)
        raise

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

@bot.command(name='all')
async def all_courses_command(ctx, session_id: str):
    """
    Chạy tự động tất cả slides và quizzes cho tất cả khóa học.

    Ví dụ: !all 2c126a931825e2695b5b6f088677d571877d5bb4
    """
    import time
    request_id = f"{ctx.author.id}-{int(time.time())}"
    
    logging.info(f"[{request_id}] User {ctx.author.name}#{ctx.author.discriminator} đã gửi lệnh all với session_id: {session_id[:8]}...")
    
    # Gửi embed thông tin bắt đầu
    embed = discord.Embed(
        title="🚀 Chạy tự động tất cả khóa học",
        description="Đang lấy danh sách khóa học từ dashboard...",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
    embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
    embed.set_footer(text=f"Session: {session_id[:8]}... | Đang xử lý...")
    status_msg = await ctx.send(embed=embed)
    
    loop = asyncio.get_running_loop()
    
    try:
        # Lấy danh sách khóa học
        courses = await loop.run_in_executor(None, CRAWL_DATA.list_courses, session_id)
        
        if not courses:
            await status_msg.edit(embed=discord.Embed(
                title="❌ Không tìm thấy khóa học",
                description="Không có khóa học nào để xử lý",
                color=discord.Color.red()
            ))
            return
        
        course_ids = list(courses.keys())
        
        # Cập nhật embed với danh sách khóa học
        embed = discord.Embed(
            title="🚀 Chạy tự động tất cả khóa học",
            description=f"Tìm thấy {len(course_ids)} khóa học. Bắt đầu xử lý...",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        embed.add_field(name="📚 Số khóa học", value=f"`{len(course_ids)}`", inline=True)
        embed.add_field(name="Khóa học:", value=", ".join(map(str, course_ids[:5])) + ("..." if len(course_ids) > 5 else ""), inline=False)
        await status_msg.edit(embed=embed)
        
        # Chạy tất cả khóa học
        results = []
        for i, course_id in enumerate(course_ids, 1):
            try:
                logging.info(f"[{request_id}] Xử lý khóa học {i}/{len(course_ids)}: {course_id}")
                
                result = await loop.run_in_executor(
                    None, 
                    CRAWL_DATA.run_course_auto, 
                    session_id, 
                    course_id,
                    True,  # process_slides
                    True,  # process_quizzes
                    False  # verbose (không in log)
                )
                
                results.append(result)
                
                # Cập nhật progress
                progress_emoji = "✅" if result.get("status") == "success" else "❌"
                
                # Tạo progress bar
                progress = i / len(course_ids)
                bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
                
                embed = discord.Embed(
                    title="🚀 Chạy tự động tất cả khóa học",
                    description=f"Đang xử lý... [{bar}] {i}/{len(course_ids)}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
                embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
                embed.add_field(
                    name="📊 Tiến độ",
                    value=f"{progress_emoji} Course {course_id}: {result.get('slides_processed', 0)} slides + {result.get('quizzes_processed', 0)} quizzes",
                    inline=False
                )
                embed.set_footer(text=f"Session: {session_id[:8]}... | Đang xử lý...")
                
                await status_msg.edit(embed=embed)
                
            except Exception as e:
                logging.error(f"[{request_id}] Lỗi xử lý khóa học {course_id}: {e}")
                results.append({
                    "status": "error",
                    "course_id": course_id,
                    "message": str(e)
                })
        
        # Tóm tắt kết quả
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = sum(1 for r in results if r.get("status") == "error")
        total_slides = sum(r.get("slides_processed", 0) for r in results if r.get("status") == "success")
        total_quizzes = sum(r.get("quizzes_processed", 0) for r in results if r.get("status") == "success")
        
        embed = discord.Embed(
            title="✅ Hoàn thành!",
            description=f"Đã xử lý {success_count}/{len(course_ids)} khóa học",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        embed.add_field(name="📚 Khóa học thành công", value=f"`{success_count}`", inline=True)
        embed.add_field(name="❌ Khóa học lỗi", value=f"`{error_count}`", inline=True)
        embed.add_field(name="📖 Tổng slides", value=f"`{total_slides}`", inline=True)
        embed.add_field(name="❓ Tổng quizzes", value=f"`{total_quizzes}`", inline=True)
        
        # Liệt kê lỗi nếu có
        if error_count > 0:
            error_details = []
            for r in results:
                if r.get("status") == "error":
                    error_details.append(f"• Course {r.get('course_id')}: {r.get('message', 'Unknown error')[:50]}")
            if error_details:
                embed.add_field(
                    name="⚠️ Chi tiết lỗi",
                    value="\n".join(error_details[:5]) + ("\n..." if len(error_details) > 5 else ""),
                    inline=False
                )
        
        embed.set_footer(text=f"Session: {session_id[:8]}...")
        
        await status_msg.edit(embed=embed)
        
        logging.info(f"[{request_id}] Hoàn thành: {success_count}/{len(course_ids)} thành công, {error_count} lỗi")
        
    except Exception as e:
        logging.error(f"[{request_id}] Lỗi: {e}")
        error_embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã có lỗi xảy ra: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.add_field(name="👤 Người yêu cầu", value=ctx.author.mention, inline=True)
        error_embed.add_field(name="🔑 Request ID", value=f"`{request_id[:16]}`", inline=True)
        await status_msg.edit(embed=error_embed)

if __name__ == "__main__":
    if not TOKEN:
        logging.error("❌ Không tìm thấy BOT_TOKEN trong file .env")
        print("❌ Vui lòng thêm BOT_TOKEN vào file .env")
    else:
        try:
            logging.info("🚀 Đang khởi động bot...")
            bot.run(TOKEN)
        except Exception as e:
            logging.error(f"❌ Lỗi khi khởi động bot: {e}")
            print(f"❌ Lỗi: {e}")

