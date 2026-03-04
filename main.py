import discord
from discord.ext import commands
import datetime
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# --- نظام الحماية التلقائي ---
SPAM_THRESHOLD = 5
SPAM_INTERVAL = 10
user_messages = {}

@bot.event
async def on_ready():
    print(f'Security Bot Active | Name: {bot.user.name}')

# منع السبام
@bot.event
async def on_message(message):
    if message.author.bot: return
    author_id = message.author.id
    now = datetime.datetime.now()
    if author_id not in user_messages: user_messages[author_id] = []
    user_messages[author_id].append(now)
    user_messages[author_id] = [t for t in user_messages[author_id] if (now - t).seconds < SPAM_INTERVAL]
    
    if len(user_messages[author_id]) > SPAM_THRESHOLD:
        await message.channel.purge(limit=SPAM_THRESHOLD)
        await message.author.timeout(datetime.timedelta(minutes=10), reason="Spam")
        await message.channel.send(f"⚠️ {message.author.mention} تم إسكاتك (سبام).", delete_after=5)
    await bot.process_commands(message)

# --- الأوامر المختصرة (حرف واحد) ---

@bot.command(name='l') # Lock
@commands.has_permissions(administrator=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Locked")

@bot.command(name='u') # Unlock
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Unlocked")

@bot.command(name='k') # Kick
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, r=None):
    await member.kick(reason=r)
    await ctx.send(f"✅ Kicked {member.name}")

@bot.command(name='b') # Ban
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, r=None):
    await member.ban(reason=r)
    await ctx.send(f"🚫 Banned {member.name}")

@bot.command(name='c') # Clear
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleaned {amount}", delete_after=3)

# تشغيل البوت
bot.run(os.getenv('DISCORD_TOKEN'))
