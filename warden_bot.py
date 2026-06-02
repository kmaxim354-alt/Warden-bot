import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta
import asyncio
import random
import string
import aiohttp
import pytz
from datetime import time

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# ========== TECH WORK SYSTEM ==========
tech_work_active = False
ALLOWED_TECH_USERS = [1436760469980450816]

def is_tech_work_time():
    msk = pytz.timezone('Europe/Moscow')
    now = datetime.now(msk).time()
    return now >= time(23, 0) or now <= time(9, 0)

async def tech_work_checker():
    global tech_work_active
    while True:
        tech_work_active = is_tech_work_time()
        await asyncio.sleep(60)

async def check_tech_work(i):
    if tech_work_active:
        embed = discord.Embed(title='🛠️ Maintenance', description='Bot is temporarily unavailable. Please come back later.', color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)
        return True
    return False

# ========== FILES ==========
SETTINGS_FILE = 'warden_settings.json'
LOGS_SETTINGS_FILE = 'logs_settings.json'
CAPTCHA_SETTINGS_FILE = 'captcha_settings.json'
WELCOME_SETTINGS_FILE = 'welcome_settings.json'
WARNS_FILE = 'warns.json'
TICKETS_FILE = 'tickets.json'
TICKET_SETTINGS_FILE = 'ticket_settings.json'
REACTION_ROLES_FILE = 'reaction_roles.json'

def load(f): return json.load(open(f, 'r', encoding='utf-8')) if os.path.exists(f) else {}
def save(f, d): json.dump(d, open(f, 'w', encoding='utf-8'), indent=4, ensure_ascii=False)

async def send_log(guild_id, embed):
    cid = load(LOGS_SETTINGS_FILE).get(str(guild_id))
    if cid and (c := bot.get_channel(cid)): await c.send(embed=embed)

active_captchas = {}
def gen_captcha(): return ''.join(random.choices(string.digits, k=6))

async def update_status():
    idx, ver = 0, "v1.0.0"
    while True:
        try:
            if tech_work_active:
                # Только Tech work, не меняется
                await bot.change_presence(activity=discord.Game(name="🛠️ Tech work"))
            else:
                # Обычный циклический статус
                srv = len(bot.guilds)
                if idx == 0:
                    t = f"{ver} | {srv} server" if srv == 1 else f"{ver} | {srv} servers"
                elif idx == 1:
                    t = f"{ver} | {sum(g.member_count for g in bot.guilds)} users"
                else:
                    t = f"{ver} | /help"
                await bot.change_presence(activity=discord.Game(name=t))
                idx = (idx + 1) % 3
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(10)

# ========== TECH WORK COMMAND ==========
@bot.tree.command(name='tech_work', description='Manage maintenance mode')
async def tech_work_cmd(i: discord.Interaction, action: str):
    if i.user.id not in ALLOWED_TECH_USERS:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    global tech_work_active
    if action.lower() == 'on':
        tech_work_active = True
        await i.response.send_message('🛠️ Maintenance mode ENABLED', ephemeral=True)
    elif action.lower() == 'off':
        tech_work_active = False
        await i.response.send_message('✅ Maintenance mode DISABLED', ephemeral=True)
    elif action.lower() == 'status':
        status = "ENABLED" if tech_work_active else "DISABLED"
        await i.response.send_message(f'🛠️ Maintenance status: **{status}**', ephemeral=True)
    else:
        await i.response.send_message('❌ Use: `on`, `off`, `status`', ephemeral=True)

