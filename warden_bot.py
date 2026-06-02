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

LANG_SETTINGS_FILE = 'lang_settings.json'


def load_lang_settings():
    if os.path.exists(LANG_SETTINGS_FILE):
        with open(LANG_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_lang_settings(settings):
    with open(LANG_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


def get_lang(guild_id):
    settings = load_lang_settings()
    return settings.get(str(guild_id), 'en')


def get_text(guild_id, key, *args):
    lang = get_lang(guild_id)
    texts = {
        'ru': {
            'hello': 'Привет, {}! Я **Warden Bot** 🤖',
            'ping': '🏓 Понг! Задержка: {} мс',
            'info_title': '🛡️ Warden Bot',
            'info_desc': 'Бот-хранитель для твоего сервера',
            'info_version': 'Версия',
            'info_cmds': 'Команды',
            'report_staff_ticket_setup': '✅ Система жалоб на персонал настроена!',
            'partnership_ticket_setup': '✅ Система партнёрства настроена!',
            'report_staff_title': '⚠️ Жалобы на персонал',
            'report_staff_desc': 'Если вы столкнулись с неправомерными действиями сотрудника сервера, нажмите на кнопку ниже, чтобы подать жалобу.\n\n**Внимание:** Ложные жалобы могут привести к наказанию!',
            'report_staff_button': '📝 Пожаловаться на персонал',
            'report_staff_modal_title': '📝 Жалоба на персонал',
            'report_staff_against': 'На кого жалуетесь?',
            'report_staff_reason': 'Причина жалобы',
            'report_staff_proof': 'Доказательства',
            'report_staff_submitted': '✅ Ваша жалоба отправлена! Сотрудники рассмотрят её в ближайшее время.',
            'report_staff_embed_title': '⚠️ ЖАЛОБА НА ПЕРСОНАЛ',
            'report_staff_embed_footer': 'Пожалуйста, рассмотрите жалобу в ближайшее время',
            'partnership_title': '🤝 Сотрудничество',
            'partnership_desc': 'Если вы хотите предложить сотрудничество, рекламу или совместные ивенты, нажмите на кнопку ниже.\n\nМы рассмотрим все предложения!',
            'partnership_button': '🤝 Предложить сотрудничество',
            'partnership_modal_title': '🤝 Предложение сотрудничества',
            'partnership_server_name': 'Название сервера/проекта',
            'partnership_type': 'Тип сотрудничества',
            'partnership_description': 'Описание',
            'partnership_links': 'Ссылки',
            'partnership_contacts': 'Контакты для связи',
            'partnership_submitted': '✅ Ваше предложение отправлено! Мы рассмотрим его в ближайшее время.',
            'partnership_embed_title': '🤝 НОВОЕ ПРЕДЛОЖЕНИЕ СОТРУДНИЧЕСТВА',
            'info_footer': 'Всегда поддерживает порядок 🔒',
            'no_permission': '❌ Нет прав!',
            'need_admin': '❌ Нужны права администратора!',
            'error': '❌ Ошибка: {}',
            'sent': '✅ Отправлено в {}',
            'no_roles': '❌ Роли не указаны!',
            'settings_saved': '✅ Настройки сохранены',
            'log_channel_set': '✅ Канал логов: {}',
            'welcome_configured': '✅ Приветствия настроены в {}',
            'photo_welcome_configured': '✅ Фото-приветствие настроено!',
            'welcome_disabled': '✅ Приветствия отключены',
            'captcha_configured': '✅ Капча настроена!',
            'captcha_disabled': '✅ Капча отключена',
            'ticket_panel_created': '✅ Панель тикетов создана!',
            'ticket_created': '✅ Тикет создан: {}',
            'invite_title': '🔗 Пригласить',
            'invite_desc': 'Спасибо за приглашение на свой сервер!',
            'tech_work_title': '🛠️ Технические работы',
            'tech_work_desc': 'Бот временно недоступен.',
            'tech_work_enabled': '🛠️ Техработы ВКЛЮЧЕНЫ',
            'tech_work_disabled': '✅ Техработы ВЫКЛЮЧЕНЫ',
            'tech_work_status': '🛠️ Статус техработ: **{status}**',
            'no_tech_permission': '❌ У вас нет прав на использование этой команды!',
            'use_on_off_status': '❌ Используй: `on`, `off`, `status`',
            'muted': '🔇 {} заглушен на {}',
            'invalid_time': '❌ Введи положительное число минут (например: 30)',
            'not_muted': '❌ Не заглушен!',
            'unmuted': '✅ {} размучен',
            'kicked': '✅ {} выгнан',
            'banned': '✅ {} забанен',
            'user_not_found': '❌ Пользователь {} не найден!',
            'unbanned': '✅ Разбанен {}',
            'cleared': '✅ Удалено {} сообщений',
            'clear_range': '❌ 1-100 сообщений!',
            'warned': '⚠️ {} получил предупреждение #{}',
            'warn_reason': 'Причина',
            'warn_total': 'Всего',
            'no_warnings': '{} не имеет предупреждений',
            'warnings_title': '⚠️ Предупреждения {}',
            'warnings_total': 'Всего: {}',
            'warn_removed': '✅ Предупреждение #{} удалено',
            'warn_not_found': '❌ Предупреждение #{} не найдено!',
            'slowmode': '✅ Медленный режим {}с в {}',
            'locked': '🔒 {} закрыт',
            'unlocked': '🔓 {} открыт',
            'reset': '✅ {} сброшен',
            'report_sent': '✅ Репорт отправлен',
            'pinned': '📌 Закреплено',
            'unpinned': '📌 Откреплено',
            'msg_not_found': '❌ Сообщение не найдено',
            'antinuke_configured': '✅ Антинук настроен!',
            'role_added': '✅ Добавлена роль {} пользователю {}',
            'role_removed': '✅ Снята роль {} с {}',
            'role_created': '✅ Роль {} создана',
            'role_deleted': '✅ Роль удалена',
            'reaction_role_set': '✅ Реакция {} → {}',
            'channel_created': '✅ Канал #{} создан',
            'channel_deleted': '✅ Канал удалён',
            'channel_cloned': '✅ Канал #{} склонирован',
            'channel_moved': '✅ Канал #{} перемещён на позицию {}',
            'voice_muted': '🔇 Заглушен {} в голосовом',
            'voice_unmuted': '🔊 Снято заглушение {} в голосовом',
            'voice_deafened': '🔇 Оглушён {}',
            'voice_undeafened': '🔊 Снято оглушение {}',
            'voice_moved': '✅ Перемещён {} в {}',
            'voice_kicked': '🎤 {} выгнан из голосового',
            'not_in_voice': '❌ Не в голосовом канале!',
            'timeout_set': '⏰ {} таймаут на {} мин',
            'timeout_removed': '✅ {} таймаут снят',
            'softbanned': '✅ {} мягко забанен',
            'massbanned': '✅ Забанено {} пользователей',
            'bot_messages_deleted': '✅ Удалено {} сообщений бота',
            'strike_given': '⚠️ {} получил страйк #{}',
            'strike_removed': '✅ Страйк #{} снят с {}',
            'no_strikes': '✅ У {} нет страйков',
            'strike_not_found': '❌ Страйк #{} не найден',
            'nickname_set': '✅ Никнейм {} изменён на {}',
            'serverinfo_owner': 'Владелец',
            'serverinfo_members': 'Участников',
            'serverinfo_channels': 'Каналов',
            'serverinfo_roles': 'Ролей',
            'userinfo_title': 'Информация о {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'Присоединился',
            'userinfo_created': 'Создан',
            'userinfo_bot': 'Бот',
            'avatar_title': 'Аватар {}',
            'membercount_total': 'Всего',
            'membercount_humans': 'Людей',
            'membercount_bots': 'Ботов',
            'admins_list': '👑 Администраторы',
            'bots_list': '🤖 Боты',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Неверное выражение',
            'reminder_set': '✅ Напоминание через {}',
            'reminder_invalid': '❌ Используй: 10s, 5m, 1h, 1d',
            'uptime_text': '🕐 Время работы: {}д {}ч {}м',
            'poll_created': '✅ Опрос создан!',
            'poll_voted': '✅ Проголосовано!',
            'poll_total': 'Всего голосов: {}',
            'announce_sent': '✅ Отправлено в {}',
            'lang_title': '🌐 Выбор языка',
            'lang_desc': 'Нажми на кнопку ниже, чтобы выбрать язык',
            'lang_changed_ru': '🌐 Язык изменён на **Русский**! Команды обновлены',
            'lang_changed_en': '🌐 Language changed to **English**! Commands updated',
            'promotion_level': '📊 Твой уровень: {} | XP: {}',
            'leaderboard_title': '🏆 Таблица лидеров',
            'xp_added': '✅ Добавлено {} XP пользователю {}',
            'xp_set': '✅ Установлено {} XP для {}',
            'level_set': '✅ Установлен уровень {} для {}',
            'afk_set': '✅ {} теперь в AFK: {}',
            'afk_removed': '✅ AFK снят',
            'not_afk': '❌ Ты не в AFK',
            'timestamp_current': '🕐 Текущая метка времени: {}',
            'color_info': '🎨 Информация о цвете {}',
            'qr_code_title': '📱 QR Код',
            'giveaway_started': '🎁 Розыгрыш запущен!',
            'cat_title': '🐱 Случайный котик',
            'roll_result': '🎲 Ты выбросил {} (1-{})',
            'eightball_result': '🎱 {}',
            'joke_title': '😂 Шутка',
            'fact_title': '📖 Факт',
            'advice_title': '💡 Совет',
            'quote_title': '📝 Цитата',
            'trivia_question': '❓ {} (Сложность: {})',
            'rps_win': 'Ты выиграл!',
            'rps_lose': 'Я выиграл!',
            'rps_tie': 'Ничья!',
            'flip_heads': 'Орёл',
            'flip_tails': 'Решка',
            'none': 'Нет',
        },
        'en': {
            'hello': 'Hello, {}! I am **Warden Bot** 🤖',
            'ping': '🏓 Pong! Latency: {} ms',
            'info_title': '🛡️ Warden Bot',
            'info_desc': 'The guardian bot for your server',
            'info_version': 'Version',
            'info_cmds': 'Commands',
            'info_footer': 'Always keeping order 🔒',
            'no_permission': '❌ No permission!',
            'need_admin': '❌ Need admin permissions!',
            'error': '❌ Error: {}',
            'sent': '✅ Sent to {}',
            'report_staff_ticket_setup': '✅ Report staff ticket system setup!',
            'partnership_ticket_setup': '✅ Partnership ticket system setup!',
            'report_staff_title': '⚠️ Report Staff',
            'report_staff_desc': 'If you have encountered misconduct by a staff member, click the button below to submit a report.\n\n**Warning:** False reports may result in punishment!',
            'report_staff_button': '📝 Report Staff',
            'report_staff_modal_title': '📝 Staff Report',
            'report_staff_against': 'Who are you reporting?',
            'report_staff_reason': 'Reason for report',
            'report_staff_proof': 'Evidence',
            'report_staff_submitted': '✅ Your report has been submitted! Staff will review it shortly.',
            'report_staff_embed_title': '⚠️ STAFF REPORT',
            'report_staff_embed_footer': 'Please review this report promptly',
            'partnership_title': '🤝 Partnership',
            'partnership_desc': 'If you want to propose partnership, advertising, or joint events, click the button below.\n\nWe will review all proposals!',
            'partnership_button': '🤝 Propose Partnership',
            'partnership_modal_title': '🤝 Partnership Proposal',
            'partnership_server_name': 'Server/Project Name',
            'partnership_type': 'Partnership Type',
            'partnership_description': 'Description',
            'partnership_links': 'Links',
            'partnership_contacts': 'Contact Information',
            'partnership_submitted': '✅ Your proposal has been submitted! We will review it shortly.',
            'partnership_embed_title': '🤝 NEW PARTNERSHIP PROPOSAL',
            'no_roles': '❌ No roles specified!',
            'settings_saved': '✅ Settings saved',
            'log_channel_set': '✅ Log channel: {}',
            'welcome_configured': '✅ Welcome configured in {}',
            'photo_welcome_configured': '✅ Photo welcome configured!',
            'welcome_disabled': '✅ Welcome disabled',
            'captcha_configured': '✅ Captcha configured!',
            'captcha_disabled': '✅ Captcha disabled',
            'ticket_panel_created': '✅ Ticket panel created!',
            'ticket_created': '✅ Ticket created: {}',
            'invite_title': '🔗 Invite',
            'invite_desc': 'Thanks for inviting me to your server!',
            'tech_work_title': '🛠️ Maintenance',
            'tech_work_desc': 'Bot is temporarily unavailable.',
            'tech_work_enabled': '🛠️ Maintenance mode ENABLED',
            'tech_work_disabled': '✅ Maintenance mode DISABLED',
            'tech_work_status': '🛠️ Maintenance status: **{status}**',
            'no_tech_permission': '❌ You do not have permission to use this command!',
            'use_on_off_status': '❌ Use: `on`, `off`, `status`',
            'muted': '🔇 {} muted for {}',
            'invalid_time': '❌ Enter a positive number of minutes (e.g., 30)',
            'not_muted': '❌ Not muted!',
            'unmuted': '✅ {} unmuted',
            'kicked': '✅ {} kicked',
            'banned': '✅ {} banned',
            'user_not_found': '❌ User {} not found!',
            'unbanned': '✅ Unbanned {}',
            'cleared': '✅ Deleted {} messages',
            'clear_range': '❌ 1-100 messages only!',
            'warned': '⚠️ {} warned #{}',
            'warn_reason': 'Reason',
            'warn_total': 'Total',
            'no_warnings': '{} has no warnings',
            'warnings_title': '⚠️ Warnings for {}',
            'warnings_total': 'Total: {}',
            'warn_removed': '✅ Warning #{} removed',
            'warn_not_found': '❌ Warning #{} not found!',
            'slowmode': '✅ Slowmode {}s in {}',
            'locked': '🔒 {} locked',
            'unlocked': '🔓 {} unlocked',
            'reset': '✅ {} reset',
            'report_sent': '✅ Report sent',
            'pinned': '📌 Pinned',
            'unpinned': '📌 Unpinned',
            'msg_not_found': '❌ Message not found',
            'antinuke_configured': '✅ Antinuke configured!',
            'role_added': '✅ Added role {} to {}',
            'role_removed': '✅ Removed role {} from {}',
            'role_created': '✅ Role {} created',
            'role_deleted': '✅ Role deleted',
            'reaction_role_set': '✅ Reaction {} → {}',
            'channel_created': '✅ Channel #{} created',
            'channel_deleted': '✅ Channel deleted',
            'channel_cloned': '✅ Cloned #{}',
            'channel_moved': '✅ Moved #{} to position {}',
            'voice_muted': '🔇 Muted {} in voice',
            'voice_unmuted': '🔊 Unmuted {} in voice',
            'voice_deafened': '🔇 Deafened {}',
            'voice_undeafened': '🔊 Undeafened {}',
            'voice_moved': '✅ Moved {} to {}',
            'voice_kicked': '🎤 {} kicked from voice',
            'not_in_voice': '❌ Not in voice channel!',
            'timeout_set': '⏰ {} timed out for {}min',
            'timeout_removed': '✅ {} timeout removed',
            'softbanned': '✅ {} softbanned',
            'massbanned': '✅ Banned {} users',
            'bot_messages_deleted': '✅ Deleted {} bot messages',
            'strike_given': '⚠️ {} strike #{}',
            'strike_removed': '✅ Strike #{} removed from {}',
            'no_strikes': '✅ {} has no strikes',
            'strike_not_found': '❌ Strike #{} not found',
            'nickname_set': '✅ Nickname for {} changed to {}',
            'serverinfo_owner': 'Owner',
            'serverinfo_members': 'Members',
            'serverinfo_channels': 'Channels',
            'serverinfo_roles': 'Roles',
            'userinfo_title': 'Info about {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'Joined',
            'userinfo_created': 'Created',
            'userinfo_bot': 'Bot',
            'avatar_title': '{}\'s avatar',
            'membercount_total': 'Total',
            'membercount_humans': 'Humans',
            'membercount_bots': 'Bots',
            'admins_list': '👑 Administrators',
            'bots_list': '🤖 Bots',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Invalid expression',
            'reminder_set': '✅ Reminder in {}',
            'reminder_invalid': '❌ Use: 10s, 5m, 1h, 1d',
            'uptime_text': '🕐 Uptime: {}d {}h {}m',
            'poll_created': '✅ Poll created!',
            'poll_voted': '✅ Voted!',
            'poll_total': 'Total votes: {}',
            'announce_sent': '✅ Sent to {}',
            'lang_title': '🌐 Language Selection',
            'lang_desc': 'Click the button below to select language',
            'lang_changed_ru': '🌐 Язык изменён на **Русский**! Commands updated',
            'lang_changed_en': '🌐 Language changed to **English**! Commands updated',
            'promotion_level': '📊 Your level: {} | XP: {}',
            'leaderboard_title': '🏆 Leaderboard',
            'xp_added': '✅ Added {} XP to {}',
            'xp_set': '✅ Set {} XP for {}',
            'level_set': '✅ Set level {} for {}',
            'afk_set': '✅ {} is now AFK: {}',
            'afk_removed': '✅ AFK removed',
            'not_afk': '❌ You are not AFK',
            'timestamp_current': '🕐 Current timestamp: {}',
            'color_info': '🎨 Color info for {}',
            'qr_code_title': '📱 QR Code',
            'giveaway_started': '🎁 Giveaway started!',
            'cat_title': '🐱 Random Cat',
            'roll_result': '🎲 You rolled {} (1-{})',
            'eightball_result': '🎱 {}',
            'joke_title': '😂 Joke',
            'fact_title': '📖 Fact',
            'advice_title': '💡 Advice',
            'quote_title': '📝 Quote',
            'trivia_question': '❓ {} (Difficulty: {})',
            'rps_win': 'You win!',
            'rps_lose': 'I win!',
            'rps_tie': 'Tie!',
            'flip_heads': 'Heads',
            'flip_tails': 'Tails',
            'none': 'None',
        }
    }
    text = texts[lang].get(key, f'[{key}]')
    if args:
        return text.format(*args)
    return text


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
        embed = discord.Embed(title=get_text(str(i.guild_id), 'tech_work_title'),
                              description=get_text(str(i.guild_id), 'tech_work_desc'), color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)
        return True
    return False


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
                await bot.change_presence(activity=discord.Game(name="🛠️ Tech work"))
            else:
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


@bot.tree.command(name='tech_work', description='Manage maintenance mode')
async def tech_work_cmd(i: discord.Interaction, action: str):
    if i.user.id not in ALLOWED_TECH_USERS:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_tech_permission'), ephemeral=True)
    global tech_work_active
    if action.lower() == 'on':
        tech_work_active = True
        await i.response.send_message(get_text(str(i.guild_id), 'tech_work_enabled'), ephemeral=True)
    elif action.lower() == 'off':
        tech_work_active = False
        await i.response.send_message(get_text(str(i.guild_id), 'tech_work_disabled'), ephemeral=True)
    elif action.lower() == 'status':
        status = "ENABLED" if tech_work_active else "DISABLED"
        await i.response.send_message(get_text(str(i.guild_id), 'tech_work_status', status=status), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'use_on_off_status'), ephemeral=True)


@bot.tree.command(name='lang', description='Change bot language')
async def lang_cmd(i: discord.Interaction):
    class LangView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.button(label='🇷🇺 Русский', style=discord.ButtonStyle.primary)
        async def russian_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            s = load_lang_settings()
            s[str(btn_i.guild_id)] = 'ru'
            save_lang_settings(s)
            await btn_i.response.send_message(get_text(str(btn_i.guild_id), 'lang_changed_ru'), ephemeral=True)

        @discord.ui.button(label='🇬🇧 English', style=discord.ButtonStyle.primary)
        async def english_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            s = load_lang_settings()
            s[str(btn_i.guild_id)] = 'en'
            save_lang_settings(s)
            await btn_i.response.send_message(get_text(str(btn_i.guild_id), 'lang_changed_en'), ephemeral=True)

    e = discord.Embed(title=get_text(str(i.guild_id), 'lang_title'), description=get_text(str(i.guild_id), 'lang_desc'),
                      color=discord.Color.blue())
    await i.response.send_message(embed=e, view=LangView())


@bot.tree.command(name='hello', description='Greet Warden bot')
async def hello(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(get_text(str(i.guild_id), 'hello', i.user.mention))


@bot.tree.command(name='ping', description='Check bot latency')
async def ping(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(get_text(str(i.guild_id), 'ping', round(bot.latency * 1000)))


@bot.tree.command(name='info', description='Bot information')
async def info(i: discord.Interaction):
    if await check_tech_work(i): return
    e = discord.Embed(title=get_text(str(i.guild_id), 'info_title'), description=get_text(str(i.guild_id), 'info_desc'),
                      color=discord.Color.blue())
    e.add_field(name=get_text(str(i.guild_id), 'info_version'), value='v1.0.0', inline=True)
    e.add_field(name=get_text(str(i.guild_id), 'info_cmds'), value='Use `/help` to see all commands', inline=False)
    e.set_footer(text=get_text(str(i.guild_id), 'info_footer'))
    await i.response.send_message(embed=e)


HELP_CATEGORIES = [
    {'id': 'overview', 'emoji': '📚', 'name_ru': 'Обзор', 'name_en': 'Overview', 'cmds': []},
    {'id': 'all', 'emoji': '📖', 'name_ru': 'Все команды', 'name_en': 'All Commands', 'cmds': []},

    {'id': 'mod', 'emoji': '🛡️', 'name_ru': 'Модерация', 'name_en': 'Moderation',
     'cmds': ['/mute', '/unmute', '/ban', '/unban', '/kick', '/clear', '/warn', '/warnings', '/topwarnings', '/unwarn',
              '/slowmode', '/lock', '/unlock', '/report', '/pin', '/unpin', '/vkick', '/timeout', '/untimeout',
              '/softban', '/massban', '/clean', '/strike', '/unstrike', '/strikes', '/topstrikes', '/setnick',
              '/setupantinuke']},

    {'id': 'roles', 'emoji': '👮', 'name_ru': 'Роли и каналы', 'name_en': 'Roles & Channels',
     'cmds': ['/addrole', '/removerole', '/createrole', '/deleterole', '/createchannel', '/deletechannel',
              '/clonechannel', '/movechannel']},

    {'id': 'voice', 'emoji': '🎤', 'name_ru': 'Голос', 'name_en': 'Voice',
     'cmds': ['/vmute', '/vunmute', '/vdeafen', '/vundeafen', '/vmove']},

    {'id': 'info', 'emoji': '📋', 'name_ru': 'Инфо', 'name_en': 'Info',
     'cmds': ['/hello', '/ping', '/info', '/serverinfo', '/userinfo', '/avatar', '/membercount', '/admins', '/bots']},

    {'id': 'level', 'emoji': '⭐', 'name_ru': 'Продвижение', 'name_en': 'Leveling',
     'cmds': ['/promotion', '/setuppromotion', '/leaderboard', '/addxp', '/setxp', '/setlevel']},

    {'id': 'util', 'emoji': '🛠️', 'name_ru': 'Утилиты', 'name_en': 'Utility',
     'cmds': ['/calc', '/poll', '/afk', '/unafk', '/remindme', '/timestamp', '/color', '/qr-code', '/uptime',
              '/giveaway']},

    {'id': 'fun', 'emoji': '🎉', 'name_ru': 'Развлечения', 'name_en': 'Fun',
     'cmds': ['/cat', '/roll', '/8ball', '/joke', '/fact', '/advice', '/quote', '/trivia', '/rps', '/flip']},

    {'id': 'setup', 'emoji': '⚙️', 'name_ru': 'Настройки', 'name_en': 'Settings',
     'cmds': ['/setup-logs', '/setup-welcome', '/setup-photowelcome', '/disable-welcome', '/setup-captcha',
              '/disable-captcha', '/setup-ticket', '/invite', '/tech_work', '/create-application',
              '/list-applications', '/delete-application']},

    {'id': 'misc', 'emoji': '🔗', 'name_ru': 'Прочее', 'name_en': 'Misc',
     'cmds': ['/help', '/lang']},
]


def build_help_embed(i, category_id=None):
    lang = get_lang(str(i.guild_id))
    embed = discord.Embed(color=discord.Color.blue())

    embed.set_author(name='Wander Bot - Помощь', icon_url=bot.user.display_avatar.url)
    embed.set_footer(text='А вы знали что всего 88 команд? :3')

    if category_id == 'overview' or category_id is None:
        embed.description = 'Выбери категорию из списка ниже, чтобы посмотреть её команды.\n"📖 **Все команды**" покажет все команды сразу удобно!'

        for cat in HELP_CATEGORIES[2:]:
            name = cat['name_ru'] if lang == 'ru' else cat['name_en']
            embed.add_field(name=f'{cat["emoji"]} **{name}**',
                            value=f'`{len(cat["cmds"])}` команд',
                            inline=True)

    elif category_id == 'all':
        embed.title = '📖 **Все команды**'
        embed.description = 'Полный список всех слэш-команд, разбит по категориям.'

        embed.add_field(name='🛡️ **Модерация**',
                        value='`/mute` `/unmute` `/ban` `/unban` `/kick` `/clear` `/warn` `/warnings` `/topwarnings` `/unwarn` `/slowmode` `/lock` `/unlock` `/report` `/pin` `/unpin` `/vkick` `/timeout` `/untimeout` `/softban` `/massban` `/clean` `/strike` `/unstrike` `/strikes` `/topstrikes` `/setnick` `/setupantinuke`',
                        inline=False)

        embed.add_field(name='👮 **Роли и каналы**',
                        value='`/addrole` `/removerole` `/createrole` `/deleterole` `/createchannel` `/deletechannel` `/clonechannel` `/movechannel`',
                        inline=False)

        embed.add_field(name='🎤 **Голос**',
                        value='`/vmute` `/vunmute` `/vdeafen` `/vundeafen` `/vmove`',
                        inline=False)

        embed.add_field(name='📋 **Инфо**',
                        value='`/hello` `/ping` `/info` `/serverinfo` `/userinfo` `/avatar` `/membercount` `/admins` `/bots`',
                        inline=False)

        embed.add_field(name='⭐ **Продвижение**',
                        value='`/promotion` `/setuppromotion` `/leaderboard` `/addxp` `/setxp` `/setlevel`',
                        inline=False)

        embed.add_field(name='🛠️ **Утилиты**',
                        value='`/calc` `/poll` `/afk` `/unafk` `/remindme` `/timestamp` `/color` `/qr-code` `/uptime` `/giveaway`',
                        inline=False)

        embed.add_field(name='🎉 **Развлечения**',
                        value='`/cat` `/roll` `/8ball` `/joke` `/fact` `/advice` `/quote` `/trivia` `/rps` `/flip`',
                        inline=False)

        embed.add_field(name='⚙️ **Настройки**',
                        value='`/setup-logs` `/setup-welcome` `/setup-photowelcome` `/disable-welcome` `/setup-captcha` `/disable-captcha` `/setup-ticket` `/invite` `/tech_work` `/create-application` `/list-applications` `/delete-application`',
                        inline=False)

        embed.add_field(name='🔗 **Прочее**',
                        value='`/help` `/lang`',
                        inline=False)

    elif category_id:
        for cat in HELP_CATEGORIES:
            if cat['id'] == category_id:
                name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                embed.title = f'{cat["emoji"]} **{name}**'
                embed.description = f'Список всех команд в категории:'

                cmds = cat['cmds']
                if len(cmds) > 12:
                    chunk_size = (len(cmds) + 2) // 3
                    chunks = [cmds[i:i + chunk_size] for i in range(0, len(cmds), chunk_size)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f'📌 **Часть {i + 1}**' if len(chunks) > 1 else f'📌 **{name}** ({len(cmds)})',
                            value=' '.join(chunk), inline=False)
                else:
                    embed.add_field(name=f'📌 **{name}** ({len(cmds)})', value=' '.join(cmds), inline=False)
                break

    return embed


def build_help_components(i):
    lang = get_lang(str(i.guild_id))
    view = discord.ui.View(timeout=120)

    class HelpSelect(discord.ui.Select):
        def __init__(self):
            options = []
            for cat in HELP_CATEGORIES:
                name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                if cat['id'] == 'overview':
                    description = 'Вернуться к началу' if lang == 'ru' else 'Back to start'
                elif cat['id'] == 'all':
                    description = 'Все 88 команд' if lang == 'ru' else 'All 88 commands'
                else:
                    description = f'{len(cat["cmds"])} команд' if lang == 'ru' else f'{len(cat["cmds"])} commands'
                options.append(
                    discord.SelectOption(label=name, emoji=cat['emoji'], value=cat['id'], description=description))
            super().__init__(placeholder='📋 Выбери категорию...' if lang == 'ru' else '📋 Choose a category...',
                             options=options, min_values=1, max_values=1)

        async def callback(self, select_interaction: discord.Interaction):
            category_id = self.values[0]
            embed = build_help_embed(select_interaction, category_id)

            for cat in HELP_CATEGORIES:
                if cat['id'] == category_id:
                    self.placeholder = f'{cat["emoji"]} {cat["name_ru"] if lang == "ru" else cat["name_en"]}'
                    break

            await select_interaction.response.edit_message(embed=embed, view=view)

    view.add_item(HelpSelect())

    invite_btn = discord.ui.Button(label='Пригласить', style=discord.ButtonStyle.url,
                                   url='https://discord.com/oauth2/authorize?client_id=1510998282254549012&permissions=8&integration_type=0&scope=bot+applications.commands')
    server_btn = discord.ui.Button(label='Сервер сообщества', style=discord.ButtonStyle.url,
                                   url='https://discord.gg/njVYNFs6Zk')

    view.add_item(invite_btn)
    view.add_item(server_btn)

    return view


try:
    bot.tree.remove_command('help')
except:
    pass


@bot.tree.command(name='help', description='Все команды бота с категориями')
async def help_command(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(embed=build_help_embed(i), view=build_help_components(i))


from datetime import datetime, timedelta, timezone


@bot.tree.command(name='mute', description='Mute a member (time in minutes)')
async def mute(i: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    if minutes <= 0:
        return await i.response.send_message(
            get_text(str(i.guild_id), 'invalid_time'),
            ephemeral=True
        )

    if minutes > 40320:
        return await i.response.send_message(
            "❌ Максимум 28 дней (40320 минут)",
            ephemeral=True
        )

    try:
        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)

        if minutes < 60:
            time_text = f"{minutes} мин"
        elif minutes < 1440:
            hours = minutes // 60
            mins = minutes % 60
            time_text = f"{hours} ч {mins} мин" if mins > 0 else f"{hours} ч"
        else:
            days = minutes // 1440
            hours = (minutes % 1440) // 60
            time_text = f"{days} д {hours} ч" if hours > 0 else f"{days} д"

        await i.response.send_message(
            get_text(str(i.guild_id), 'muted', member.mention, time_text),
            ephemeral=True
        )
    except Exception as e:
        await i.response.send_message(
            get_text(str(i.guild_id), 'error', str(e)),
            ephemeral=True
        )


@bot.tree.command(name='unmute', description='Unmute a member')
async def unmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.timed_out_until is None:
        return await i.response.send_message(get_text(str(i.guild_id), 'not_muted'), ephemeral=True)
    await member.timeout(None)
    await i.response.send_message(get_text(str(i.guild_id), 'unmuted', member.mention), ephemeral=True)


@bot.tree.command(name='ban', description='Ban a member')
async def ban(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.ban(reason=reason)
    await i.response.send_message(get_text(str(i.guild_id), 'banned', member.mention), ephemeral=True)


@bot.tree.command(name='unban', description='Unban by ID')
async def unban(i: discord.Interaction, user_id: str, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    banned = [entry async for entry in i.guild.bans()]
    target = next((entry.user for entry in banned if str(entry.user.id) == user_id), None)

    if not target:
        return await i.response.send_message(get_text(str(i.guild_id), 'user_not_found', user_id), ephemeral=True)

    await i.guild.unban(target, reason=reason)
    await i.response.send_message(get_text(str(i.guild_id), 'unbanned', target.name), ephemeral=True)


@bot.tree.command(name='kick', description='Kick a member')
async def kick(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.kick(reason=reason)
    await i.response.send_message(get_text(str(i.guild_id), 'kicked', member.mention), ephemeral=True)


@bot.tree.command(name='warn', description='Warn a member')
async def warn(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(member.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    wid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': wid, 'reason': reason, 'mod': i.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)
    await i.response.send_message(get_text(str(i.guild_id), 'warned', member.mention, wid), ephemeral=True)


@bot.tree.command(name='warnings', description='Show warnings')
async def warnings(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(member.id), [])
    if not w:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_warnings', member.mention), ephemeral=True)
    e = discord.Embed(title=get_text(str(i.guild_id), 'warnings_title', member.name),
                      description=get_text(str(i.guild_id), 'warnings_total', len(w)), color=0xe67e22)
    for ww in w[-5:]:
        mod = i.guild.get_member(ww['mod'])
        e.add_field(name=f"Warning #{ww['id']}",
                    value=f"**Reason:** {ww['reason']}\n**Mod:** {mod.name if mod else 'Unknown'}", inline=False)
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topwarnings', description='Top warnings')
async def topwarnings(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {})
    if not w:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_warnings', ''), ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := i.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Top warnings', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} warnings', inline=False)
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='unwarn', description='Remove warning')
async def unwarn(i: discord.Interaction, member: discord.Member, warn_id: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(member.id)
    if gid not in w or uid not in w[gid]:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_warnings', member.mention), ephemeral=True)
    for idx, ww in enumerate(w[gid][uid]):
        if ww['id'] == warn_id:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)
            return await i.response.send_message(get_text(str(i.guild_id), 'warn_removed', warn_id), ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'warn_not_found', warn_id), ephemeral=True)


@bot.tree.command(name='slowmode', description='Set slowmode')
async def slowmode(i: discord.Interaction, channel: discord.TextChannel, seconds: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.edit(slowmode_delay=seconds)
    await i.response.send_message(get_text(str(i.guild_id), 'slowmode', seconds, channel.mention), ephemeral=True)


@bot.tree.command(name='lock', description='Lock channel')
async def lock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=False)
    await i.response.send_message(get_text(str(i.guild_id), 'locked', channel.mention), ephemeral=True)


@bot.tree.command(name='unlock', description='Unlock channel')
async def unlock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=None)
    await i.response.send_message(get_text(str(i.guild_id), 'unlocked', channel.mention), ephemeral=True)


@bot.tree.command(name='report', description='Report user')
async def report(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_tech_work(i): return
    e = discord.Embed(title='📢 Report', description=f'{i.user.mention} reported {user.mention}',
                      color=discord.Color.red())
    e.add_field(name='Reason', value=reason)
    await send_log(i.guild_id, e)
    await i.response.send_message(get_text(str(i.guild_id), 'report_sent'), ephemeral=True)


@bot.tree.command(name='pin', description='Pin message')
async def pin(i: discord.Interaction, message_id: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.pin()
        await i.response.send_message(get_text(str(i.guild_id), 'pinned'), ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='unpin', description='Unpin message')
async def unpin(i: discord.Interaction, message_id: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.unpin()
        await i.response.send_message(get_text(str(i.guild_id), 'unpinned'), ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='vmute', description='Mute in voice')
async def vmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(mute=True)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_muted', member.mention), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vunmute', description='Unmute in voice')
async def vunmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(mute=False)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_unmuted', member.mention), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vdeafen', description='Deafen in voice')
async def vdeafen(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=True)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_deafened', member.mention), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vundeafen', description='Undeafen in voice')
async def vundeafen(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=False)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_undeafened', member.mention), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vkick', description='Kick from voice')
async def vkick(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(None)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_kicked', member.mention), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vmove', description='Move in voice')
async def vmove(i: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(channel)
        await i.response.send_message(get_text(str(i.guild_id), 'voice_moved', member.mention, channel.name),
                                      ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='serverinfo', description='Server info')
async def serverinfo(i: discord.Interaction):
    if await check_tech_work(i): return
    g = i.guild
    e = discord.Embed(title=f'📊 {g.name}', color=0x3498db)
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_owner'), value=g.owner.mention if g.owner else 'Unknown')
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_members'), value=g.member_count)
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_channels'), value=len(g.channels))
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_roles'), value=len(g.roles))
    await i.response.send_message(embed=e)


@bot.tree.command(name='userinfo', description='User info')
async def userinfo(i: discord.Interaction, member: discord.Member = None):
    if await check_tech_work(i): return
    m = member or i.user
    e = discord.Embed(title=get_text(str(i.guild_id), 'userinfo_title', m.name), color=m.color if m.color else 0x3498db)
    if m.avatar: e.set_thumbnail(url=m.avatar.url)
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_id'), value=m.id)
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_joined'),
                value=m.joined_at.strftime('%d.%m.%Y') if m.joined_at else 'Unknown')
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_created'), value=m.created_at.strftime('%d.%m.%Y'))
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_bot'), value='Yes' if m.bot else 'No')
    await i.response.send_message(embed=e)


@bot.tree.command(name='avatar', description='Show avatar')
async def avatar(i: discord.Interaction, member: discord.Member = None):
    if await check_tech_work(i): return
    m = member or i.user
    e = discord.Embed(title=get_text(str(i.guild_id), 'avatar_title', m.name), color=0x3498db)
    e.set_image(url=m.display_avatar.url)
    await i.response.send_message(embed=e)


@bot.tree.command(name='membercount', description='Member count')
async def membercount(i: discord.Interaction):
    if await check_tech_work(i): return
    total = i.guild.member_count
    humans = sum(1 for m in i.guild.members if not m.bot)
    bots = total - humans
    e = discord.Embed(title='📊 Member Count', color=0x3498db)
    e.add_field(name=get_text(str(i.guild_id), 'membercount_total'), value=total)
    e.add_field(name=get_text(str(i.guild_id), 'membercount_humans'), value=humans)
    e.add_field(name=get_text(str(i.guild_id), 'membercount_bots'), value=bots)
    await i.response.send_message(embed=e)


@bot.tree.command(name='admins', description='Server admins')
async def admins(i: discord.Interaction):
    if await check_tech_work(i): return
    admins_list = [m.mention for m in i.guild.members if m.guild_permissions.administrator]
    await i.response.send_message(' '.join(admins_list) or get_text(str(i.guild_id), 'none', 'None'), ephemeral=True)


@bot.tree.command(name='bots', description='Bots on server')
async def bots(i: discord.Interaction):
    if await check_tech_work(i): return
    bots_list = [m.mention for m in i.guild.members if m.bot]
    await i.response.send_message(' '.join(bots_list) or get_text(str(i.guild_id), 'none', 'None'), ephemeral=True)


@bot.tree.command(name='timeout', description='Timeout member')
async def timeout(i: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.timeout(datetime.now() + timedelta(minutes=minutes), reason=reason)
    await i.response.send_message(get_text(str(i.guild_id), 'timeout_set', member.mention, minutes), ephemeral=True)


@bot.tree.command(name='untimeout', description='Remove timeout')
async def untimeout(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.timeout(None)
    await i.response.send_message(get_text(str(i.guild_id), 'timeout_removed', member.mention), ephemeral=True)


@bot.tree.command(name='softban', description='Softban')
async def softban(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.ban(reason=reason)
    await i.guild.unban(member, reason="Softban")
    await i.response.send_message(get_text(str(i.guild_id), 'softbanned', member.mention), ephemeral=True)


@bot.tree.command(name='massban', description='Mass ban')
async def massban(i: discord.Interaction, ids: str, reason: str = "Not specified"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    ids_list = ids.split()
    count = 0
    for uid in ids_list:
        try:
            user = await bot.fetch_user(int(uid))
            await i.guild.ban(user, reason=reason)
            count += 1
        except:
            pass
    await i.response.send_message(get_text(str(i.guild_id), 'massbanned', count), ephemeral=True)


@bot.tree.command(name='clean', description='Clean bot messages')
async def clean(i: discord.Interaction, amount: int = 10):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    deleted = 0
    async for msg in i.channel.history(limit=amount):
        if msg.author == bot.user:
            await msg.delete()
            deleted += 1
    await i.response.send_message(get_text(str(i.guild_id), 'bot_messages_deleted', deleted), ephemeral=True)


@bot.tree.command(name='strike', description='Give strike')
async def strike(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(user.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    sid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': sid, 'reason': reason, 'mod': i.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)
    await i.response.send_message(get_text(str(i.guild_id), 'strike_given', user.mention, sid), ephemeral=True)


@bot.tree.command(name='unstrike', description='Remove strike')
async def unstrike(i: discord.Interaction, user: discord.Member, sid: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(i.guild_id), str(user.id)
    if gid not in w or uid not in w[gid]:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_strikes', user.mention), ephemeral=True)
    for idx, s in enumerate(w[gid][uid]):
        if s['id'] == sid:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)
            return await i.response.send_message(get_text(str(i.guild_id), 'strike_removed', sid, user.mention),
                                                 ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'strike_not_found', sid), ephemeral=True)


@bot.tree.command(name='strikes', description='Show strikes')
async def strikes(i: discord.Interaction, user: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(user.id), [])
    if not w:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_strikes', user.mention), ephemeral=True)
    e = discord.Embed(title=f'⚠️ Strikes for {user.name}', description=f'Total: {len(w)}', color=0xe67e22)
    for s in w[-5:]:
        mod = i.guild.get_member(s['mod'])
        e.add_field(name=f"Strike #{s['id']}", value=f"Reason: {s['reason']}\nMod: {mod.name if mod else 'Unknown'}",
                    inline=False)
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topstrikes', description='Top strikes')
async def topstrikes(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
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
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.edit(nick=nick)
    await i.response.send_message(get_text(str(i.guild_id), 'nickname_set', member.mention, nick), ephemeral=True)


@bot.tree.command(name='setupantinuke', description='Setup antinuke')
async def setupantinuke(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'antinuke_configured'), ephemeral=True)


@bot.tree.command(name='addrole', description='Add role')
async def addrole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.add_roles(role)
    await i.response.send_message(get_text(str(i.guild_id), 'role_added', role.mention, member.mention), ephemeral=True)


@bot.tree.command(name='removerole', description='Remove role')
async def removerole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.remove_roles(role)
    await i.response.send_message(get_text(str(i.guild_id), 'role_removed', role.mention, member.mention),
                                  ephemeral=True)


@bot.tree.command(name='createrole', description='Create role')
async def createrole(i: discord.Interaction, name: str, color: str = "default"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    cols = {'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff, 'yellow': 0xffff00, 'purple': 0xff00ff,
            'default': 0x99aab5}
    r = await i.guild.create_role(name=name, color=cols.get(color, 0x99aab5))
    await i.response.send_message(get_text(str(i.guild_id), 'role_created', r.mention), ephemeral=True)


@bot.tree.command(name='deleterole', description='Delete role')
async def deleterole(i: discord.Interaction, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await role.delete()
    await i.response.send_message(get_text(str(i.guild_id), 'role_deleted'), ephemeral=True)


@bot.tree.command(name='reactionrole', description='Reaction role')
async def reactionrole(i: discord.Interaction, msg_id: str, role: discord.Role, emoji: str):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(msg_id))
        await msg.add_reaction(emoji)
        rr = load(REACTION_ROLES_FILE)
        rr[f"{i.guild_id}_{msg_id}_{emoji}"] = role.id
        save(REACTION_ROLES_FILE, rr)
        await i.response.send_message(get_text(str(i.guild_id), 'reaction_role_set', emoji, role.mention),
                                      ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'error', 'Message not found'), ephemeral=True)


@bot.tree.command(name='createchannel', description='Create channel')
async def createchannel(i: discord.Interaction, name: str, category: discord.CategoryChannel = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await i.guild.create_text_channel(name, category=category)
    await i.response.send_message(get_text(str(i.guild_id), 'channel_created', name), ephemeral=True)


@bot.tree.command(name='deletechannel', description='Delete channel')
async def deletechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.delete()
    await i.response.send_message(get_text(str(i.guild_id), 'channel_deleted'), ephemeral=True)


@bot.tree.command(name='clonechannel', description='Clone channel')
async def clonechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.clone()
    await i.response.send_message(get_text(str(i.guild_id), 'channel_cloned', ch.name), ephemeral=True)


@bot.tree.command(name='movechannel', description='Move channel')
async def movechannel(i: discord.Interaction, ch: discord.TextChannel, pos: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.edit(position=pos)
    await i.response.send_message(get_text(str(i.guild_id), 'channel_moved', ch.name, pos), ephemeral=True)


level_data = {}


@bot.tree.command(name='promotion', description='Your level')
async def promotion(i: discord.Interaction):
    if await check_tech_work(i): return
    uid = str(i.user.id)
    lvl = level_data.get(uid, {}).get('level', 0)
    xp = level_data.get(uid, {}).get('xp', 0)
    await i.response.send_message(get_text(str(i.guild_id), 'promotion_level', lvl, xp), ephemeral=True)


@bot.tree.command(name='setuppromotion', description='Setup leveling')
async def setuppromotion(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'settings_saved'), ephemeral=True)


@bot.tree.command(name='leaderboard', description='Level leaderboard')
async def leaderboard(i: discord.Interaction):
    if await check_tech_work(i): return
    sorted_users = sorted(level_data.items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:10]
    text = ''
    for idx, (uid, data) in enumerate(sorted_users, 1):
        m = i.guild.get_member(int(uid))
        if m:
            text += f'{idx}. {m.name} - Level {data.get("level", 0)} ({data.get("xp", 0)} XP)\n'
    if not text:
        text = 'No data yet'
    e = discord.Embed(title=get_text(str(i.guild_id), 'leaderboard_title'), description=text, color=0x3498db)
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='addxp', description='Add XP')
async def addxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] += xp
    await i.response.send_message(get_text(str(i.guild_id), 'xp_added', xp, member.mention), ephemeral=True)


@bot.tree.command(name='setxp', description='Set XP')
async def setxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] = xp
    await i.response.send_message(get_text(str(i.guild_id), 'xp_set', xp, member.mention), ephemeral=True)


@bot.tree.command(name='setlevel', description='Set level')
async def setlevel(i: discord.Interaction, member: discord.Member, lvl: int):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['level'] = lvl
    await i.response.send_message(get_text(str(i.guild_id), 'level_set', lvl, member.mention), ephemeral=True)


@bot.tree.command(name='calc', description='Calculate')
async def calc(i: discord.Interaction, expression: str):
    if await check_tech_work(i): return
    try:
        res = eval(expression.replace('^', '**'))
        await i.response.send_message(get_text(str(i.guild_id), 'calc_result', expression, res), ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'calc_invalid'), ephemeral=True)


@bot.tree.command(name='poll', description='Create a poll')
async def poll(i: discord.Interaction, question: str, opt1: str, opt2: str, opt3: str = None, opt4: str = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
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
    await i.response.send_message(get_text(str(i.guild_id), 'poll_created'), ephemeral=True)


afk_data = {}


@bot.tree.command(name='afk', description='Set AFK')
async def afk(i: discord.Interaction, reason: str = "AFK"):
    if await check_tech_work(i): return
    afk_data[str(i.user.id)] = reason
    await i.response.send_message(get_text(str(i.guild_id), 'afk_set', i.user.mention, reason), ephemeral=True)


@bot.tree.command(name='unafk', description='Remove AFK')
async def unafk(i: discord.Interaction):
    if await check_tech_work(i): return
    if str(i.user.id) in afk_data:
        del afk_data[str(i.user.id)]
        await i.response.send_message(get_text(str(i.guild_id), 'afk_removed'), ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_afk'), ephemeral=True)


@bot.tree.command(name='remindme', description='Set reminder')
async def remindme(i: discord.Interaction, time: str, reminder: str):
    if await check_tech_work(i): return
    try:
        unit = time[-1]
        amount = int(time[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        await i.response.send_message(get_text(str(i.guild_id), 'reminder_set', time), ephemeral=True)
        await asyncio.sleep(sec)
        await i.user.send(f'⏰ Reminder: {reminder}')
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'reminder_invalid'), ephemeral=True)


@bot.tree.command(name='timestamp', description='Current timestamp')
async def timestamp(i: discord.Interaction):
    if await check_tech_work(i): return
    await i.response.send_message(get_text(str(i.guild_id), 'timestamp_current', int(datetime.now().timestamp())),
                                  ephemeral=True)


@bot.tree.command(name='color', description='Color info')
async def color(i: discord.Interaction, hex_code: str):
    if await check_tech_work(i): return
    try:
        color = int(hex_code.strip('#'), 16)
        e = discord.Embed(title=get_text(str(i.guild_id), 'color_info', hex_code), color=color)
        e.add_field(name='RGB', value=f'{(color >> 16) & 255}, {(color >> 8) & 255}, {color & 255}')
        await i.response.send_message(embed=e)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'error', 'Invalid hex'), ephemeral=True)


@bot.tree.command(name='qr-code', description='Generate QR code')
async def qr_code(i: discord.Interaction, text: str):
    if await check_tech_work(i): return
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
    e = discord.Embed(title=get_text(str(i.guild_id), 'qr_code_title'), color=0x3498db)
    e.set_image(url=url)
    await i.response.send_message(embed=e)


start_time = datetime.now()


@bot.tree.command(name='uptime', description='Bot uptime')
async def uptime(i: discord.Interaction):
    if await check_tech_work(i): return
    delta = datetime.now() - start_time
    await i.response.send_message(
        get_text(str(i.guild_id), 'uptime_text', delta.days, delta.seconds // 3600, (delta.seconds % 3600) // 60))


giveaways = {}


@bot.tree.command(name='giveaway', description='Start a giveaway')
async def giveaway(i: discord.Interaction, duration: str, prize: str, winners: int = 1):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        e = discord.Embed(title='🎁 Giveaway', description=f'Prize: {prize}\nWinners: {winners}\nDuration: {duration}',
                          color=0x00ff00)
        msg = await i.channel.send(embed=e)
        await msg.add_reaction('🎉')
        giveaways[str(msg.id)] = {'channel': i.channel.id, 'prize': prize, 'winners': winners,
                                  'end': datetime.now() + timedelta(seconds=sec)}
        await i.response.send_message(get_text(str(i.guild_id), 'giveaway_started'), ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'invalid_time'), ephemeral=True)


@bot.tree.command(name='cat', description='Random cat')
async def cat(i: discord.Interaction):
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.thecatapi.com/v1/images/search') as r:
            data = await r.json()
            e = discord.Embed(title=get_text(str(i.guild_id), 'cat_title'), color=0x3498db)
            e.set_image(url=data[0]['url'])
            await i.response.send_message(embed=e)


@bot.tree.command(name='roll', description='Roll dice')
async def roll(i: discord.Interaction, sides: int = 6):
    if await check_tech_work(i): return
    result = random.randint(1, sides)
    await i.response.send_message(get_text(str(i.guild_id), 'roll_result', result, sides))


@bot.tree.command(name='8ball', description='Magic 8ball')
async def eightball(i: discord.Interaction, question: str):
    if await check_tech_work(i): return
    answers = ['Yes', 'No', 'Maybe', 'Definitely!', 'Not likely', 'Ask later', 'Of course!', 'Never']
    await i.response.send_message(get_text(str(i.guild_id), 'eightball_result', random.choice(answers)))


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
            await i.response.send_message(get_text(str(i.guild_id), 'trivia_question', q['question'], q['difficulty']),
                                          ephemeral=True)


@bot.tree.command(name='rps', description='Rock Paper Scissors')
async def rps(i: discord.Interaction, choice: str):
    if await check_tech_work(i): return
    choices = ['rock', 'paper', 'scissors']
    if choice.lower() not in choices:
        return await i.response.send_message(get_text(str(i.guild_id), 'error', 'Choose: rock, paper, scissors'),
                                             ephemeral=True)
    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = get_text(str(i.guild_id), 'rps_tie')
    elif (choice.lower() == 'rock' and bot_choice == 'scissors') or (
            choice.lower() == 'paper' and bot_choice == 'rock') or (
            choice.lower() == 'scissors' and bot_choice == 'paper'):
        result = get_text(str(i.guild_id), 'rps_win')
    else:
        result = get_text(str(i.guild_id), 'rps_lose')
    await i.response.send_message(f'You chose {choice}, I chose {bot_choice}. {result}')


@bot.tree.command(name='flip', description='Flip coin')
async def flip(i: discord.Interaction):
    if await check_tech_work(i): return
    result = random.choice([get_text(str(i.guild_id), 'flip_heads'), get_text(str(i.guild_id), 'flip_tails')])
    await i.response.send_message(f'🪙 {result}!')


@bot.tree.command(name='setup-logs', description='Setup logging channel')
async def setup_logs(i: discord.Interaction, channel: discord.TextChannel):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    save(LOGS_SETTINGS_FILE, {str(i.guild_id): channel.id})
    await i.response.send_message(get_text(str(i.guild_id), 'log_channel_set', channel=channel.mention), ephemeral=True)


@bot.tree.command(name='setup-welcome', description='Setup welcome message')
async def setup_welcome(i: discord.Interaction, channel: discord.TextChannel, message: str = "Welcome {member}!"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s:
        s[gid] = {}

    s[gid]['welcome_enabled'] = True
    s[gid]['welcome_channel_id'] = channel.id
    s[gid]['welcome_message'] = message
    save(WELCOME_SETTINGS_FILE, s)

    await i.response.send_message(
        get_text(str(i.guild_id), 'welcome_configured', channel.mention),
        ephemeral=True
    )


@bot.tree.command(name='setup-photowelcome', description='Setup photo welcome')
async def setup_photowelcome(i: discord.Interaction, channel: discord.TextChannel, image_url: str,
                             title: str = "Welcome!", description: str = "Welcome {member}!"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    s[gid]['photo_welcome'] = {'enabled': True, 'channel_id': channel.id, 'image_url': image_url,
                               'welcome_title': title, 'welcome_description': description}
    save(WELCOME_SETTINGS_FILE, s)
    await i.response.send_message(get_text(str(i.guild_id), 'photo_welcome_configured'), ephemeral=True)


@bot.tree.command(name='disable-welcome', description='Disable welcome')
async def disable_welcome(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid in s:
        s[gid]['welcome_enabled'] = False
        if 'photo_welcome' in s[gid]:
            s[gid]['photo_welcome']['enabled'] = False
        save(WELCOME_SETTINGS_FILE, s)
        await i.response.send_message(get_text(str(i.guild_id), 'welcome_disabled'), ephemeral=True)


@bot.tree.command(name='setup-captcha', description='Setup captcha')
async def setup_captcha(i: discord.Interaction, role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    s[str(i.guild_id)] = {'enabled': True, 'verify_role_id': role.id}
    save(CAPTCHA_SETTINGS_FILE, s)
    await i.response.send_message(get_text(str(i.guild_id), 'captcha_configured', role=role.mention), ephemeral=True)


APPLICATIONS_FILE = 'applications.json'


def load_applications():
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_applications(apps):
    with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=4, ensure_ascii=False)


@bot.tree.command(name='create-application', description='Создать новую заявку с вопросами')
async def create_application(i: discord.Interaction, название: str, роль: discord.Role):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    apps = load_applications()
    gid = str(i.guild_id)

    if gid not in apps:
        apps[gid] = {}

    app_id = len(apps[gid]) + 1

    apps[gid][str(app_id)] = {
        'name': название,
        'role_id': роль.id,
        'questions': [],
        'channel_id': i.channel_id,
        'creator_id': i.user.id
    }
    save_applications(apps)

    class AddQuestionView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label='➕ Добавить вопрос', style=discord.ButtonStyle.primary)
        async def add_question(self, btn_i: discord.Interaction, button: discord.ui.Button):
            modal = AddQuestionModal(app_id, название, роль, gid, i.channel.id)
            await btn_i.response.send_modal(modal)

        @discord.ui.button(label='✅ Завершить создание', style=discord.ButtonStyle.success)
        async def finish(self, btn_i: discord.Interaction, button: discord.ui.Button):
            apps_check = load_applications()
            questions = apps_check.get(gid, {}).get(str(app_id), {}).get('questions', [])
            if len(questions) < 1:
                return await btn_i.response.send_message('❌ Добавь хотя бы 1 вопрос!', ephemeral=True)

            class ApplicationMenu(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label=f'📝 Подать заявку: {название}', style=discord.ButtonStyle.primary)
                async def apply(self, apply_i: discord.Interaction, button: discord.ui.Button):
                    await apply_i.response.send_modal(ApplicationModal(app_id, gid))

            embed = discord.Embed(
                title=f'📝 {название}',
                description=f'Нажми на кнопку ниже, чтобы подать заявку.\nПосле проверки ты получишь роль {роль.mention}',
                color=discord.Color.blue()
            )
            await i.channel.send(embed=embed, view=ApplicationMenu())
            await btn_i.response.send_message('✅ Заявка создана! Кнопка отправлена в канал.', ephemeral=True)
            self.stop()

    class AddQuestionModal(discord.ui.Modal):
        def __init__(self, app_id, app_name, role, gid, channel_id):
            self.app_id = app_id
            self.app_name = app_name
            self.role = role
            self.gid = gid
            self.channel_id = channel_id
            super().__init__(title=f'Добавить вопрос в "{app_name}"')
            self.add_item(discord.ui.TextInput(label='Вопрос', style=discord.TextStyle.paragraph,
                                               placeholder='Напиши вопрос для заявки...'))

        async def on_submit(self, modal_i: discord.Interaction):
            question = self.children[0].value
            apps = load_applications()

            if self.gid not in apps:
                apps[self.gid] = {}
            if str(self.app_id) not in apps[self.gid]:
                apps[self.gid][str(self.app_id)] = {'questions': []}

            apps[self.gid][str(self.app_id)]['questions'].append(question)
            save_applications(apps)

            await modal_i.response.send_message(
                f'✅ Вопрос добавлен! (Всего: {len(apps[self.gid][str(self.app_id)]["questions"])})', ephemeral=True)

    embed = discord.Embed(
        title='📝 Создание заявки',
        description=f'**Название:** {название}\n**Роль:** {роль.mention}\n\nНажми на кнопки ниже, чтобы добавить вопросы.',
        color=discord.Color.green()
    )
    await i.response.send_message(embed=embed, view=AddQuestionView(), ephemeral=True)


class ApplicationModal(discord.ui.Modal):
    def __init__(self, app_id, guild_id):
        self.app_id = app_id
        self.guild_id = guild_id
        self.app_data = load_applications().get(guild_id, {}).get(str(app_id), {})
        self.questions = self.app_data.get('questions', [])

        super().__init__(title=f'📝 {self.app_data.get("name", "Заявка")}')

        for i, q in enumerate(self.questions[:5]):
            self.add_item(discord.ui.TextInput(label=q[:45], style=discord.TextStyle.paragraph, required=True))

    async def on_submit(self, interaction: discord.Interaction):

        app_data = load_applications().get(self.guild_id, {}).get(str(self.app_id), {})
        role_id = app_data.get('role_id')
        app_name = app_data.get('name', 'Заявка')

        role = interaction.guild.get_role(role_id) if role_id else None

        embed = discord.Embed(
            title=f'📥 Новая заявка: {app_name}',
            description=f'От: {interaction.user.mention}\nID: {interaction.user.id}',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for i, (q, a) in enumerate(zip(app_data.get('questions', []), self.children)):
            embed.add_field(name=f'❓ Вопрос {i + 1}', value=f'**{q[:50]}**\n{a.value[:500]}', inline=False)

        channel_id = app_data.get('channel_id')
        channel = interaction.guild.get_channel(channel_id) if channel_id else interaction.channel

        class ReviewView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=86400)

            @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success)
            async def approve(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                if role:
                    await interaction.user.add_roles(role)
                    await btn_i.response.send_message(
                        f'✅ Заявка одобрена! {interaction.user.mention} получил роль {role.mention}', ephemeral=True)
                else:
                    await btn_i.response.send_message('✅ Заявка одобрена!', ephemeral=True)
                await btn_i.message.edit(view=None)

            @discord.ui.button(label='❌ Отказать', style=discord.ButtonStyle.danger)
            async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                await btn_i.response.send_modal(RejectModal(interaction.user, btn_i.message))

        class RejectModal(discord.ui.Modal):
            def __init__(self, user, msg):
                self.user = user
                self.msg = msg
                super().__init__(title='Причина отказа')
                self.add_item(discord.ui.TextInput(label='Причина', style=discord.TextStyle.paragraph,
                                                   placeholder='Укажите причину отказа...'))

            async def on_submit(self, modal_i: discord.Interaction):
                reason = self.children[0].value
                await self.user.send(f'❌ Ваша заявка **{app_name}** отклонена.\nПричина: {reason}')
                await modal_i.response.send_message(f'❌ Заявка отклонена. Причина отправлена пользователю.',
                                                    ephemeral=True)
                await self.msg.edit(view=None)

        await channel.send(role.mention if role else '', embed=embed, view=ReviewView())
        await interaction.response.send_message('✅ Заявка отправлена! Ожидай решения.', ephemeral=True)


@bot.tree.command(name='list-applications', description='Показать список созданных заявок')
async def list_applications(i: discord.Interaction):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    apps = load_applications().get(str(i.guild_id), {})
    if not apps:
        return await i.response.send_message('❌ Нет созданных заявок!', ephemeral=True)

    embed = discord.Embed(title='📋 Список заявок', color=discord.Color.blue())
    for app_id, app_data in apps.items():
        role = i.guild.get_role(app_data.get('role_id'))
        embed.add_field(
            name=f'ID: {app_id} - {app_data.get("name")}',
            value=f'Роль: {role.mention if role else "Не указана"}\nВопросов: {len(app_data.get("questions", []))}',
            inline=False
        )
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='delete-application', description='Удалить заявку по ID')
async def delete_application(i: discord.Interaction, id_заявки: str):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    apps = load_applications()
    gid = str(i.guild_id)

    if gid not in apps or id_заявки not in apps[gid]:
        return await i.response.send_message('❌ Заявка не найдена!', ephemeral=True)

    del apps[gid][id_заявки]
    save_applications(apps)
    await i.response.send_message(f'✅ Заявка #{id_заявки} удалена!', ephemeral=True)


@bot.tree.command(name='disable-captcha', description='Disable captcha')
async def disable_captcha(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid in s:
        s[gid]['enabled'] = False
        save(CAPTCHA_SETTINGS_FILE, s)
        await i.response.send_message(get_text(str(i.guild_id), 'captcha_disabled'), ephemeral=True)


@bot.tree.command(name='setup-application', description='Setup roles for applications')
async def setup_application(i: discord.Interaction, moderator: discord.Role = None, administrator: discord.Role = None):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    if moderator: s[gid]['moderator_role'] = moderator.id
    if administrator: s[gid]['admin_role'] = administrator.id
    save(SETTINGS_FILE, s)
    await i.response.send_message(get_text(str(i.guild_id), 'settings_saved'), ephemeral=True)


@bot.tree.command(name='create-apps', description='Create application menu')
async def create_apps(i: discord.Interaction):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE).get(str(i.guild_id), {})
    if not s:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_roles'), ephemeral=True)

    class AppSelect(discord.ui.Select):
        def __init__(self):
            opts = []
            if s.get('moderator_role'):
                opts.append(discord.SelectOption(label='Moderator', emoji='🛡️', value='moderator'))
            if s.get('admin_role'):
                opts.append(discord.SelectOption(label='Administrator', emoji='👑', value='admin'))
            super().__init__(placeholder='📋 Choose a position...', options=opts, min_values=1, max_values=1)

        async def callback(self, select_interaction: discord.Interaction):
            await select_interaction.response.send_modal(AppModal(self.values[0], s))

    view = discord.ui.View()
    view.add_item(AppSelect())
    e = discord.Embed(title='📝 Applications', description='Select a position from the menu below to apply.',
                      color=0x2b2d31)
    await i.response.send_message(embed=e, view=view)


class AppModal(discord.ui.Modal):
    def __init__(self, role_type, s):
        self.role_type = role_type
        self.s = s
        super().__init__(title=f'Application for {role_type.title()}')
        self.add_item(discord.ui.TextInput(label='Why do you want this position?', style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label='What experience do you have?', style=discord.TextStyle.paragraph))

    async def on_submit(self, i: discord.Interaction):
        rid = self.s.get(f'{self.role_type}_role')
        if rid and (r := i.guild.get_role(rid)):
            await i.response.send_message(f'✅ Application sent to {r.mention}!', ephemeral=True)
            e = discord.Embed(title=f'📥 New application for {self.role_type.title()}',
                              description=f'From: {i.user.mention}', color=0x00ff00)
            e.add_field(name='Why?', value=self.children[0].value[:500])
            e.add_field(name='Experience', value=self.children[1].value[:500])
            await i.channel.send(r.mention, embed=e)
        else:
            await i.response.send_message(get_text(str(i.guild_id), 'error', 'Role not found'), ephemeral=True)


@bot.tree.command(name='setup-ticket', description='Setup ticket system')
async def setup_ticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    save(TICKET_SETTINGS_FILE, {str(i.guild_id): {'category': category.id, 'role': support_role.id}})

    class TicketView(discord.ui.View):
        @discord.ui.button(label='🎫 Create Ticket', style=discord.ButtonStyle.primary)
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            s = load(TICKET_SETTINGS_FILE).get(str(bi.guild_id), {})
            cat = bi.guild.get_channel(s.get('category'))
            role = bi.guild.get_role(s.get('role'))
            name = f'ticket-{bi.user.name.lower()}-{random.randint(100, 999)}'
            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
            ch = await bi.guild.create_text_channel(name, category=cat, overwrites=ow)

            class CloseView(discord.ui.View):
                @discord.ui.button(label='🔒 Close', style=discord.ButtonStyle.danger)
                async def close(self, ci: discord.Interaction, button: discord.ui.Button):
                    await ci.response.send_message('Closing...', ephemeral=True)
                    await asyncio.sleep(3)
                    await ch.delete()

            e = discord.Embed(title='🎫 Ticket Created', description=f'{bi.user.mention} describe your issue',
                              color=0x3498db)
            await ch.send(embed=e, view=CloseView())
            await bi.response.send_message(get_text(str(bi.guild_id), 'ticket_created', channel=ch.mention),
                                           ephemeral=True)

    e = discord.Embed(title='🎫 Ticket System', description='Click the button below to create a ticket', color=0x3498db)
    await i.channel.send(embed=e, view=TicketView())
    await i.response.send_message(get_text(str(i.guild_id), 'ticket_panel_created'), ephemeral=True)


@bot.tree.command(name='invite', description='Invite bot')
async def invite(i: discord.Interaction):
    if await check_tech_work(i): return
    e = discord.Embed(title=get_text(str(i.guild_id), 'invite_title'),
                      description=get_text(str(i.guild_id), 'invite_desc'), color=discord.Color.blue())
    if i.guild.icon:
        e.set_thumbnail(url=i.guild.icon.url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='🤖 Invite Bot', style=discord.ButtonStyle.link,
                                    url=f'https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands'))
    view.add_item(
        discord.ui.Button(label='🌐 Community Server', style=discord.ButtonStyle.link, url='https://discord.gg/invite'))
    await i.response.send_message(embed=e, view=view)


@bot.event
async def on_member_join(member):
    cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
    if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
        code = gen_captcha()
        active_captchas[str(member.id)] = {'code': code, 'attempts': 0, 'guild_id': member.guild.id,
                                           'verify_role_id': rid}

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)

            @discord.ui.button(label='✅ I am human', style=discord.ButtonStyle.green)
            async def btn(self, bi: discord.Interaction, button: discord.ui.Button):
                if bi.user.id != member.id:
                    return await bi.response.send_message("❌ Not for you!", ephemeral=True)

                class Modal(discord.ui.Modal):
                    def __init__(self, c, uid, gid, rid):
                        self.c = c
                        self.uid = uid
                        self.gid = gid
                        self.rid = rid
                        super().__init__(title="🔐 Verification")
                        self.add_item(discord.ui.TextInput(label="Enter 6-digit code", max_length=6, min_length=6))

                    async def on_submit(self, mi: discord.Interaction):
                        d = active_captchas.get(str(self.uid))
                        if not d:
                            return await mi.response.send_message("❌ Expired!", ephemeral=True)
                        if self.children[0].value == d['code']:
                            g = bot.get_guild(self.gid)
                            if g and (r := g.get_role(self.rid)) and (mo := g.get_member(self.uid)):
                                await mo.add_roles(r)
                                await mi.response.send_message("✅ Verified! Welcome!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                        else:
                            d['attempts'] += 1
                            if d['attempts'] >= 3:
                                if (g := bot.get_guild(self.gid)) and (mo := g.get_member(self.uid)):
                                    await mo.kick(reason="Failed captcha")
                                await mi.response.send_message("❌ Kicked for 3 failed attempts!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                            else:
                                await mi.response.send_message(f"❌ Invalid! {3 - d['attempts']} attempts left",
                                                               ephemeral=True)

                await bi.response.send_modal(Modal(code, member.id, member.guild.id, rid))

        e = discord.Embed(title='🔐 Verification Required', description=f'Welcome to {member.guild.name}!',
                          color=0x3498db)
        e.add_field(name='Code', value=f'||{code}||')
        e.set_footer(text='5 minutes | 3 attempts')
        try:
            await member.send(embed=e, view=View())
        except:
            pass

    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('welcome_message', 'Welcome {member}!')
        msg = msg.replace('{member}', member.mention)
        await ch.send(msg)


@bot.event
async def on_member_remove(member):
    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('goodbye_message', '{member} left')
        msg = msg.replace('{member}', member.name)
        await ch.send(msg)
    e = discord.Embed(title='🚪 Member left', description=f'{member.mention} left', color=0xe74c3c)
    await send_log(member.guild.id, e)


@bot.event
async def on_message_delete(msg):
    if msg.author.bot:
        return
    e = discord.Embed(title='🗑️ Message deleted', description=f'{msg.author.mention} in {msg.channel.mention}',
                      color=0xe74c3c)
    e.add_field(name='Content', value=msg.content[:500] if msg.content else '*No text*')
    await send_log(msg.guild.id, e)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content:
        return
    e = discord.Embed(title='✏️ Message edited', description=f'{before.author.mention}', color=0xe67e22)
    e.add_field(name='Before', value=before.content[:500] if before.content else '*No text*')
    e.add_field(name='After', value=after.content[:500] if after.content else '*No text*')
    await send_log(before.guild.id, e)


@bot.tree.command(name='setup-reportstaffticket', description='Setup report staff ticket system')
async def setup_reportstaffticket(i: discord.Interaction, category: discord.CategoryChannel,
                                  support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    save(TICKET_SETTINGS_FILE, {str(i.guild_id): {
        'report_staff_category': category.id,
        'report_staff_role': support_role.id,
        'ticket_type': 'report_staff'
    }})

    class ReportStaffTicketView(discord.ui.View):
        @discord.ui.button(label=get_text(str(i.guild_id), 'report_staff_button'), style=discord.ButtonStyle.danger,
                           emoji='⚠️')
        async def create_report(self, bi: discord.Interaction, button: discord.ui.Button):
            s = load(TICKET_SETTINGS_FILE).get(str(bi.guild_id), {})
            cat = bi.guild.get_channel(s.get('report_staff_category'))
            role = bi.guild.get_role(s.get('report_staff_role'))
            name = f'report-{bi.user.name.lower()}-{random.randint(100, 999)}'

            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

            ch = await bi.guild.create_text_channel(name, category=cat, overwrites=ow)

            class ReportModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title=get_text(str(bi.guild_id), 'report_staff_modal_title'))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'report_staff_against'),
                                                       placeholder='Укажите ник или ID сотрудника', required=True))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'report_staff_reason'),
                                                       placeholder='Опишите ситуацию...', required=True,
                                                       style=discord.TextStyle.paragraph))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'report_staff_proof'),
                                                       placeholder='Ссылки на скриншоты', required=False))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title=get_text(str(modal_i.guild_id), 'report_staff_embed_title'),
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='👤 На кого', value=self.children[0].value, inline=False)
                    embed.add_field(name='📋 Причина', value=self.children[1].value, inline=False)
                    if self.children[2].value:
                        embed.add_field(name='🔗 Доказательства', value=self.children[2].value, inline=False)
                    embed.set_footer(text=get_text(str(modal_i.guild_id), 'report_staff_embed_footer'))

                    await ch.send(role.mention if role else '', embed=embed)
                    await modal_i.response.send_message(get_text(str(modal_i.guild_id), 'report_staff_submitted'),
                                                        ephemeral=True)

            await bi.response.send_modal(ReportModal())

    e = discord.Embed(
        title=get_text(str(i.guild_id), 'report_staff_title'),
        description=get_text(str(i.guild_id), 'report_staff_desc'),
        color=discord.Color.red()
    )
    await i.channel.send(embed=e, view=ReportStaffTicketView())
    await i.response.send_message(get_text(str(i.guild_id), 'report_staff_ticket_setup'), ephemeral=True)


