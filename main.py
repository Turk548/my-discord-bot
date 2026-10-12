import random
import disnake
from disnake.ext import commands

# تحديد الـ Intents
intents = disnake.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------------------------------
# ⚙️ إعدادات الرومات والرتب (الأرقام الخاصة بسيرفرك)
# ----------------------------------------------------
WELCOME_CHANNEL_ID = 1337378755689058335   # ID روم الترحيب
LOG_CHANNEL_ID = 1337378755689058335       # ID روم اللوقات (عدله لروم اللوقات لو عندك روم مستقل)
VOICE_CHANNEL_ID = 1337381189002072117     # 🔊 حط هنا ID الروم الصوتي اللي تبي البوت يدخل فيه

# رتب الإدارة العليا المصرح لها باستخدام الأوامر الإدارية
ALLOWED_ROLES = [
    1337388816440496181,  # رتبة أونر (Owner)
    1337392028006223914   # رتبة بوس (Boss)
]

# دالة التحقق من صلاحية العضو
def is_admin():
    async def predicate(ctx):
        if not ctx.author.guild_permissions.administrator:
            has_role = any(role.id in ALLOWED_ROLES for role in ctx.author.roles)
            if not has_role:
                await ctx.send("❌ هذا الأمر مخصص للإدارة العليا فقط (أونر / بوس)!", delete_after=5)
                return False
        return True
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"✅ تم تشغيل البوت بنجاح باسم: {bot.user}")
    await bot.change_presence(activity=disnake.Game(name="!help | خدمة السيرفر"))

    # 🔊 الاتصال بالروم الصوتي تلقائياً عند التشغيل
    if VOICE_CHANNEL_ID != 0000000000000000000:
        voice_channel = bot.get_channel(VOICE_CHANNEL_ID)
        if voice_channel:
            try:
                await voice_channel.connect()
                print(f"🔊 تم اتصال البوت بالروم الصوتي: {voice_channel.name}")
            except Exception as e:
                print(f"❌ تعذر الاتصال بالروم الصوتي: {e}")

# ----------------------------------------------------
# 1️⃣ نظام الترحيب تلقائياً (Welcome System)
# ----------------------------------------------------
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = disnake.Embed(
            title="👋 أهلاً وسهلاً بك في السيرفر!",
            description=f"حياك الله يا {member.mention}\nنورت السيرفر، نتمنى لك وقتاً ممتعاً! 🌹",
            color=disnake.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"عدد الأعضاء الحالي: {member.guild.member_count}")
        await channel.send(embed=embed)

# ----------------------------------------------------
# 2️⃣ نظام اللوقات الشامل (Logs System)
# ----------------------------------------------------

# لوق حذف الرسائل
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(
            title="🗑️ تم حذف رسالة",
            color=disnake.Color.red()
        )
        embed.add_field(name="الكاتب:", value=message.author.mention, inline=True)
        embed.add_field(name="الروم:", value=message.channel.mention, inline=True)
        embed.add_field(name="محتوى الرسالة:", value=message.content or "محتوى غير نصي/صورة", inline=False)
        await log_channel.send(embed=embed)

# لوق تعديل الرسائل
@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(
            title="✏️ تم تعديل رسالة",
            color=disnake.Color.orange()
        )
        embed.add_field(name="الكاتب:", value=before.author.mention, inline=True)
        embed.add_field(name="الروم:", value=before.channel.mention, inline=True)
        embed.add_field(name="قبل التعديل:", value=before.content, inline=False)
        embed.add_field(name="بعد التعديل:", value=after.content, inline=False)
        await log_channel.send(embed=embed)

# لوق خروج الأعضاء
@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(
            title="🚪 غادر عضو السيرفر",
            description=f"العضو {member.mention} ({member.name}) غادر السيرفر.",
            color=disnake.Color.dark_gray()
        )
        await log_channel.send(embed=embed)

# ----------------------------------------------------
# 3️⃣ الأوامر الإدارية (محصورة على أونر وبوس فقط)
# ----------------------------------------------------

# أمر مسح الشات
@bot.command()
@is_admin()
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 تم مسح `{amount}` رسالة بنجاح!", delete_after=3)

# أمر الطرد (Kick)
@bot.command()
@is_admin()
async def kick(ctx, member: disnake.Member, *, reason="لا يوجد سبب"):
    await member.kick(reason=reason)
    await ctx.send(f"✅ تم طرد {member.mention} | السبب: {reason}")

# أمر الحظر (Ban)
@bot.command()
@is_admin()
async def ban(ctx, member: disnake.Member, *, reason="لا يوجد سبب"):
    await member.ban(reason=reason)
    await ctx.send(f"⛔ تم حظر {member.mention} | السبب: {reason}")

# ----------------------------------------------------
# 4️⃣ ألعاب وتسلية (متاحة لجميع المواطنين والأعضاء)
# ----------------------------------------------------

# لعبة رمي النرد
@bot.command()
async def dice(ctx):
    result = random.randint(1, 6)
    await ctx.send(f"🎲 طلع لك الرقم: **{result}**")

# لعبة حجر ورقة مقص
@bot.command()
async def rps(ctx, choice: str):
    options = ["حجر", "ورقة", "مقص"]
    bot_choice = random.choice(options)
    
    if choice not in options:
        await ctx.send("يرجى اختيار: `حجر` أو `ورقة` أو `مقص` (مثال: `!rps حجر`)")
        return

    if choice == bot_choice:
        res = "تعادل! 🤝"
    elif (choice == "حجر" and bot_choice == "مقص") or \
         (choice == "ورقة" and bot_choice == "حجر") or \
         (choice == "مقص" and bot_choice == "ورقة"):
        res = "فزت عليّ! 🎉"
    else:
        res = "أنا فزت عليك! 😎"

    await ctx.send(f"اخترت أنت: **{choice}** | اخترت أنا: **{bot_choice}**\n**النتيجة:** {res}")

# ضع التوكن الجديد الخاص ببوتك هنا بين القوسين
bot.run("MTU1OTA0NzEzNjQ1MTEwMDcyNA.GxSu92.hKqzySbovZ-f79An6LmaWgUfer5EtzDZDxbL40")