# ========== BASIC COMMANDS ==========
@bot.tree.command(name='hello', description='Greet Warden bot')
async def hello(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(f'Hello, {i.user.mention}! I am **Warden Bot** 🤖')

@bot.tree.command(name='ping', description='Check bot latency')
async def ping(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(f'🏓 Pong! {round(bot.latency*1000)}ms')

@bot.tree.command(name='info', description='Bot information')
async def info(i: discord.Interaction):
    if await check_tech_work(i): return
    e = discord.Embed(title='🛡️ Warden Bot', description='The guardian bot for your server', color=discord.Color.blue())
    e.add_field(name='Version', value='v1.0.0', inline=True)
    e.add_field(name='Commands', value='Use `/help` to see all commands', inline=False)
    e.set_footer(text='Always keeping order 🔒')
    await i.response.send_message(embed=e)

@bot.tree.command(name='help', description='All commands')
async def help_cmd(i: discord.Interaction):
    if await check_tech_work(i): return
    e = discord.Embed(title='🛡️ Warden Bot Commands', color=discord.Color.blue())
    e.add_field(name='📋 Basic', value='`/hello` `/ping` `/info` `/help`')
    e.add_field(name='🛡️ Moderation', value='`/mute` `/unmute` `/ban` `/unban` `/kick` `/clear` `/warn` `/warnings` `/topwarnings` `/delwarn` `/slowmode` `/lock` `/unlock` `/report` `/pin` `/unpin`')
    e.add_field(name='⚔️ Moderation 2', value='`/vkick` `/timeout` `/untimeout` `/softban` `/massban` `/clean` `/strike` `/unstrike` `/strikes` `/topstrikes` `/setnick` `/setupantinuke`')
    e.add_field(name='👮 Roles & Channels', value='`/addrole` `/removerole` `/createrole` `/deleterole` `/reactionrole` `/createchannel` `/deletechannel` `/clonechannel` `/movechannel`')
    e.add_field(name='🎤 Voice', value='`/vmute` `/vunmute` `/vdeafen` `/vundeafen` `/vmove`')
    e.add_field(name='📋 Info', value='`/serverinfo` `/userinfo` `/avatar` `/membercount` `/admins` `/bots`')
    e.add_field(name='⭐ Leveling', value='`/promotion` `/setuppromotion` `/leaderboard` `/addxp` `/setxp` `/setlevel`')
    e.add_field(name='🛠️ Utility', value='`/calc` `/poll` `/afk` `/unafk` `/remindme` `/timestamp` `/color` `/qr-code` `/uptime` `/giveaway`')
    e.add_field(name='🎉 Fun', value='`/cat` `/roll` `/8ball` `/joke` `/fact` `/advice` `/quote` `/trivia` `/rps` `/flip`')
    e.add_field(name='⚙️ Setup', value='`/setup-logs` `/setup-welcome` `/setup-photowelcome` `/disable-welcome` `/setup-captcha` `/disable-captcha` `/setup-application` `/create-apps` `/setup-ticket`')
    e.add_field(name='🔗 Misc', value='`/invite` `/tech_work`')
    await i.response.send_message(embed=e)

# ========== MODERATION COMMANDS ==========
@bot.tree.command(name='mute', description='Mute a member')
async def mute(i: discord.Interaction, member: discord.Member, time: str, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    dmap = {'s':1,'m':60,'h':3600,'d':86400}
    if time[-1] not in dmap:
        return await i.response.send_message('❌ Use: 10s, 5m, 1h, 1d', ephemeral=True)
    try:
        sec = int(time[:-1]) * dmap[time[-1]]
        await member.timeout(datetime.now() + timedelta(seconds=sec), reason=reason)
        await i.response.send_message(f'🔇 {member.mention} muted for {time}', ephemeral=True)
    except:
        await i.response.send_message('❌ Invalid format!', ephemeral=True)

@bot.tree.command(name='unmute', description='Unmute a member')
async def unmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.timed_out_until is None:
        return await i.response.send_message('❌ Not muted!', ephemeral=True)
    await member.timeout(None)
    await i.response.send_message(f'✅ {member.mention} unmuted', ephemeral=True)

@bot.tree.command(name='ban', description='Ban a member')
async def ban(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.ban(reason=reason)
    await i.response.send_message(f'✅ {member.mention} banned', ephemeral=True)

@bot.tree.command(name='unban', description='Unban by ID')
async def unban(i: discord.Interaction, user_id: str, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    banned = [e async for e in i.guild.banned_users()]
    target = next((e.user for e in banned if str(e.user.id) == user_id), None)
    if not target:
        return await i.response.send_message(f'❌ User {user_id} not found!', ephemeral=True)
    await i.guild.unban(target, reason=reason)
    await i.response.send_message(f'✅ Unbanned {target.name}', ephemeral=True)

@bot.tree.command(name='kick', description='Kick a member')
async def kick(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.kick(reason=reason)
    await i.response.send_message(f'✅ {member.mention} kicked', ephemeral=True)

@bot.tree.command(name='clear', description='Clear messages')
async def clear(i: discord.Interaction, amount: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if amount < 1 or amount > 100:
        return await i.response.send_message('❌ 1-100 only!', ephemeral=True)
    deleted = await i.channel.purge(limit=amount)
    await i.response.send_message(f'✅ Deleted {len(deleted)} messages', ephemeral=True)

@bot.tree.command(name='warn', description='Warn a member')
async def warn(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(member.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    wid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': wid, 'reason': reason, 'mod': i.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)
    await i.response.send_message(f'⚠️ {member.mention} warned #{wid}', ephemeral=True)

@bot.tree.command(name='warnings', description='Show warnings')
async def warnings(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(member.id), [])
    if not w:
        return await i.response.send_message(f'{member.mention} has no warnings.', ephemeral=True)
    e = discord.Embed(title=f'⚠️ Warnings for {member.name}', description=f'Total: {len(w)}', color=0xe67e22)
    for ww in w[-5:]:
        mod = i.guild.get_member(ww['mod'])
        e.add_field(name=f"Warning #{ww['id']}", value=f"Reason: {ww['reason']}\nMod: {mod.name if mod else 'Unknown'}", inline=False)
    await i.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name='topwarnings', description='Top warnings')
async def topwarnings(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {})
    if not w:
        return await i.response.send_message('No warnings!', ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := i.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Top warnings', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} warnings', inline=False)
    await i.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name='delwarn', description='Remove warning')
async def delwarn(i: discord.Interaction, member: discord.Member, warn_id: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(member.id)
    if gid not in w or uid not in w[gid]:
        return await i.response.send_message(f'{member.mention} has no warnings!', ephemeral=True)
    for idx, ww in enumerate(w[gid][uid]):
        if ww['id'] == warn_id:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)
            return await i.response.send_message(f'✅ Warning #{warn_id} removed!', ephemeral=True)
    await i.response.send_message(f'❌ Warning #{warn_id} not found!', ephemeral=True)

@bot.tree.command(name='slowmode', description='Set slowmode')
async def slowmode(i: discord.Interaction, channel: discord.TextChannel, seconds: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await channel.edit(slowmode_delay=seconds)
    await i.response.send_message(f'✅ Slowmode {seconds}s in {channel.mention}', ephemeral=True)

@bot.tree.command(name='lock', description='Lock channel')
async def lock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=False)
    await i.response.send_message(f'🔒 {channel.mention} locked', ephemeral=True)

@bot.tree.command(name='unlock', description='Unlock channel')
async def unlock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=None)
    await i.response.send_message(f'🔓 {channel.mention} unlocked', ephemeral=True)

@bot.tree.command(name='report', description='Report user')
async def report(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_tech_work(i): return
    e = discord.Embed(title='📢 Report', description=f'{i.user.mention} reported {user.mention}', color=discord.Color.red())
    e.add_field(name='Reason', value=reason)
    await send_log(i.guild_id, e)
    await i.response.send_message('✅ Report sent', ephemeral=True)

@bot.tree.command(name='pin', description='Pin message')
async def pin(i: discord.Interaction, message_id: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.pin()
        await i.response.send_message('📌 Pinned', ephemeral=True)
    except:
        await i.response.send_message('❌ Message not found', ephemeral=True)

@bot.tree.command(name='unpin', description='Unpin message')
async def unpin(i: discord.Interaction, message_id: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.unpin()
        await i.response.send_message('📌 Unpinned', ephemeral=True)
    except:
        await i.response.send_message('❌ Message not found', ephemeral=True)

# ========== VOICE COMMANDS ==========
@bot.tree.command(name='vmute', description='Mute in voice')
async def vmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.edit(mute=True)
        await i.response.send_message(f'🔇 Muted {member.mention} in voice', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

@bot.tree.command(name='vunmute', description='Unmute in voice')
async def vunmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.edit(mute=False)
        await i.response.send_message(f'🔊 Unmuted {member.mention} in voice', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

@bot.tree.command(name='vdeafen', description='Deafen in voice')
async def vdeafen(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.edit(deafen=True)
        await i.response.send_message(f'🔇 Deafened {member.mention}', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

@bot.tree.command(name='vundeafen', description='Undeafen in voice')
async def vundeafen(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.edit(deafen=False)
        await i.response.send_message(f'🔊 Undeafened {member.mention}', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

@bot.tree.command(name='vkick', description='Kick from voice')
async def vkick(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.move_to(None)
        await i.response.send_message(f'🎤 {member.mention} kicked from voice', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

@bot.tree.command(name='vmove', description='Move in voice')
async def vmove(i: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    if member.voice:
        await member.move_to(channel)
        await i.response.send_message(f'✅ Moved {member.mention} to {channel.name}', ephemeral=True)
    else:
        await i.response.send_message('❌ Not in voice', ephemeral=True)

# ========== INFO COMMANDS ==========
@bot.tree.command(name='serverinfo', description='Server info')
async def serverinfo(i: discord.Interaction):
    if await check_tech_work(i): return
    g = i.guild
    e = discord.Embed(title=f'📊 {g.name}', color=0x3498db)
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name='Owner', value=g.owner.mention if g.owner else 'Unknown')
    e.add_field(name='Members', value=g.member_count)
    e.add_field(name='Channels', value=len(g.channels))
    e.add_field(name='Roles', value=len(g.roles))
    await i.response.send_message(embed=e)

@bot.tree.command(name='userinfo', description='User info')
async def userinfo(i: discord.Interaction, member: discord.Member = None):
    if await check_tech_work(i): return
    m = member or i.user
    e = discord.Embed(title=f'👤 {m.name}', color=m.color if m.color else 0x3498db)
    if m.avatar: e.set_thumbnail(url=m.avatar.url)
    e.add_field(name='ID', value=m.id)
    e.add_field(name='Joined', value=m.joined_at.strftime('%d.%m.%Y') if m.joined_at else 'Unknown')
    e.add_field(name='Created', value=m.created_at.strftime('%d.%m.%Y'))
    e.add_field(name='Bot', value='Yes' if m.bot else 'No')
    await i.response.send_message(embed=e)

@bot.tree.command(name='avatar', description='Show avatar')
async def avatar(i: discord.Interaction, member: discord.Member = None):
    if await check_tech_work(i): return
    m = member or i.user
    e = discord.Embed(title=f"{m.name}'s avatar", color=0x3498db)
    e.set_image(url=m.display_avatar.url)
    await i.response.send_message(embed=e)

@bot.tree.command(name='membercount', description='Member count')
async def membercount(i: discord.Interaction):
    if await check_tech_work(i): return
    total = i.guild.member_count
    humans = sum(1 for m in i.guild.members if not m.bot)
    bots = total - humans
    e = discord.Embed(title='📊 Member Count', color=0x3498db)
    e.add_field(name='Total', value=total)
    e.add_field(name='Humans', value=humans)
    e.add_field(name='Bots', value=bots)
    await i.response.send_message(embed=e)

@bot.tree.command(name='admins', description='Server admins')
async def admins(i: discord.Interaction):
    if await check_tech_work(i): return
    admins_list = [m.mention for m in i.guild.members if m.guild_permissions.administrator]
    await i.response.send_message(' '.join(admins_list) or 'None', ephemeral=True)

@bot.tree.command(name='bots', description='Bots on server')
async def bots(i: discord.Interaction):
    if await check_tech_work(i): return
    bots_list = [m.mention for m in i.guild.members if m.bot]
    await i.response.send_message(' '.join(bots_list) or 'None', ephemeral=True)

# ========== MODERATION 2 COMMANDS ==========
@bot.tree.command(name='timeout', description='Timeout member')
async def timeout(i: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.timeout(datetime.now() + timedelta(minutes=minutes), reason=reason)
    await i.response.send_message(f'⏰ {member.mention} timed out for {minutes}min', ephemeral=True)

@bot.tree.command(name='untimeout', description='Remove timeout')
async def untimeout(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.timeout(None)
    await i.response.send_message(f'✅ {member.mention} timeout removed', ephemeral=True)

@bot.tree.command(name='softban', description='Softban')
async def softban(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.ban(reason=reason)
    await i.guild.unban(member, reason="Softban")
    await i.response.send_message(f'✅ {member.mention} softbanned', ephemeral=True)

@bot.tree.command(name='massban', description='Mass ban')
async def massban(i: discord.Interaction, ids: str, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    ids_list = ids.split()
    count = 0
    for uid in ids_list:
        try:
            user = await bot.fetch_user(int(uid))
            await i.guild.ban(user, reason=reason)
            count += 1
        except:
            pass
    await i.response.send_message(f'✅ Banned {count} users', ephemeral=True)

@bot.tree.command(name='clean', description='Clean bot messages')
async def clean(i: discord.Interaction, amount: int = 10):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    deleted = 0
    async for msg in i.channel.history(limit=amount):
        if msg.author == bot.user:
            await msg.delete()
            deleted += 1
    await i.response.send_message(f'✅ Deleted {deleted} bot messages', ephemeral=True)

@bot.tree.command(name='strike', description='Give strike')
async def strike(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(user.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    sid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': sid, 'reason': reason, 'mod': i.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)
    await i.response.send_message(f'⚠️ {user.mention} strike #{sid}', ephemeral=True)

@bot.tree.command(name='unstrike', description='Remove strike')
async def unstrike(i: discord.Interaction, user: discord.Member, sid: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(user.id)
    if gid not in w or uid not in w[gid]:
        return await i.response.send_message(f'❌ {user.mention} has no strikes', ephemeral=True)
    for idx, s in enumerate(w[gid][uid]):
        if s['id'] == sid:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)
            return await i.response.send_message(f'✅ Strike #{sid} removed', ephemeral=True)
    await i.response.send_message(f'❌ Strike #{sid} not found', ephemeral=True)

@bot.tree.command(name='strikes', description='Show strikes')
async def strikes(i: discord.Interaction, user: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(user.id), [])
    if not w:
        return await i.response.send_message(f'✅ {user.mention} has no strikes', ephemeral=True)
    e = discord.Embed(title=f'⚠️ Strikes for {user.name}', description=f'Total: {len(w)}', color=0xe67e22)
    for s in w[-5:]:
        mod = i.guild.get_member(s['mod'])
        e.add_field(name=f"Strike #{s['id']}", value=f"Reason: {s['reason']}\nMod: {mod.name if mod else 'Unknown'}", inline=False)
    await i.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name='topstrikes', description='Top strikes')
async def topstrikes(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {})
    if not w: return await i.response.send_message('No strikes', ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := i.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Top strikes', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} strikes', inline=False)
    await i.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name='setnick', description='Set nickname')
async def setnick(i: discord.Interaction, member: discord.Member, nick: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_nicknames:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.edit(nick=nick)
    await i.response.send_message(f'✅ Nickname set for {member.mention}', ephemeral=True)

@bot.tree.command(name='setupantinuke', description='Setup antinuke')
async def setupantinuke(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    await i.response.send_message('✅ Antinuke configured!', ephemeral=True)

# ========== ROLES & CHANNELS COMMANDS ==========
@bot.tree.command(name='addrole', description='Add role')
async def addrole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.add_roles(role)
    await i.response.send_message(f'✅ Added {role.mention} to {member.mention}', ephemeral=True)

@bot.tree.command(name='removerole', description='Remove role')
async def removerole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await member.remove_roles(role)
    await i.response.send_message(f'✅ Removed {role.mention} from {member.mention}', ephemeral=True)

@bot.tree.command(name='createrole', description='Create role')
async def createrole(i: discord.Interaction, name: str, color: str = "default"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    cols = {'red':0xff0000, 'green':0x00ff00, 'blue':0x0000ff, 'yellow':0xffff00, 'purple':0xff00ff, 'default':0x99aab5}
    r = await i.guild.create_role(name=name, color=cols.get(color, 0x99aab5))
    await i.response.send_message(f'✅ Role {r.mention} created', ephemeral=True)

@bot.tree.command(name='deleterole', description='Delete role')
async def deleterole(i: discord.Interaction, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await role.delete()
    await i.response.send_message('✅ Role deleted', ephemeral=True)

@bot.tree.command(name='reactionrole', description='Reaction role')
async def reactionrole(i: discord.Interaction, msg_id: str, role: discord.Role, emoji: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(msg_id))
        await msg.add_reaction(emoji)
        rr = load(REACTION_ROLES_FILE)
        rr[f"{i.guild_id}_{msg_id}_{emoji}"] = role.id
        save(REACTION_ROLES_FILE, rr)
        await i.response.send_message(f'✅ Reaction {emoji} → {role.mention}', ephemeral=True)
    except:
        await i.response.send_message('❌ Error', ephemeral=True)

@bot.tree.command(name='createchannel', description='Create channel')
async def createchannel(i: discord.Interaction, name: str, category: discord.CategoryChannel = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await i.guild.create_text_channel(name, category=category)
    await i.response.send_message(f'✅ Channel #{name} created', ephemeral=True)

@bot.tree.command(name='deletechannel', description='Delete channel')
async def deletechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await ch.delete()
    await i.response.send_message('✅ Channel deleted', ephemeral=True)

@bot.tree.command(name='clonechannel', description='Clone channel')
async def clonechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await ch.clone()
    await i.response.send_message(f'✅ Cloned #{ch.name}', ephemeral=True)

@bot.tree.command(name='movechannel', description='Move channel')
async def movechannel(i: discord.Interaction, ch: discord.TextChannel, pos: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    await ch.edit(position=pos)
    await i.response.send_message(f'✅ Moved #{ch.name} to {pos}', ephemeral=True)

# ========== LEVELING COMMANDS ==========
level_data = {}
@bot.tree.command(name='promotion', description='Your level')
async def promotion(i: discord.Interaction):
    if await check_tech_work(i): return
    uid = str(i.user.id)
    lvl = level_data.get(uid, {}).get('level', 0)
    xp = level_data.get(uid, {}).get('xp', 0)
    await i.response.send_message(f'📊 Your level: {lvl} | XP: {xp}', ephemeral=True)

@bot.tree.command(name='setuppromotion', description='Setup leveling')
async def setuppromotion(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    await i.response.send_message('✅ Leveling system configured!', ephemeral=True)

@bot.tree.command(name='leaderboard', description='Level leaderboard')
async def leaderboard(i: discord.Interaction):
    if await check_tech_work(i): return
    sorted_users = sorted(level_data.items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:10]
    text = ''
    for idx, (uid, data) in enumerate(sorted_users, 1):
        m = i.guild.get_member(int(uid))
        if m:
            text += f'{idx}. {m.name} - Level {data.get("level", 0)} ({data.get("xp", 0)} XP)\n'
    if not text: text = 'No data yet'
    await i.response.send_message(f'🏆 **Leaderboard**\n{text}', ephemeral=True)

@bot.tree.command(name='addxp', description='Add XP')
async def addxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    uid = str(member.id)
    if uid not in level_data: level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] += xp
    await i.response.send_message(f'✅ Added {xp} XP to {member.mention}', ephemeral=True)

@bot.tree.command(name='setxp', description='Set XP')
async def setxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    uid = str(member.id)
    if uid not in level_data: level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] = xp
    await i.response.send_message(f'✅ Set {xp} XP for {member.mention}', ephemeral=True)

@bot.tree.command(name='setlevel', description='Set level')
async def setlevel(i: discord.Interaction, member: discord.Member, lvl: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    uid = str(member.id)
    if uid not in level_data: level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['level'] = lvl
    await i.response.send_message(f'✅ Set level {lvl} for {member.mention}', ephemeral=True)

# ========== UTILITY COMMANDS ==========
@bot.tree.command(name='calc', description='Calculate')
async def calc(i: discord.Interaction, expression: str):
    if await check_tech_work(i): return
    try:
        res = eval(expression.replace('^', '**'))
        await i.response.send_message(f'🧮 `{expression}` = `{res}`', ephemeral=True)
    except:
        await i.response.send_message('❌ Invalid expression', ephemeral=True)

@bot.tree.command(name='poll', description='Create a poll')
async def poll(i: discord.Interaction, question: str, opt1: str, opt2: str, opt3: str = None, opt4: str = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message('❌ No permission!', ephemeral=True)
    opts = [opt1, opt2]
    if opt3: opts.append(opt3)
    if opt4: opts.append(opt4)
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    e = discord.Embed(title=f'📊 {question}', color=0x3498db)
    for idx, opt in enumerate(opts):
        e.add_field(name=f'{emojis[idx]} {opt}', value='0 votes', inline=False)
    msg = await i.channel.send(embed=e)
    for idx in range(len(opts)):
        await msg.add_reaction(emojis[idx])
    await i.response.send_message('✅ Poll created!', ephemeral=True)

afk_data = {}
@bot.tree.command(name='afk', description='Set AFK')
async def afk(i: discord.Interaction, reason: str = "AFK"):
    if await check_tech_work(i): return
    afk_data[str(i.user.id)] = reason
    await i.response.send_message(f'✅ {i.user.mention} is now AFK: {reason}', ephemeral=True)

@bot.tree.command(name='unafk', description='Remove AFK')
async def unafk(i: discord.Interaction):
    if await check_tech_work(i): return
    if str(i.user.id) in afk_data:
        del afk_data[str(i.user.id)]
        await i.response.send_message('✅ AFK removed', ephemeral=True)
    else:
        await i.response.send_message('❌ Not AFK', ephemeral=True)

@bot.tree.command(name='remindme', description='Set reminder')
async def remindme(i: discord.Interaction, time: str, reminder: str):
    if await check_tech_work(i): return
    try:
        unit = time[-1]
        amount = int(time[:-1])
        sec = amount * {'s':1, 'm':60, 'h':3600, 'd':86400}[unit]
        await i.response.send_message(f'✅ Reminder in {time}', ephemeral=True)
        await asyncio.sleep(sec)
        await i.user.send(f'⏰ Reminder: {reminder}')
    except:
        await i.response.send_message('❌ Use: 10s, 5m, 1h, 1d', ephemeral=True)

@bot.tree.command(name='timestamp', description='Current timestamp')
async def timestamp(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(f'🕐 {int(datetime.now().timestamp())}', ephemeral=True)

@bot.tree.command(name='color', description='Color info')
async def color(i: discord.Interaction, hex_code: str):
    if await check_tech_work(i): return
    try:
        color = int(hex_code.strip('#'), 16)
        e = discord.Embed(title=f'Color {hex_code}', color=color)
        e.add_field(name='RGB', value=f'{(color>>16)&255}, {(color>>8)&255}, {color&255}')
        await i.response.send_message(embed=e)
    except:
        await i.response.send_message('❌ Invalid hex', ephemeral=True)

@bot.tree.command(name='qr-code', description='Generate QR code')
async def qr_code(i: discord.Interaction, text: str):
    if await check_tech_work(i): return
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
    e = discord.Embed(title='📱 QR Code', color=0x3498db)
    e.set_image(url=url)
    await i.response.send_message(embed=e)

start_time = datetime.now()
@bot.tree.command(name='uptime', description='Bot uptime')
async def uptime(i: discord.Interaction):
    if await check_tech_work(i): return
    delta = datetime.now() - start_time
    await i.response.send_message(f'🕐 Uptime: {delta.days}d {delta.seconds//3600}h {(delta.seconds%3600)//60}m')

giveaways = {}
@bot.tree.command(name='giveaway', description='Start a giveaway')
async def giveaway(i: discord.Interaction, duration: str, prize: str, winners: int = 1):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        sec = amount * {'s':1, 'm':60, 'h':3600, 'd':86400}[unit]
        e = discord.Embed(title='🎁 Giveaway', description=f'Prize: {prize}\nWinners: {winners}\nDuration: {duration}', color=0x00ff00)
        msg = await i.channel.send(embed=e)
        await msg.add_reaction('🎉')
        giveaways[str(msg.id)] = {'channel': i.channel.id, 'prize': prize, 'winners': winners, 'end': datetime.now() + timedelta(seconds=sec)}
        await i.response.send_message('✅ Giveaway started!', ephemeral=True)
    except:
        await i.response.send_message('❌ Use: 10s, 5m, 1h, 1d', ephemeral=True)

# ========== FUN COMMANDS ==========
@bot.tree.command(name='cat', description='Random cat')
async def cat(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.thecatapi.com/v1/images/search') as r:
            data = await r.json()
            e = discord.Embed(title='🐱 Cat', color=0x3498db)
            e.set_image(url=data[0]['url'])
            await i.response.send_message(embed=e)

@bot.tree.command(name='roll', description='Roll dice')
async def roll(i: discord.Interaction, sides: int = 6):
    if await check_tech_work(i): return
    await i.response.send_message(f'🎲 You rolled {random.randint(1, sides)} (1-{sides})')

@bot.tree.command(name='8ball', description='Magic 8ball')
async def eightball(i: discord.Interaction, question: str):
    if await check_tech_work(i): return
    answers = ['Yes', 'No', 'Maybe', 'Definitely!', 'Not likely', 'Ask later', 'Of course!', 'Never']
    await i.response.send_message(f'🎱 {random.choice(answers)}')

@bot.tree.command(name='joke', description='Random joke')
async def joke(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://v2.jokeapi.dev/joke/Any?safe-mode') as r:
            data = await r.json()
            if data['type'] == 'single':
                await i.response.send_message(f'😂 {data["joke"]}')
            else:
                await i.response.send_message(f'😂 {data["setup"]}\n\n||{data["delivery"]}||')

@bot.tree.command(name='fact', description='Random fact')
async def fact(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://uselessfacts.jsph.pl/random.json?language=en') as r:
            data = await r.json()
            await i.response.send_message(f'📖 {data["text"]}')

@bot.tree.command(name='advice', description='Random advice')
async def advice(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.adviceslip.com/advice') as r:
            data = await r.json()
            await i.response.send_message(f'💡 {data["slip"]["advice"]}')

@bot.tree.command(name='quote', description='Random quote')
async def quote(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.quotable.io/random') as r:
            data = await r.json()
            await i.response.send_message(f'📝 "{data["content"]}" - {data["author"]}')

@bot.tree.command(name='trivia', description='Trivia question')
async def trivia(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://opentdb.com/api.php?amount=1&type=multiple') as r:
            data = await r.json()
            q = data['results'][0]
            await i.response.send_message(f'❓ {q["question"]} (Difficulty: {q["difficulty"]})', ephemeral=True)

@bot.tree.command(name='rps', description='Rock Paper Scissors')
async def rps(i: discord.Interaction, choice: str):
    if await check_tech_work(i): return
    choices = ['rock', 'paper', 'scissors']
    if choice.lower() not in choices:
        return await i.response.send_message('❌ Choose: rock, paper, scissors', ephemeral=True)
    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = "Tie!"
    elif (choice.lower() == 'rock' and bot_choice == 'scissors') or (choice.lower() == 'paper' and bot_choice == 'rock') or (choice.lower() == 'scissors' and bot_choice == 'paper'):
        result = "You win!"
    else:
        result = "I win!"
    await i.response.send_message(f'You chose {choice}, I chose {bot_choice}. {result}')

@bot.tree.command(name='flip', description='Flip coin')
async def flip(i: discord.Interaction):
    if await check_tech_work(i): return
    result = random.choice(['Heads', 'Tails'])
    await i.response.send_message(f'🪙 {result}!')

# ========== SETUP COMMANDS ==========
@bot.tree.command(name='setup-logs', description='Setup logging channel')
async def setup_logs(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    save(LOGS_SETTINGS_FILE, {str(i.guild_id): channel.id})
    await i.response.send_message(f'✅ Log channel set to {channel.mention}', ephemeral=True)

@bot.tree.command(name='setup-welcome', description='Setup welcome message')
async def setup_welcome(i: discord.Interaction, channel: discord.TextChannel, message: str = "Welcome {member}!"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    s[gid]['welcome_enabled'] = True
    s[gid]['welcome_channel_id'] = channel.id
    s[gid]['welcome_message'] = message
    save(WELCOME_SETTINGS_FILE, s)
    await i.response.send_message(f'✅ Welcome configured in {channel.mention}', ephemeral=True)

@bot.tree.command(name='setup-photowelcome', description='Setup photo welcome')
async def setup_photowelcome(i: discord.Interaction, channel: discord.TextChannel, image_url: str, title: str = "Welcome!", description: str = "Welcome {member}!"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    s[gid]['photo_welcome'] = {'enabled': True, 'channel_id': channel.id, 'image_url': image_url, 'welcome_title': title, 'welcome_description': description}
    save(WELCOME_SETTINGS_FILE, s)
    await i.response.send_message('✅ Photo welcome configured!', ephemeral=True)

@bot.tree.command(name='disable-welcome', description='Disable welcome')
async def disable_welcome(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid in s:
        s[gid]['welcome_enabled'] = False
        if 'photo_welcome' in s[gid]:
            s[gid]['photo_welcome']['enabled'] = False
        save(WELCOME_SETTINGS_FILE, s)
        await i.response.send_message('✅ Welcome disabled!', ephemeral=True)

@bot.tree.command(name='setup-captcha', description='Setup captcha')
async def setup_captcha(i: discord.Interaction, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    s[str(i.guild_id)] = {'enabled': True, 'verify_role_id': role.id}
    save(CAPTCHA_SETTINGS_FILE, s)
    await i.response.send_message(f'✅ Captcha configured with {role.mention}', ephemeral=True)

@bot.tree.command(name='disable-captcha', description='Disable captcha')
async def disable_captcha(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid in s:
        s[gid]['enabled'] = False
        save(CAPTCHA_SETTINGS_FILE, s)
        await i.response.send_message('✅ Captcha disabled!', ephemeral=True)

@bot.tree.command(name='setup-application', description='Setup roles for applications')
async def setup_application(i: discord.Interaction, moderator: discord.Role = None, administrator: discord.Role = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    if moderator: s[gid]['moderator_role'] = moderator.id
    if administrator: s[gid]['admin_role'] = administrator.id
    save(SETTINGS_FILE, s)
    await i.response.send_message('✅ Application roles saved', ephemeral=True)

@bot.tree.command(name='create-apps', description='Create application menu')
async def create_apps(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    s = load(SETTINGS_FILE).get(str(i.guild_id), {})
    if not s:
        return await i.response.send_message('❌ First use /setup-application', ephemeral=True)
    class AppSelect(discord.ui.Select):
        def __init__(self):
            opts = []
            if s.get('moderator_role'): opts.append(discord.SelectOption(label='Moderator', value='moderator'))
            if s.get('admin_role'): opts.append(discord.SelectOption(label='Administrator', value='admin'))
            super().__init__(placeholder='Choose position...', options=opts)
        async def callback(self, si):
            await si.response.send_modal(AppModal(self.values[0], s))
    view = discord.ui.View()
    view.add_item(AppSelect())
    await i.response.send_message(embed=discord.Embed(title='📝 Applications', description='Select a position'), view=view)

class AppModal(discord.ui.Modal):
    def __init__(self, role_type, s):
        self.role_type = role_type
        self.s = s
        super().__init__(title=f'Application for {role_type}')
        self.add_item(discord.ui.TextInput(label='Why do you want this position?', style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label='What experience do you have?', style=discord.TextStyle.paragraph))
    async def on_submit(self, i):
        rid = self.s.get(f'{self.role_type}_role')
        if rid and (r := i.guild.get_role(rid)):
            await i.response.send_message(f'✅ Application sent to {r.mention}!', ephemeral=True)
            e = discord.Embed(title=f'📥 New application for {self.role_type}', description=f'From: {i.user.mention}', color=0x00ff00)
            e.add_field(name='Why?', value=self.children[0].value[:500])
            e.add_field(name='Experience', value=self.children[1].value[:500])
            await i.channel.send(r.mention, embed=e)
        else:
            await i.response.send_message('❌ Role not found', ephemeral=True)

@bot.tree.command(name='setup-ticket', description='Setup ticket system')
async def setup_ticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Need admin!', ephemeral=True)
    TICKET_SETTINGS_FILE = 'ticket_settings.json'
    save(TICKET_SETTINGS_FILE, {str(i.guild_id): {'category': category.id, 'role': support_role.id}})
    class TicketView(discord.ui.View):
        @discord.ui.button(label='🎫 Create Ticket', style=discord.ButtonStyle.primary)
        async def create(self, bi, button):
            s = load(TICKET_SETTINGS_FILE).get(str(bi.guild_id), {})
            cat = bi.guild.get_channel(s.get('category'))
            role = bi.guild.get_role(s.get('role'))
            name = f'ticket-{bi.user.name.lower()}-{random.randint(100,999)}'
            ow = {bi.guild.default_role: discord.PermissionOverwrite(view_channel=False), bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
            if role: ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            ch = await bi.guild.create_text_channel(name, category=cat, overwrites=ow)
            class CloseView(discord.ui.View):
                @discord.ui.button(label='🔒 Close Ticket', style=discord.ButtonStyle.danger)
                async def close(self, ci, button):
                    await ci.response.send_message('Closing...', ephemeral=True)
                    await asyncio.sleep(3)
                    await ch.delete()
            await ch.send(f'{bi.user.mention} describe your issue', view=CloseView())
            await bi.response.send_message(f'✅ Ticket created: {ch.mention}', ephemeral=True)
    await i.channel.send('Click to create a ticket', view=TicketView())
    await i.response.send_message('✅ Ticket system configured!', ephemeral=True)

@bot.tree.command(name='invite', description='Invite bot')
async def invite(i: discord.Interaction):
    if await check_tech_work(i): return
    e = discord.Embed(title='🔗 Invite', description='Thanks for inviting me to your server!\nFor full functionality, leave all checkboxes and raise bot role above others.', color=discord.Color.blue())
    if i.guild.icon: e.set_thumbnail(url=i.guild.icon.url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='🤖 Invite Bot', style=discord.ButtonStyle.link, url=f'https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands'))
    view.add_item(discord.ui.Button(label='🌐 Community Server', style=discord.ButtonStyle.link, url='https://discord.gg/invite'))
    await i.response.send_message(embed=e, view=view)

# ========== EVENTS ==========
@bot.event
async def on_member_join(member):
    cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
    if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
        code = gen_captcha()
        active_captchas[str(member.id)] = {'code': code, 'attempts': 0, 'guild_id': member.guild.id, 'verify_role_id': rid}
        class View(discord.ui.View):
            def __init__(self): super().__init__(timeout=300)
            @discord.ui.button(label='✅ I am human', style=discord.ButtonStyle.green)
            async def btn(self, bi, b):
                if bi.user.id != member.id: return await bi.response.send_message("❌ Not for you!", ephemeral=True)
                class Modal(discord.ui.Modal):
                    def __init__(self, c, uid, gid, rid): self.c=c; self.uid=uid; self.gid=gid; self.rid=rid; super().__init__(title="🔐 Verification"); self.add_item(discord.ui.TextInput(label="Enter code", max_length=6, min_length=6))
                    async def on_submit(self, mi):
                        d = active_captchas.get(str(self.uid))
                        if not d: return await mi.response.send_message("❌ Expired!", ephemeral=True)
                        if self.children[0].value == d['code']:
                            g = bot.get_guild(self.gid)
                            if g and (r := g.get_role(self.rid)) and (mo := g.get_member(self.uid)):
                                await mo.add_roles(r)
                                await mi.response.send_message("✅ Verified!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                        else:
                            d['attempts'] += 1
                            if d['attempts'] >= 3:
                                if (g := bot.get_guild(self.gid)) and (mo := g.get_member(self.uid)):
                                    await mo.kick(reason="Failed captcha")
                                await mi.response.send_message("❌ Kicked!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                            else:
                                await mi.response.send_message(f"❌ Invalid! {3-d['attempts']} left", ephemeral=True)
                await bi.response.send_modal(Modal(code, member.id, member.guild.id, rid))
        e = discord.Embed(title='🔐 Verification', description=f'Welcome to {member.guild.name}!', color=0x3498db)
        e.add_field(name='Code', value=f'||{code}||')
        try: await member.send(embed=e, view=View())
        except: pass
    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('welcome_message', 'Welcome {member}!').replace('{member}', member.mention)
        await ch.send(msg)

@bot.event
async def on_member_remove(member):
    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('goodbye_message', '{member} left').replace('{member}', member.name)
        await ch.send(msg)
    e = discord.Embed(title='🚪 Member left', description=f'{member.mention} left', color=0xe74c3c)
    await send_log(member.guild.id, e)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')
    bot.loop.create_task(update_status())
    bot.loop.create_task(tech_work_checker())
    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=discord.Object(id=guild.id))
            print(f'📢 Synced for {guild.name}')
        except Exception as e:
            print(f'❌ Error for {guild.name}: {e}')
    print(f'📢 Bot on {len(bot.guilds)} servers')

@bot.event
async def on_message_delete(msg):
    if msg.author.bot: return
    e = discord.Embed(title='🗑️ Deleted', description=f'{msg.author.mention} in {msg.channel.mention}', color=0xe74c3c)
    e.add_field(name='Content', value=msg.content[:500] if msg.content else '*No text*')
    await send_log(msg.guild.id, e)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    e = discord.Embed(title='✏️ Edited', description=f'{before.author.mention}', color=0xe67e22)
    e.add_field(name='Before', value=before.content[:500] if before.content else '*No text*')
    e.add_field(name='After', value=after.content[:500] if after.content else '*No text*')
    await send_log(before.guild.id, e)


# ========== ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ ==========
@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')
    bot.loop.create_task(update_status())

    # ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ КОМАНД
    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=discord.Object(id=guild.id))
            print(f'📢 Synced for {guild.name}')
        except Exception as e:
            print(f'❌ Error for {guild.name}: {e}')

    # Глобальная синхронизация
    try:
        synced = await bot.tree.sync()
        print(f'📢 Total synced {len(synced)} commands')
    except Exception as e:
        print(f'❌ Global sync error: {e}')

    print(f'📢 Bot on {len(bot.guilds)} servers')

# ========== RUN ==========
TOKEN = ''
bot.run(os.environ['TOKEN'])