@bot.tree.command(name='setup-partnershipticket', description='Setup partnership ticket system')
async def setup_partnershipticket(i: discord.Interaction, category: discord.CategoryChannel,
                                  support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    save(TICKET_SETTINGS_FILE, {str(i.guild_id): {
        'partnership_category': category.id,
        'partnership_role': support_role.id,
        'ticket_type': 'partnership'
    }})

    class PartnershipTicketView(discord.ui.View):
        @discord.ui.button(label=get_text(str(i.guild_id), 'partnership_button'), style=discord.ButtonStyle.success,
                           emoji='🤝')
        async def create_partnership(self, bi: discord.Interaction, button: discord.ui.Button):
            s = load(TICKET_SETTINGS_FILE).get(str(bi.guild_id), {})
            cat = bi.guild.get_channel(s.get('partnership_category'))
            role = bi.guild.get_role(s.get('partnership_role'))
            name = f'partnership-{bi.user.name.lower()}-{random.randint(100, 999)}'

            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

            ch = await bi.guild.create_text_channel(name, category=cat, overwrites=ow)

            class PartnershipModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title=get_text(str(bi.guild_id), 'partnership_modal_title'))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'partnership_server_name'),
                                                       placeholder='Введите название', required=True))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'partnership_type'),
                                                       placeholder='Реклама, взаимный пиар и т.д.', required=True))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'partnership_description'),
                                                       placeholder='Расскажите подробнее...', required=True,
                                                       style=discord.TextStyle.paragraph))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'partnership_links'),
                                                       placeholder='Ссылки на сервер, соцсети', required=False))
                    self.add_item(discord.ui.TextInput(label=get_text(str(bi.guild_id), 'partnership_contacts'),
                                                       placeholder='Discord, Telegram', required=True))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title=get_text(str(modal_i.guild_id), 'partnership_embed_title'),
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='📌 Название', value=self.children[0].value, inline=False)
                    embed.add_field(name='📋 Тип', value=self.children[1].value, inline=False)
                    embed.add_field(name='📝 Описание', value=self.children[2].value, inline=False)
                    if self.children[3].value:
                        embed.add_field(name='🔗 Ссылки', value=self.children[3].value, inline=False)
                    embed.add_field(name='📞 Контакты', value=self.children[4].value, inline=False)

                    await ch.send(role.mention if role else '', embed=embed)
                    await modal_i.response.send_message(get_text(str(modal_i.guild_id), 'partnership_submitted'),
                                                        ephemeral=True)

            await bi.response.send_modal(PartnershipModal())

    e = discord.Embed(
        title=get_text(str(i.guild_id), 'partnership_title'),
        description=get_text(str(i.guild_id), 'partnership_desc'),
        color=discord.Color.green()
    )
    await i.channel.send(embed=e, view=PartnershipTicketView())
    await i.response.send_message(get_text(str(i.guild_id), 'partnership_ticket_setup'), ephemeral=True)


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

    try:
        synced = await bot.tree.sync()
        print(f'📢 Total synced {len(synced)} commands')
    except Exception as e:
        print(f'❌ Global sync error: {e}')

    print(f'📢 Bot on {len(bot.guilds)} servers')


TOKEN = 'MTUxMDk5ODI4MjI1NDU0OTAxMg.GZaGA1.GdLyzAv9nMfOfPoHSuQcUw3ZWvZHhZS8kEVYyc'
bot.run(TOKEN)
