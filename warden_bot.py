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
from openai import AsyncOpenAI
import yt_dlp

# ========== НАСТРОЙКА ЛИЧНЫХ ВОЙСОВ ==========
PRIVATE_VOICE_SETTINGS_FILE = 'private_voice_settings.json'
user_voice_channels = {}  # {user_id: channel_id}

TECH_MODE = False
YOUR_ID = 1436760469980450816
tech_work_active = False

# ========== НАСТРОЙКА ЦВЕТОВ ==========
COLOR_BLUE    = discord.Color.blue()        # 🔵 Синий
COLOR_SUCCESS = discord.Color.green()       # 🟢 Зелёный
COLOR_ERROR   = discord.Color.red()         # 🔴 Красный (для ошибок)
COLOR_WHITE   = discord.Color.from_rgb(255, 255, 255)  # ⚪ БЕЛЫЙ

def load_private_voice_settings():
    if os.path.exists(PRIVATE_VOICE_SETTINGS_FILE):
        with open(PRIVATE_VOICE_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_private_voice_settings(settings):
    with open(PRIVATE_VOICE_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

bot = commands.Bot(command_prefix='bari ', intents=discord.Intents.all())

# =====================================================
# 🔥 КОМАНДА /SetActivityCheck
# =====================================================

# Файл для сохранения канала
ACTIVITY_CHECK_FILE = 'activity_check_channel.json'


# Загружаем сохранённый канал при запуске
def load_activity_channel():
    if os.path.exists(ACTIVITY_CHECK_FILE):
        with open(ACTIVITY_CHECK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('channel_id')
    return None


# Сохраняем канал
def save_activity_channel(channel_id):
    with open(ACTIVITY_CHECK_FILE, 'w', encoding='utf-8') as f:
        json.dump({'channel_id': channel_id}, f, indent=4, ensure_ascii=False)


# Загружаем канал при старте
activity_check_channel_id = load_activity_channel()

# Файл для сохранения дня
DAY_COUNTER_FILE = 'day_counter.json'


def get_current_day():
    """Возвращает текущий день и увеличивает счётчик"""
    if os.path.exists(DAY_COUNTER_FILE):
        with open(DAY_COUNTER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            last_date = data.get('last_date')
            current_day = data.get('current_day', 1)

            today = datetime.now().strftime('%Y-%m-%d')
            if last_date != today:
                current_day += 1
                data['current_day'] = current_day
                data['last_date'] = today
                with open(DAY_COUNTER_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            return current_day
    else:
        data = {'current_day': 1, 'last_date': datetime.now().strftime('%Y-%m-%d')}
        with open(DAY_COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return 1


def get_next_ppl_range(member_count: int) -> int:
    """Определяет следующий диапазон PPL (округление до десятков)"""
    if member_count <= 0:
        return 10
    next_ppl = ((member_count + 9) // 10) * 10
    if member_count % 10 == 0:
        next_ppl = member_count + 10
    return next_ppl


async def send_activity_check():
    global activity_check_channel_id
    if activity_check_channel_id is None:
        return
    channel = bot.get_channel(activity_check_channel_id)
    if not channel:
        # Канал не найден - возможно, удалён
        print(f"❌ Канал с ID {activity_check_channel_id} не найден!")
        return

    member_count = channel.guild.member_count
    next_ppl = get_next_ppl_range(member_count)
    current_day = get_current_day()

    # Формируем сообщение с номером дня
    message_content = (
        f"# activity check\n"
        f"### DAY {current_day}\n"
        f"@everyone @here \n"
        f"NEXT {next_ppl} PPL \n\n"
        f"### ADD REACTIONS ✅"
    )
    sent_message = await channel.send(message_content)
    await sent_message.add_reaction("✅")
    print(f"[{datetime.now()}] Отправлено | День: {current_day} | NEXT: {next_ppl} PPL")


async def schedule_daily_check():
    while True:
        try:
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            random_hour = random.randint(10, 16)
            random_minute = random.randint(0, 59)
            next_run = datetime(tomorrow.year, tomorrow.month, tomorrow.day, random_hour, random_minute, 0)
            wait_seconds = (next_run - now).total_seconds()
            if wait_seconds < 0:
                wait_seconds += 86400
            print(f"⏰ Следующая проверка: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            await asyncio.sleep(wait_seconds)
            await send_activity_check()
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(3600)
            

@bot.tree.command(name="setactivitycheck", description="Установить канал для активности check")
@app_commands.describe(channel="Канал для уведомлений")
async def setactivitycheck(interaction: discord.Interaction, channel: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    global activity_check_channel_id
    activity_check_channel_id = channel.id
    save_activity_channel(channel.id)  # Сохраняем в файл

    embed = discord.Embed(
        title="✅ Канал установлен",
        description=f"Проверки активности будут отправляться в {channel.mention}",
        color=discord.Color.green()
    )
    embed.add_field(name="⏰ Время", value="Каждый день в случайное время (10:00-17:00)", inline=False)
    embed.add_field(name="📊 Формула", value="1-9→10 | 10-19→20 | 100-109→110 | 110-119→120", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="checknow", description="Отправить проверку активности сейчас (вручную)")
async def checknow(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    global activity_check_channel_id

    # Пробуем загрузить из файла если переменная пустая
    if activity_check_channel_id is None:
        activity_check_channel_id = load_activity_channel()

    if activity_check_channel_id is None:
        await interaction.response.send_message("❌ Сначала установите канал через `/setactivitycheck`", ephemeral=True)
        return

    await interaction.response.send_message("✅ Отправляю проверку активности...", ephemeral=True)
    await send_activity_check()


BLACKLIST_USERS = [1290322870290878539]


async def check_blacklist(obj):
    """Проверяет, находится ли пользователь в чёрном списке"""
    user_id = obj.user.id if hasattr(obj, 'user') else obj.author.id
    response = obj.response if hasattr(obj, 'response') else obj

    if user_id in BLACKLIST_USERS:
        embed = discord.Embed(
            title="⛔ ДОСТУП ЗАПРЕЩЁН",
            description="**Вы находитесь в чёрном списке бота.**\nОбратитесь к администратору для разблокировки.",
            	color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text="bariier Bot • Блокировка")
        await response.send_message(embed=embed, ephemeral=True)
        return True
    return False

LANG_SETTINGS_FILE = 'lang_settings.json'


# =====================================================
# 📋 ФУНКЦИЯ ДЛЯ ЛОГОВ МОДЕРАЦИИ
# =====================================================
async def send_mod_log(guild_id, action, moderator, target, reason, rule=None, duration=None):
    """Отправляет лог модерации в канал логов"""
    cid = load(LOGS_SETTINGS_FILE).get(str(guild_id))
    if not cid:
        return
    channel = bot.get_channel(cid)
    if not channel:
        return

    embed = discord.Embed(
        title=f"🛡️ Действие модерации | {action}",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="👮 Модератор", value=moderator.mention, inline=True)
    embed.add_field(name="👤 Нарушитель", value=target.mention, inline=True)
    embed.add_field(name="🆔 ID нарушителя", value=target.id, inline=True)

    if rule:
        embed.add_field(name="📋 Правило", value=rule, inline=False)
    if reason:
        embed.add_field(name="📝 Причина", value=reason, inline=False)
    if duration:
        embed.add_field(name="⏰ Длительность", value=duration, inline=False)

    embed.set_footer(text=f"Модератор ID: {moderator.id}")
    await channel.send(embed=embed)


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
            'hello_title': '✨ Приветствие',
            'hello_footer': 'bariier Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Задержка:** `{} ms`\n**Статус:** {}',
            'ping_good': '🟢 Отлично',
            'ping_medium': '🟡 Средне',
            'ping_bad': '🔴 Плохо',
            'ping_footer': 'bariier Bot | 🌐 Статус сети',
            'lang_changed_title': '🌐 Язык изменён',
            'lang_changed_footer': 'bariier Bot | Настройки',
            'lang_ru_desc': 'Изменить язык на русский',
            'lang_en_desc': 'Change language to English',
            'lang_es_desc': 'Cambiar idioma a español',
            'authors_title': '👑 bariier Bot | Авторы и разработчики',
            'authors_desc': 'Вот команда, которая сделала этого бота возможным!',
            'authors_ceo': '👑 CEO / Founder',
            'authors_ceo_value': '**Forever**\nГлавный разработчик и идейный вдохновитель',
            'authors_moderators': '🛠️ Moderators',
            'authors_moderators_value': '**D1koot** - Модератор и разработчик\n**Andy.wirus** - Модератор и тестировщик🎉<t:1781388000:s>',
            'authors_coder': '💻 Coder',
            'authors_coder_value': '**D1koot** - Основной разработчик кода',
            'authors_support': '🎧 Support Team',
            'authors_support_value': '**Artem2012rtgf** - Помощь пользователям\n**Майк** - Тестер, Помощь пользователям',
            'authors_thanks': '📢 Благодарности',
            'authors_thanks_value': 'Спасибо всем, кто помогал в тестировании и развитии бота!\nБот создан для вашего удобства и безопасности.',
            'authors_footer': 'bariier Bot • Уважение разработчикам',
            'lang_fr_desc': 'Changer la langue en français',
            'lang_footer': 'bariier Bot • 🔒 Требуются права администратора',
            'serverinfo_footer': 'ID сервера: {} • bariier Bot',
            'userinfo_footer': 'bariier Bot | Информация',
            'avatar_footer': 'bariier Bot | Аватар пользователя',
            'membercount_footer': 'bariier Bot | Статистика',
            'calc_title': '🧮 Калькулятор',
            'calc_footer': 'bariier Bot | Утилиты',
            'poll_title': '📊 Голосование: {}',
            'poll_footer': 'bariier Bot | Голосование активно',
            'poll_created': '✅ Голосование создано',
            'afk_title': '💤 AFK режим',
            'afk_footer': 'bariier Bot | AFK',
            'reminder_title': '⏰ Напоминание установлено',
            'reminder_footer': 'bariier Bot | Напоминание',
            'timestamp_title': '🕐 Текущий timestamp',
            'timestamp_footer': 'bariier Bot | Утилиты',
            'color_title': '🎨 Информация о цвете {}',
            'color_footer': 'bariier Bot | Информация о цвете',
            'qr_title': '📱 QR Код',
            'qr_footer': 'bariier Bot | QR Генератор',
            'uptime_title': '🕐 Время работы бота',
            'uptime_footer': 'bariier Bot | Статистика',
            'giveaway_title': '🎁 Розыгрыш',
            'giveaway_footer': 'bariier Bot | Удачи!',
            'giveaway_prize': '🏆 Приз: {}',
            'giveaway_winners': '👑 Победителей: {}',
            'giveaway_duration': '⏰ Длительность: {}',
            'cat_title': '🐱 Случайный котик',
            'cat_footer': 'bariier Bot | Котики',
            'roll_title': '🎲 Бросок кубика',
            'roll_footer': 'bariier Bot | Игры',
            'eightball_title': '🎱 Магический шар',
            'eightball_question': '❓ Вопрос',
            'autorole_no_permission': '⛔ Нет прав',
            'autorole_admin_only': 'Только администраторы могут использовать эту команду!',
            'autorole_access_denied': 'bariier Bot | Доступ запрещён',
            'autorole_error_no_role': '❌ Ошибка',
            'autorole_error_no_role_desc': 'Укажите роль для выдачи!\nПример: `/autorole on @Роль`',
            'autorole_warning': '⚠️ Внимание',
            'autorole_no_admin_role': 'Нельзя автоматически выдавать администраторскую роль!',
            'autorole_error_role_higher': '⚠️ Ошибка',
            'autorole_role_higher_desc': 'Роль {} выше или равна моей роли!\nПереместите мою роль выше в списке.',
            'autorole_enabled': '✅ Авто-роль включена',
            'autorole_enabled_desc': 'Новые участники будут автоматически получать роль {}',
            'autorole_setup_by': 'Настроил: {}',
            'autorole_disabled': '⚙️ Авто-роль выключена',
            'autorole_disabled_desc': 'Новые участники больше не будут получать роль автоматически.',
            'autorole_info': 'ℹ️ Информация',
            'autorole_not_configured': 'Авто-роль и так не была настроена.',
            'autorole_status_title': '📊 Статус авто-роли',
            'autorole_status_enabled': '✅ **Включена**\n\nВыдаваемая роль: {}\nID роли: `{}`',
            'autorole_status_enabled_no_role': '⚠️ **Включена, но роль не найдена!**\nВозможно, роль была удалена.\nИспользуйте `/autorole off` чтобы выключить.',
            'autorole_status_disabled': '⚫ **Выключена**\n\nИспользуйте `/autorole on @Роль` чтобы включить.',
            'autorole_footer': 'bariier Bot | Авто-роль',
            'eightball_footer': 'bariier Bot | Предсказания',
            'joke_title': '😂 Шутка',
            'joke_footer': 'bariier Bot | Юмор',
            'fact_title': '📖 Случайный факт',
            'fact_footer': 'bariier Bot | Интересно',
            'advice_title': '💡 Совет',
            'advice_footer': 'bariier Bot | Мудрость',
            'quote_title': '📝 Цитата',
            'quote_footer': 'bariier Bot | Вдохновение',
            'trivia_title': '❓ Викторина',
            'trivia_footer': 'bariier Bot | Викторины',
            'rps_title': '✊ Камень, ножницы, бумага',
            'rps_footer': 'bariier Bot | Игры',
            'rps_choice': 'Вы выбрали **{}**, я выбрал **{}**.',
            'flip_title': '🪙 Монетка',
            'flip_footer': 'bariier Bot | Игры',
            'flip_result': 'Выпал **{}**!',
            'setup_logs_title': '📋 Настройка логов',
            'setup_logs_footer': 'bariier Bot | Логирование',
            'setup_welcome_title': '👋 Настройка приветствий',
            'setup_welcome_footer': 'bariier Bot | Приветствия',
            'setup_photowelcome_title': '🖼️ Настройка фото-приветствий',
            'setup_photowelcome_footer': 'bariier Bot | Приветствия с фото',
            'disable_welcome_title': '⚠️ Отключение приветствий',
            'disable_welcome_footer': 'bariier Bot | Приветствия отключены',
            'setup_captcha_title': '🔐 Настройка капчи',
            'setup_captcha_footer': 'bariier Bot | Безопасность',
            'disable_captcha_title': '🔐 Отключение капчи',
            'disable_captcha_footer': 'bariier Bot | Капча отключена',
            'invite_title': '🔗 Пригласить',
            'invite_desc': 'Спасибо за приглашение на свой сервер!',
            'invite_footer': 'bariier Bot | Приглашения',
            'invite_button': '🤖 Пригласить бота',
            'server_button': '🌐 Сервер поддержки',
            'send_dm_title': '📨 Сообщение отправлено',
            'send_dm_success': '✅ Сообщение успешно отправлено пользователю {} (ID: {})',
            'send_dm_text': '📝 Текст сообщения',
            'send_dm_footer': 'bariier Bot | Разработка',
            'servers_title': '📊 Список серверов с ботом',
            'servers_footer': 'Всего серверов: {} • bariier Bot',
            'servers_id': '🆔 ID: `{}`',
            'servers_owner': '👑 Владелец: {}',
            'servers_members': '👥 Участников: {}',
            'servers_your': '🔴 **ВАШ**',
            'regex_title_on': '🛡️ Автомодерация',
            'regex_desc_on': '✅ Система **ВКЛЮЧЕНА**\n\n**📝 За маты:** Мут на 1 час ({} слов)\n**🔨 За рекламу/оскорбление сервера:** Перманентный бан ({} фраз)',
            'regex_title_off': '🛡️ Автомодерация',
            'regex_desc_off': '⚫ Система **ВЫКЛЮЧЕНА**',
            'regex_title_status': '🛡️ Статус автомодерации',
            'regex_desc_status': '{}\n\n**📝 Маты:** Мут на 1 час ({} слов)\n**🔨 Оскорбление сервера:** Перманентный бан ({} фраз)',
            'regex_status_enabled': '🔴 **ВКЛЮЧЕНА**',
            'regex_status_disabled': '⚫ **ВЫКЛЮЧЕНА**',
            'regex_footer': 'bariier Bot | Защита',
            'blacklist_title': '⛔ ДОСТУП ЗАПРЕЩЁН',
            'blacklist_desc': '**Вы находитесь в чёрном списке бота.**\nОбратитесь к администратору для разблокировки.',
            'blacklist_footer': 'bariier Bot • Блокировка',
            'massunban_title': '🔓 Массовый разбан',
            'massunban_success': '✅ Успешно разбанены',
            'massunban_list': '📋 Список разбаненных',
            'massunban_errors': '❌ Ошибки',
            'massunban_start': '🔄 Начинаю разбан **{}** пользователей...',
            'massunban_none': '❌ На сервере нет забаненных пользователей!',
            'massunban_footer': 'Запросил: {} • bariier Bot',
            'member_join_log': '🚪 Member joined',
            'member_remove_log': '🚪 Member left',
            'message_delete_log': '🗑️ Message deleted',
            'message_edit_log': '✏️ Message edited',
            'log_footer': 'bariier Bot | Логи',
            'hello': 'Привет, {}! Я **bariier Bot** 🤖',
            'ping': '🏓 Понг! Задержка: {} мс',
            'help_title': '📚 Помощь - {}',
            'help_desc': 'Выбери категорию в меню ниже, чтобы увидеть список команд.\nИли используй `/help all` для полного списка.',
            'help_cmd_count': '{} команд',
            'help_footer': 'А вы знали что всего 100 команд? :3',
            'help_all_title': '📖 Все команды',
            'help_all_desc': 'Полный список всех команд бота:',
            'help_category_title': '{} - Список команд',
            'help_category_desc': 'Всего команд в категории: {}',
            'help_select_placeholder': '📋 Выбери категорию...',
            'help_select_overview': '📚 Обзор',
            'help_select_overview_desc': 'Вернуться к началу',
            'help_select_all': '📖 Все команды',
            'help_select_all_desc': 'Показать все 100 команд',
            'help_select_mod_desc': '28 команд',
            'help_select_roles_desc': '8 команд',
            'help_select_voice_desc': '5 команд',
            'help_select_info_desc': '9 команд',
            'help_select_level_desc': '6 команд',
            'help_select_util_desc': '10 команд',
            'help_select_fun_desc': '10 команд',
            'help_select_setup_desc': '13 команд',
            'help_select_misc_desc': '2 команды',
            'info_title': '🛡️ bariier Bot',
            'info_desc': 'Бот-хранитель для твоего сервера',
            'info_version': 'Версия',
            'info_cmds': 'Команды',
            'info_footer': 'Всегда поддерживает порядок 🔒',
            'no_permission': '❌ Нет прав!',
            'need_admin': '❌ Нужны права администратора!',
            'error': '❌ Ошибка: {}',
            'sent': '✅ Отправлено в {}',
            'no_roles': '❌ Роли не указаны!',
            'settings_saved': '✅ Настройки сохранены'
        },
        'es': {
            'hello': '¡Hola, {}! Soy **bariier Bot** 🤖',
            'ping': '🏓 Pong! Latencia: {} ms',
            'help_title': '📚 Ayuda - {}',
            'help_desc': 'Selecciona una categoría en el menú para ver la lista de comandos.\nO usa `/help all` para la lista completa.',
            'help_cmd_count': '{} comandos',
            'help_footer': '¿Sabías que solo hay 100 comandos? :3',
            'help_all_title': '📖 Todos los comandos',
            'help_all_desc': 'Lista completa de todos los comandos del bot:',
            'help_category_title': '{} - Lista de comandos',
            'autorole_no_permission': '⛔ Sin permiso',
            'autorole_admin_only': '¡Solo los administradores pueden usar este comando!',
            'autorole_access_denied': 'bariier Bot | Acceso denegado',
            'autorole_error_no_role': '❌ Error',
            'autorole_error_no_role_desc': '¡Especifica un rol para asignar!\nEjemplo: `/autorole on @Rol`',
            'autorole_warning': '⚠️ Advertencia',
            'autorole_no_admin_role': '¡No se puede asignar automáticamente el rol de administrador!',
            'autorole_error_role_higher': '⚠️ Error',
            'autorole_role_higher_desc': '¡El rol {} es superior o igual a mi rol!\nMueve mi rol más arriba en la lista.',
            'autorole_enabled': '✅ Autorol activado',
            'autorole_enabled_desc': 'Los nuevos miembros recibirán automáticamente el rol {}',
            'autorole_setup_by': 'Configurado por: {}',
            'autorole_disabled': '⚙️ Autorol desactivado',
            'autorole_disabled_desc': 'Los nuevos miembros ya no recibirán roles automáticamente.',
            'autorole_info': 'ℹ️ Información',
            'autorole_not_configured': 'El autorol no estaba configurado.',
            'autorole_status_title': '📊 Estado del Autorol',
            'autorole_status_enabled': '✅ **Activado**\n\nRol asignado: {}\nID del rol: `{}`',
            'autorole_status_enabled_no_role': '⚠️ **Activado, pero rol no encontrado!**\nEl rol puede haber sido eliminado.\nUsa `/autorole off` para desactivar.',
            'autorole_status_disabled': '⚫ **Desactivado**\n\nUsa `/autorole on @Rol` para activar.',
            'autorole_footer': 'bariier Bot | Autorol',
            'help_category_desc': 'Total de comandos en categoría: {}',
            'help_select_placeholder': '📋 Elige una categoría...',
            'help_select_overview': '📚 Descripción general',
            'help_select_overview_desc': 'Volver al principio',
            'help_select_all': '📖 Todos los comandos',
            'help_select_all_desc': 'Mostrar los 100 comandos',
            'help_select_mod_desc': '28 comandos',
            'help_select_roles_desc': '8 comandos',
            'help_select_voice_desc': '5 comandos',
            'help_select_info_desc': '9 comandos',
            'help_select_level_desc': '6 comandos',
            'help_select_util_desc': '10 comandos',
            'help_select_fun_desc': '10 comandos',
            'help_select_setup_desc': '13 comandos',
            'help_select_misc_desc': '2 comandos',
            'info_title': '🛡️ bariier Bot',
            'info_desc': 'El bot guardián para tu servidor',
            'info_version': 'Versión',
            'info_cmds': 'Comandos',
            'info_footer': 'Siempre manteniendo el orden 🔒',
            'no_permission': '❌ ¡Sin permisos!',
            'need_admin': '❌ ¡Necesitas permisos de administrador!',
            'error': '❌ Error: {}',
            'sent': '✅ Enviado a {}',
            'no_roles': '❌ ¡No se especificaron roles!',
            'settings_saved': '✅ Configuración guardada',
            'log_channel_set': '✅ Canal de registros: {}',
            'invite_title': '🔗 Invitar',
            'invite_desc': '¡Gracias por invitarme a tu servidor!',
            'invite_button': '🤖 Invitar Bot',
            'server_button': '🌐 Servidor de Soporte',
            'invite_footer': 'bariier Bot | Invitaciones',
            'tech_work_title': '🛠️ Mantenimiento',
            'tech_work_desc': 'El bot no está disponible temporalmente.',
            'tech_work_enabled': '🛠️ Modo mantenimiento ACTIVADO',
            'tech_work_disabled': '✅ Modo mantenimiento DESACTIVADO',
            'tech_work_status': '🛠️ Estado del mantenimiento: **{status}**',
            'no_tech_permission': '❌ ¡No tienes permiso para usar este comando!',
            'use_on_off_status': '❌ Usa: `on`, `off`, `status`',
            'muted': '🔇 {} silenciado por {}',
            'invalid_time': '❌ Ingresa un número positivo de minutos (ej: 30)',
            'not_muted': '❌ ¡No está silenciado!',
            'unmuted': '✅ {} ya no está silenciado',
            'kicked': '✅ {} expulsado',
            'banned': '✅ {} baneado',
            'user_not_found': '❌ ¡Usuario {} no encontrado!',
            'unbanned': '✅ {} desbaneado',
            'cleared': '✅ {} mensajes eliminados',
            'clear': '✅ {} mensajes eliminados',
            'clear_range': '❌ ¡Solo 1-100 mensajes!',
            'delwarn': '✅ Advertencia #{} eliminada',
            'warned': '⚠️ {} recibió advertencia #{}',
            'warn_reason': 'Razón',
            'warn_total': 'Total',
            'no_warnings': '{} no tiene advertencias',
            'warnings_title': '⚠️ Advertencias de {}',
            'warnings_total': 'Total: {}',
            'warn_removed': '✅ Advertencia #{} eliminada',
            'warn_not_found': '❌ ¡Advertencia #{} no encontrada!',
            'topwarnings_desc': '🏆 Top advertencias',
            'slowmode': '✅ Modo lento {}s en {}',
            'locked': '🔒 {} bloqueado',
            'unlocked': '🔓 {} desbloqueado',
            'reset': '✅ {} reiniciado',
            'report_sent': '✅ Reporte enviado',
            'pinned': '📌 Fijado',
            'unpinned': '📌 Desfijado',
            'msg_not_found': '❌ Mensaje no encontrado',
            'antinuke_configured': '✅ ¡Antinuke configurado!',
            'setupantinuke_desc': '🛡️ Protección antinuke activada',
            'timeout_set': '⏰ {} tiempo muerto por {} min',
            'timeout_removed': '✅ {} tiempo muerto eliminado',
            'softbanned': '✅ {} softbaneado',
            'massbanned': '✅ {} usuarios baneados',
            'bot_messages_deleted': '✅ {} mensajes del bot eliminados',
            'strike_given': '⚠️ {} strike #{}',
            'strike_removed': '✅ Strike #{} eliminado de {}',
            'no_strikes': '✅ {} no tiene strikes',
            'strike_not_found': '❌ Strike #{} no encontrado',
            'strikes_title': '⚠️ Strikes de {}',
            'topstrikes_title': '🏆 Top strikes',
            'nickname_set': '✅ Apodo de {} cambiado a {}',
            'role_added': '✅ Rol {} añadido a {}',
            'role_removed': '✅ Rol {} eliminado de {}',
            'role_created': '✅ Rol {} creado',
            'role_deleted': '✅ Rol eliminado',
            'reaction_role_set': '✅ Reacción {} → {}',
            'channel_created': '✅ Canal #{} creado',
            'channel_deleted': '✅ Canal eliminado',
            'channel_cloned': '✅ Canal #{} clonado',
            'channel_moved': '✅ Canal #{} movido a posición {}',
            'voice_muted': '🔇 {} silenciado en canal de voz',
            'voice_unmuted': '🔊 {} ya no está silenciado en voz',
            'voice_deafened': '🔇 {} ensordecido',
            'voice_undeafened': '🔊 {} ya no está ensordecido',
            'voice_moved': '✅ {} movido a {}',
            'voice_kicked': '🎤 {} expulsado del canal de voz',
            'vkick_desc': '🎤 {} expulsado del canal de voz',
            'vmove_desc': '🔊 {} movido a {}',
            'not_in_voice': '❌ ¡No está en un canal de voz!',
            'serverinfo_owner': 'Propietario',
            'serverinfo_members': 'Miembros',
            'serverinfo_channels': 'Canales',
            'serverinfo_roles': 'Roles',
            'serverinfo_title': '📊 Información del servidor | {}',
            'serverinfo_footer': 'ID del servidor: {} • bariier Bot',
            'userinfo_title': 'Información de {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'Se unió',
            'userinfo_created': 'Creado',
            'userinfo_bot': 'Bot',
            'userinfo_roles_header': 'Roles',
            'userinfo_footer': 'bariier Bot | Información',
            'avatar_title': 'Avatar de {}',
            'avatar_title_full': 'Avatar de {}',
            'avatar_footer': 'bariier Bot | Avatar de usuario',
            'membercount_total': 'Total',
            'membercount_humans': 'Humanos',
            'membercount_bots': 'Bots',
            'membercount_title': '📊 Estadísticas de miembros',
            'membercount_footer': 'bariier Bot | Estadísticas',
            'admins_list': '👑 Administradores',
            'admins_title': '👑 Administradores del servidor',
            'admins_footer': 'bariier Bot | Administración',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots en el servidor',
            'bots_footer': 'bariier Bot | Bots',
            'none': 'Ninguno',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Expresión inválida',
            'calc_title': '🧮 Calculadora',
            'calc_footer': 'bariier Bot | Utilidades',
            'reminder_set': '✅ Recordatorio en {}',
            'reminder_invalid': '❌ Usa: 10s, 5m, 1h, 1d',
            'reminder_title': '⏰ Recordatorio Establecido',
            'reminder_footer': 'bariier Bot | Recordatorio',
            'uptime_text': '🕐 Tiempo activo: {}d {}h {}m',
            'uptime_title': '🕐 Tiempo de Actividad',
            'uptime_footer': 'bariier Bot | Estadísticas',
            'poll_created': '✅ ¡Encuesta creada!',
            'poll_voted': '✅ ¡Votado!',
            'poll_total': 'Total de votos: {}',
            'poll_title': '📊 Encuesta: {}',
            'poll_option': '{} votos',
            'poll_footer': 'bariier Bot | Encuesta activa',
            'announce_sent': '✅ Enviado a {}',
            'lang_title': '🌐 Selección de idioma',
            'lang_desc': 'Haz clic en el botón para seleccionar el idioma',
            'lang_changed_ru': '🌐 Idioma cambiado a **Ruso**! Comandos actualizados.',
            'lang_changed_en': '🌐 Language changed to **English**! Commands updated.',
            'lang_changed_es': '🌐 Idioma cambiado a **Español**! Comandos actualizados.',
            'lang_changed_fr': '🌐 Idioma cambiado a **Francés**! Comandos actualizados.',
            'lang_es': '🇪🇸 Español',
            'lang_fr': '🇫🇷 Francés',
            'lang_changed_title': '🌐 Idioma Cambiado',
            'lang_changed_footer': 'bariier Bot | Ajustes',
            'lang_ru_desc': 'Cambiar idioma a ruso',
            'lang_en_desc': 'Cambiar idioma a inglés',
            'lang_es_desc': 'Cambiar idioma a español',
            'lang_fr_desc': 'Cambiar idioma a francés',
            'lang_select_placeholder': '🌐 Selecciona idioma',
            'lang_current': '**Idioma actual:** {}',
            'lang_admin_only': '**¡Solo para administradores!**',
            'lang_select_menu': 'Selecciona un idioma del menú.',
            'lang_footer': 'bariier Bot • 🔒 Solo administradores',
            'promotion_level': '📊 Tu nivel: {} | XP: {}',
            'leaderboard_title': '🏆 Tabla de clasificación',
            'xp_added': '✅ {} XP añadidos a {}',
            'xp_set': '✅ {} XP establecidos para {}',
            'level_set': '✅ Nivel {} establecido para {}',
            'afk_set': '✅ {} ahora está AFK: {}',
            'afk_removed': '✅ AFK eliminado',
            'not_afk': '❌ No estás AFK',
            'afk_title': '💤 Modo AFK',
            'afk_footer': 'bariier Bot | AFK',
            'timestamp_current': '🕐 Marca de tiempo actual: {}',
            'timestamp_title': '🕐 Marca de Tiempo Actual',
            'timestamp_footer': 'bariier Bot | Utilidades',
            'color_info': '🎨 Información del color {}',
            'color_title': '🎨 Información del color {}',
            'color_footer': 'bariier Bot | Información de color',
            'qr_code_title': '📱 Código QR',
            'qr_title': '📱 Código QR',
            'qr_footer': 'bariier Bot | Generador QR',
            'giveaway_started': '🎁 ¡Sorteo iniciado!',
            'giveaway_title': '🎁 Sorteo',
            'giveaway_prize': '🏆 Premio: {}',
            'giveaway_winners': '👑 Ganadores: {}',
            'giveaway_duration': '⏰ Duración: {}',
            'giveaway_footer': 'bariier Bot | ¡Buena suerte!',
            'cat_title': '🐱 Gato Aleatorio',
            'cat_title_full': '🐱 Gato aleatorio',
            'cat_footer': 'bariier Bot | Gatos',
            'roll_result': '🎲 Tiraste {} (1-{})',
            'roll_title': '🎲 Lanzamiento de Dado',
            'roll_footer': 'bariier Bot | Juegos',
            'eightball_result': '🎱 {}',
            'eightball_title': '🎱 Bola Mágica',
            'eightball_title_full': '🎱 Bola mágica',
            'eightball_question': '❓ Pregunta',
            'eightball_footer': 'bariier Bot | Predicciones',
            'joke_title': '😂 Chiste',
            'joke_title_full': '😂 Chiste',
            'joke_footer': 'bariier Bot | Humor',
            'fact_title': '📖 Dato Aleatorio',
            'fact_title_full': '📖 Dato aleatorio',
            'fact_footer': 'bariier Bot | Interesante',
            'advice_title': '💡 Consejo',
            'advice_title_full': '💡 Consejo',
            'advice_footer': 'bariier Bot | Sabiduría',
            'quote_title': '📝 Cita',
            'quote_title_full': '📝 Cita',
            'quote_footer': 'bariier Bot | Inspiración',
            'trivia_question': '❓ {} (Dificultad: {})',
            'trivia_title': '❓ Trivia',
            'trivia_footer': 'bariier Bot | Trivia',
            'rps_win': '¡Ganaste!',
            'rps_lose': '¡Gané!',
            'rps_tie': '¡Empate!',
            'rps_title': '✊ Piedra, Papel, Tijera',
            'rps_choice': 'Elegiste **{}**, yo elegí **{}**.',
            'rps_footer': 'bariier Bot | Juegos',
            'flip_heads': 'Cara',
            'flip_tails': 'Cruz',
            'flip_title': '🪙 Lanzamiento de Moneda',
            'flip_result': '¡Salió **{}**!',
            'flip_footer': 'bariier Bot | Juegos',
            'welcome_configured': '✅ Bienvenidas configuradas en {}',
            'welcome_disabled': '✅ Bienvenidas desactivadas',
            'photo_welcome_configured': '✅ ¡Bienvenida con foto configurada!',
            'setup_logs_title': '📋 Configuración de Registros',
            'setup_logs_footer': 'bariier Bot | Registros',
            'setup_welcome_title': '👋 Configuración de Bienvenidas',
            'setup_welcome_footer': 'bariier Bot | Bienvenidas',
            'setup_photowelcome_title': '🖼️ Configuración de Bienvenida con Foto',
            'setup_photowelcome_footer': 'bariier Bot | Bienvenidas con Foto',
            'disable_welcome_title': '⚠️ Desactivar Bienvenidas',
            'disable_welcome_footer': 'bariier Bot | Bienvenidas Desactivadas',
            'captcha_configured': '✅ Captcha configurado con rol {}',
            'captcha_disabled': '✅ Captcha desactivado',
            'setup_captcha_title': '🔐 Configuración de Captcha',
            'setup_captcha_footer': 'bariier Bot | Seguridad',
            'disable_captcha_title': '🔐 Desactivar Captcha',
            'disable_captcha_footer': 'bariier Bot | Captcha Desactivado',
            'ticket_setup_success': '✅ ¡Sistema configurado!',
            'ticket_setup_info': 'Tipo: **{}**\nCategoría: {}\nRol: {}',
            'ticket_created': '✅ Ticket creado: {}',
            'ticket_no_permission': '❌ ¡Sin permisos!',
            'ticket_closing': '🔒 Cerrando ticket...',
            'ticket_closed_user': '✅ Tu ticket **{}** ha sido cerrado.',
            'ticket_accepted': '✅ ¡Ticket aceptado para trabajo!',
            'ticket_accepted_user': '✅ Tu ticket **{}** ha sido aceptado por {}',
            'ticket_rejected': '❌ ¡Ticket rechazado!',
            'ticket_rejected_user': '❌ Tu ticket **{}** ha sido rechazado.',
            'ticket_reply_sent': '✅ ¡Respuesta enviada!',
            'ticket_reply_user': '📩 Respuesta a tu ticket **{}** de {}:\n\n{}',
            'ticket_status_pending': '⏳ Pendiente',
            'ticket_status_accepted': '✅ ACEPTADO',
            'ticket_status_rejected': '❌ RECHAZADO',
            'ticket_status_answered': '✅ RESPONDIDO',
            'ticket_support_title': '🎫 Sistema de tickets',
            'ticket_support_desc': 'Haz clic en el botón para crear un ticket.\nNuestro personal te contactará pronto.',
            'ticket_bug_title': '🐛 Sistema de reporte de errores',
            'ticket_bug_desc': '¿Encontraste un error? Haz clic en el botón para reportarlo a los desarrolladores.\n\n**¡Gracias por ayudar a mejorar el bot!**',
            'ticket_idea_title': '💡 Ideas para el bot',
            'ticket_idea_desc': '¿Tienes una idea para mejorar el bot? ¡Haz clic en el botón y compártela!\n\n**¡Las mejores ideas serán implementadas!**',
            'ticket_report_title': '⚠️ Reportes de personal',
            'ticket_report_desc': 'Haz clic en el botón para reportar a un miembro del personal.\n\n**¡Los reportes falsos serán castigados!**',
            'ticket_partnership_title': '🤝 Colaboración',
            'ticket_partnership_desc': 'Haz clic en el botón para proponer colaboración, publicidad o eventos conjuntos.',
            'ticket_modal_support_title': '🎫 Crear ticket',
            'ticket_modal_support_topic': 'Asunto',
            'ticket_modal_support_description': 'Descripción',
            'ticket_modal_bug_title': '🐛 Reporte de error',
            'ticket_modal_bug_summary': 'Resumen',
            'ticket_modal_bug_details': 'Descripción detallada',
            'ticket_modal_bug_steps': 'Pasos para reproducir',
            'ticket_modal_idea_title': '💡 Idea para el bot',
            'ticket_modal_idea_name': 'Título de la idea',
            'ticket_modal_idea_description': 'Descripción',
            'ticket_modal_idea_benefit': '¿Por qué es útil?',
            'ticket_modal_report_title': '⚠️ Reporte de personal',
            'ticket_modal_report_against': '¿A quién reportas?',
            'ticket_modal_report_reason': 'Razón',
            'ticket_modal_report_proof': 'Evidencia',
            'ticket_modal_partnership_title': '🤝 Colaboración',
            'ticket_modal_partnership_name': 'Nombre del proyecto',
            'ticket_modal_partnership_type': 'Tipo de colaboración',
            'ticket_modal_partnership_description': 'Descripción',
            'ticket_modal_partnership_contacts': 'Contactos',
            'ticket_embed_new': '🆕 NUEVO TICKET',
            'ticket_embed_topic': '📌 Asunto',
            'ticket_embed_question': '📝 Descripción',
            'ticket_button_close': '🔒 Cerrar',
            'ticket_button_accept': '✅ Aceptar',
            'ticket_button_reject': '❌ Rechazar',
            'ticket_button_reply': '✏️ Responder',
            'ticket_reply_modal_title': '📝 Responder al usuario',
            'ticket_reply_modal_label': 'Mensaje',
            'application_created': '✅ ¡Solicitud creada! Botón enviado al canal.',
            'application_no_questions': '❌ ¡Añade al menos 1 pregunta!',
            'application_question_added': '✅ ¡Pregunta añadida! (Total: {})',
            'application_button_label': '📝 Solicitar: {}',
            'application_embed_title': '📝 {}',
            'application_embed_desc': 'Haz clic en el botón para solicitar.\nDespués de la revisión recibirás el rol {}',
            'application_creation_title': '📝 Crear solicitud',
            'application_creation_desc': '**Nombre:** {}\n**Rol:** {}\n**Canal de envío:** {}\n\nHaz clic en los botones para añadir preguntas.',
            'application_add_question_button': '➕ Añadir pregunta',
            'application_finish_button': '✅ Finalizar creación',
            'application_submit_button': '📝 Solicitar: {}',
            'application_modal_title': '📝 {}',
            'application_submitted': '✅ ¡Solicitud enviada! Espera una decisión.',
            'application_new_title': '📥 Nueva solicitud: {}',
            'application_new_desc': '**De:** {}\n**ID:** {}\n**Estado:** ⏳ Pendiente de revisión',
            'application_question_field': '❓ Pregunta {}',
            'application_footer': 'ID de solicitud: {}',
            'application_approve_button': '✅ Aprobar',
            'application_reject_button': '❌ Rechazar',
            'application_approve_msg_button': '✏️ Aprobar con mensaje',
            'application_reject_msg_button': '📝 Rechazar con mensaje',
            'application_approved': '✅ ¡Solicitud aprobada! {} recibió el rol {}',
            'application_approved_simple': '✅ ¡Solicitud aprobada!',
            'application_rejected': '❌ ¡Solicitud rechazada!',
            'application_approved_with_msg': '✅ ¡Solicitud aprobada con mensaje!',
            'application_rejected_with_msg': '❌ ¡Solicitud rechazada con mensaje!',
            'application_status_approved': '✅ APROBADA',
            'application_status_rejected': '❌ RECHAZADA',
            'application_status_approved_msg': '✅ APROBADA (con mensaje)',
            'application_status_rejected_msg': '❌ RECHAZADA (con mensaje)',
            'application_reviewed_by': '✅ Revisado por',
            'application_reviewed_by_reject': '❌ Revisado por',
            'application_review_message': '📝 Mensaje',
            'application_reject_reason': '📝 Razón',
            'application_dm_approved': '✅ Tu solicitud **{}** ha sido **APROBADA**! Recibiste el rol {}',
            'application_dm_rejected': '❌ Tu solicitud **{}** ha sido **RECHAZADA**.',
            'application_dm_approved_msg': '✅ Tu solicitud **{}** ha sido **APROBADA**! Recibiste el rol {}\n\n**Mensaje de la administración:**\n{}',
            'application_dm_rejected_msg': '❌ Tu solicitud **{}** ha sido **RECHAZADA**.\n\n**Razón:**\n{}',
            'application_no_permission': '❌ ¡Sin permisos!',
            'application_approve_modal_title': '✅ Aprobar solicitud con mensaje',
            'application_approve_modal_label': 'Mensaje al usuario',
            'application_approve_modal_placeholder': 'Escribe un mensaje para el usuario...',
            'application_reject_modal_title': '❌ Rechazar solicitud con mensaje',
            'application_reject_modal_label': 'Razón del rechazo',
            'application_reject_modal_placeholder': 'Escribe la razón del rechazo...',
            'application_list_title': '📋 Lista de solicitudes',
            'application_delete_success': '✅ ¡Solicitud #{} eliminada!',
            'application_not_found': '❌ ¡Solicitud no encontrada!',
            'application_no_apps': '❌ ¡No hay solicitudes creadas!',
            'authors_title': '👑 bariier Bot | Autores y Desarrolladores',
            'authors_desc': '¡Este es el equipo que hizo posible este bot!',
            'authors_ceo': '👑 CEO / Fundador',
            'authors_ceo_value': '**Forever**\nDesarrollador principal y visionario',
            'authors_moderators': '🛠️ Moderadores',
            'authors_moderators_value': '**D1koot** - Moderador y Desarrollador\n**Andy.wirus** - Moderador y Probador🎉<t:1781388000:s>',
            'authors_coder': '💻 Programador',
            'authors_coder_value': '**D1koot**\nDesarrollador principal del código',
            'authors_support': '🎧 Equipo de Soporte',
            'authors_support_value': '**K1APMI** - Soporte Técnico\n**Artem2012rtgf** - Ayuda a usuarios\n**Mike** - Probador, Ayuda a usuarios',
            'authors_thanks': '📢 Agradecimientos',
            'authors_thanks_value': '¡Gracias a todos los que ayudaron a probar y desarrollar el bot!\nEl bot fue creado para tu comodidad y seguridad.',
            'authors_footer': 'bariier Bot • Respeto a los desarrolladores',
            'hello_title': '✨ Saludo',
            'hello_footer': 'bariier Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latencia:** `{} ms`\n**Estado:** {}',
            'ping_good': '🟢 Excelente',
            'ping_medium': '🟡 Media',
            'ping_bad': '🔴 Mala',
            'ping_footer': 'bariier Bot | 🌐 Estado de red',
            'blacklist_title': '⛔ ACCESO DENEGADO',
            'blacklist_desc': '**Estás en la lista negra del bot.**\nContacta al administrador para ser desbloqueado.',
            'blacklist_footer': 'bariier Bot • Bloqueado',
            'massunban_title': '🔓 Desbaneo Masivo',
            'massunban_success': '✅ Desbaneados exitosamente',
            'massunban_list': '📋 Lista de desbaneados',
            'massunban_errors': '❌ Errores',
            'massunban_start': '🔄 Comenzando desbaneo de **{}** usuarios...',
            'massunban_none': '❌ ¡No hay usuarios baneados en el servidor!',
            'massunban_footer': 'Solicitado por: {} • bariier Bot',
            'send_dm_title': '📨 Mensaje Enviado',
            'send_dm_success': '✅ Mensaje enviado exitosamente al usuario {} (ID: {})',
            'send_dm_text': '📝 Texto del mensaje',
            'send_dm_footer': 'bariier Bot | Desarrollo',
            'servers_title': '📊 Lista de Servidores con el Bot',
            'servers_footer': 'Total de servidores: {} • bariier Bot',
            'servers_id': '🆔 ID: `{}`',
            'servers_owner': '👑 Propietario: {}',
            'servers_members': '👥 Miembros: {}',
            'servers_your': '🔴 **TUYO**',
            'regex_title_on': '🛡️ Automoderación',
            'regex_desc_on': '✅ Sistema **ACTIVADO**\n\n**📝 Por insultos:** Muto de 1 hora ({} palabras)\n**🔨 Por insulto al servidor/publicidad:** Baneo permanente ({} frases)',
            'regex_title_off': '🛡️ Automoderación',
            'regex_desc_off': '⚫ Sistema **DESACTIVADO**',
            'regex_title_status': '🛡️ Estado de la Automoderación',
            'regex_desc_status': '{}\n\n**📝 Insultos:** Muto de 1 hora ({} palabras)\n**🔨 Insulto al servidor:** Baneo permanente ({} frases)',
            'regex_status_enabled': '🔴 **ACTIVADA**',
            'regex_status_disabled': '⚫ **DESACTIVADA**',
            'regex_footer': 'bariier Bot | Protección',
            'member_join_log': '🚪 Miembro unido',
            'member_remove_log': '🚪 Miembro salió',
            'message_delete_log': '🗑️ Mensaje eliminado',
            'message_edit_log': '✏️ Mensaje editado',
            'log_footer': 'bariier Bot | Registros',
        },
        'fr': {
            'hello': 'Bonjour, {}! Je suis **bariier Bot** 🤖',
            'ping': '🏓 Pong! Latence: {} ms',
            'help_title': '📚 Aide - {}',
            'help_desc': 'Sélectionne une catégorie dans le menu pour voir la liste des commandes.\nOu utilise `/help all` pour la liste complète.',
            'help_cmd_count': '{} commandes',
            'help_footer': 'Saviez-vous qu\'il n\'y a que 100 commandes? :3',
            'help_all_title': '📖 Toutes les commandes',
            'help_all_desc': 'Liste complète de toutes les commandes du bot:',
            'autorole_no_permission': '⛔ Pas de permission',
            'autorole_admin_only': 'Seuls les administrateurs peuvent utiliser cette commande!',
            'autorole_access_denied': 'bariier Bot | Accès refusé',
            'autorole_error_no_role': '❌ Erreur',
            'autorole_error_no_role_desc': 'Spécifiez un rôle à attribuer!\nExemple: `/autorole on @Rôle`',
            'autorole_warning': '⚠️ Attention',
            'autorole_no_admin_role': 'Impossible d\'attribuer automatiquement un rôle d\'administrateur!',
            'autorole_error_role_higher': '⚠️ Erreur',
            'autorole_role_higher_desc': 'Le rôle {} est supérieur ou égal à mon rôle!\nDéplacez mon rôle plus haut dans la liste.',
            'autorole_enabled': '✅ Autorôle activé',
            'autorole_enabled_desc': 'Les nouveaux membres recevront automatiquement le rôle {}',
            'autorole_setup_by': 'Configuré par: {}',
            'autorole_disabled': '⚙️ Autorôle désactivé',
            'autorole_disabled_desc': 'Les nouveaux membres ne recevront plus automatiquement de rôle.',
            'autorole_info': 'ℹ️ Info',
            'autorole_not_configured': 'L\'autorôle n\'était pas configuré.',
            'autorole_status_title': '📊 Statut de l\'Autorôle',
            'autorole_status_enabled': '✅ **Activé**\n\nRôle attribué: {}\nID du rôle: `{}`',
            'autorole_status_enabled_no_role': '⚠️ **Activé, mais rôle introuvable!**\nLe rôle a peut-être été supprimé.\nUtilisez `/autorole off` pour désactiver.',
            'autorole_status_disabled': '⚫ **Désactivé**\n\nUtilisez `/autorole on @Rôle` pour activer.',
            'autorole_footer': 'bariier Bot | Autorôle',
            'help_category_title': '{} - Liste des commandes',
            'help_category_desc': 'Total des commandes dans la catégorie: {}',
            'help_select_placeholder': '📋 Choisis une catégorie...',
            'help_select_overview': '📚 Aperçu',
            'help_select_overview_desc': 'Retour au début',
            'help_select_all': '📖 Toutes les commandes',
            'help_select_all_desc': 'Afficher les 100 commandes',
            'help_select_mod_desc': '28 commandes',
            'help_select_roles_desc': '8 commandes',
            'help_select_voice_desc': '5 commandes',
            'help_select_info_desc': '9 commandes',
            'help_select_level_desc': '6 commandes',
            'help_select_util_desc': '10 commandes',
            'help_select_fun_desc': '10 commandes',
            'help_select_setup_desc': '13 commandes',
            'help_select_misc_desc': '2 commandes',
            'info_title': '🛡️ bariier Bot',
            'info_desc': 'Le bot gardien pour ton serveur',
            'info_version': 'Version',
            'info_cmds': 'Commandes',
            'info_footer': 'Maintient toujours l\'ordre 🔒',
            'no_permission': '❌ Pas de permission!',
            'need_admin': '❌ Besoin des permissions administrateur!',
            'error': '❌ Erreur: {}',
            'sent': '✅ Envoyé à {}',
            'no_roles': '❌ Aucun rôle spécifié!',
            'settings_saved': '✅ Paramètres enregistrés',
            'log_channel_set': '✅ Salon des logs: {}',
            'invite_title': '🔗 Inviter',
            'invite_desc': 'Merci de m\'inviter sur ton serveur!',
            'invite_button': '🤖 Inviter le Bot',
            'server_button': '🌐 Serveur de Support',
            'invite_footer': 'bariier Bot | Invitations',
            'tech_work_title': '🛠️ Maintenance',
            'tech_work_desc': 'Le bot est temporairement indisponible.',
            'tech_work_enabled': '🛠️ Mode maintenance ACTIVÉ',
            'tech_work_disabled': '✅ Mode maintenance DÉSACTIVÉ',
            'tech_work_status': '🛠️ Statut de la maintenance: **{status}**',
            'no_tech_permission': '❌ Vous n\'avez pas la permission d\'utiliser cette commande!',
            'use_on_off_status': '❌ Utilise: `on`, `off`, `status`',
            'muted': '🔇 {} réduit au silence pour {}',
            'invalid_time': '❌ Entre un nombre positif de minutes (ex: 30)',
            'not_muted': '❌ Non réduit au silence!',
            'unmuted': '✅ {} n\'est plus réduit au silence',
            'kicked': '✅ {} expulsé',
            'banned': '✅ {} banni',
            'user_not_found': '❌ Utilisateur {} non trouvé!',
            'unbanned': '✅ {} débanni',
            'cleared': '✅ {} messages supprimés',
            'clear': '✅ {} messages supprimés',
            'clear_range': '❌ 1-100 messages seulement!',
            'delwarn': '✅ Avertissement #{} supprimé',
            'warned': '⚠️ {} a reçu un avertissement #{}',
            'warn_reason': 'Raison',
            'warn_total': 'Total',
            'no_warnings': '{} n\'a aucun avertissement',
            'warnings_title': '⚠️ Avertissements pour {}',
            'warnings_total': 'Total: {}',
            'warn_removed': '✅ Avertissement #{} supprimé',
            'warn_not_found': '❌ Avertissement #{} non trouvé!',
            'topwarnings_desc': '🏆 Top avertissements',
            'slowmode': '✅ Mode lent {}s dans {}',
            'locked': '🔒 {} verrouillé',
            'unlocked': '🔓 {} déverrouillé',
            'reset': '✅ {} réinitialisé',
            'report_sent': '✅ Signalement envoyé',
            'pinned': '📌 Épinglé',
            'unpinned': '📌 Désépinglé',
            'msg_not_found': '❌ Message non trouvé',
            'antinuke_configured': '✅ Antinuke configuré!',
            'setupantinuke_desc': '🛡️ Protection antinuke activée',
            'timeout_set': '⏰ {} en timeout pour {} min',
            'timeout_removed': '✅ {} timeout supprimé',
            'softbanned': '✅ {} softbanni',
            'massbanned': '✅ {} utilisateurs bannis',
            'bot_messages_deleted': '✅ {} messages du bot supprimés',
            'strike_given': '⚠️ {} strike #{}',
            'strike_removed': '✅ Strike #{} retiré de {}',
            'no_strikes': '✅ {} n\'a aucun strike',
            'strike_not_found': '❌ Strike #{} non trouvé',
            'strikes_title': '⚠️ Strikes de {}',
            'topstrikes_title': '🏆 Top strikes',
            'nickname_set': '✅ Surnom de {} changé en {}',
            'role_added': '✅ Rôle {} ajouté à {}',
            'role_removed': '✅ Rôle {} retiré de {}',
            'role_created': '✅ Rôle {} créé',
            'role_deleted': '✅ Rôle supprimé',
            'reaction_role_set': '✅ Réaction {} → {}',
            'channel_created': '✅ Salon #{} créé',
            'channel_deleted': '✅ Salon supprimé',
            'channel_cloned': '✅ Salon #{} cloné',
            'channel_moved': '✅ Salon #{} déplacé à la position {}',
            'voice_muted': '🔇 {} réduit au silence en vocal',
            'voice_unmuted': '🔊 {} n\'est plus réduit au silence en vocal',
            'voice_deafened': '🔇 {} assourdi',
            'voice_undeafened': '🔊 {} n\'est plus assourdi',
            'voice_moved': '✅ {} déplacé vers {}',
            'voice_kicked': '🎤 {} expulsé du vocal',
            'vkick_desc': '🎤 {} expulsé du canal vocal',
            'vmove_desc': '🔊 {} déplacé vers {}',
            'not_in_voice': '❌ Pas dans un salon vocal!',
            'serverinfo_owner': 'Propriétaire',
            'serverinfo_members': 'Membres',
            'serverinfo_channels': 'Salons',
            'serverinfo_roles': 'Rôles',
            'serverinfo_title': '📊 Informations sur le serveur | {}',
            'serverinfo_footer': 'ID du serveur: {} • bariier Bot',
            'userinfo_title': 'Informations sur {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'A rejoint',
            'userinfo_created': 'Créé',
            'userinfo_bot': 'Bot',
            'userinfo_roles_header': 'Rôles',
            'userinfo_footer': 'bariier Bot | Informations',
            'avatar_title': 'Avatar de {}',
            'avatar_title_full': 'Avatar de {}',
            'avatar_footer': 'bariier Bot | Avatar de l\'utilisateur',
            'membercount_total': 'Total',
            'membercount_humans': 'Humains',
            'membercount_bots': 'Bots',
            'membercount_title': '📊 Statistiques des membres',
            'membercount_footer': 'bariier Bot | Statistiques',
            'admins_list': '👑 Administrateurs',
            'admins_title': '👑 Administrateurs du serveur',
            'admins_footer': 'bariier Bot | Administration',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots sur le serveur',
            'bots_footer': 'bariier Bot | Bots',
            'none': 'Aucun',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Expression invalide',
            'calc_title': '🧮 Calculatrice',
            'calc_footer': 'bariier Bot | Utilitaires',
            'reminder_set': '✅ Rappel dans {}',
            'reminder_invalid': '❌ Utilise: 10s, 5m, 1h, 1d',
            'reminder_title': '⏰ Rappel Défini',
            'reminder_footer': 'bariier Bot | Rappel',
            'uptime_text': '🕐 Temps de fonctionnement: {}j {}h {}m',
            'uptime_title': '🕐 Temps de Fonctionnement',
            'uptime_footer': 'bariier Bot | Statistiques',
            'poll_created': '✅ Sondage créé!',
            'poll_voted': '✅ Voté!',
            'poll_total': 'Total des votes: {}',
            'poll_title': '📊 Sondage: {}',
            'poll_option': '{} votes',
            'poll_footer': 'bariier Bot | Sondage actif',
            'announce_sent': '✅ Envoyé à {}',
            'lang_title': '🌐 Sélection de la langue',
            'lang_desc': 'Clique sur le bouton pour sélectionner la langue',
            'lang_changed_ru': '🌐 Langue changée en **Russe**! Commandes mises à jour.',
            'lang_changed_en': '🌐 Language changed to **English**! Commands updated.',
            'lang_changed_es': '🌐 Langue changée en **Espagnol**! Commandes mises à jour.',
            'lang_changed_fr': '🌐 Langue changée en **Français**! Commandes mises à jour.',
            'lang_es': '🇪🇸 Espagnol',
            'lang_fr': '🇫🇷 Français',
            'lang_changed_title': '🌐 Langue Changée',
            'lang_changed_footer': 'bariier Bot | Paramètres',
            'lang_ru_desc': 'Changer la langue en russe',
            'lang_en_desc': 'Changer la langue en anglais',
            'lang_es_desc': 'Changer la langue en espagnol',
            'lang_fr_desc': 'Changer la langue en français',
            'lang_select_placeholder': '🌐 Choisis la langue',
            'lang_current': '**Langue actuelle:** {}',
            'lang_admin_only': '**Réservé aux administrateurs!**',
            'lang_select_menu': 'Sélectionne une langue dans le menu.',
            'lang_footer': 'bariier Bot • 🔒 Administrateurs uniquement',
            'promotion_level': '📊 Ton niveau: {} | XP: {}',
            'leaderboard_title': '🏆 Classement',
            'xp_added': '✅ {} XP ajoutés à {}',
            'xp_set': '✅ {} XP définis pour {}',
            'level_set': '✅ Niveau {} défini pour {}',
            'afk_set': '✅ {} est maintenant AFK: {}',
            'afk_removed': '✅ AFK retiré',
            'not_afk': '❌ Tu n\'es pas AFK',
            'afk_title': '💤 Mode AFK',
            'afk_footer': 'bariier Bot | AFK',
            'timestamp_current': '🕐 Horodatage actuel: {}',
            'timestamp_title': '🕐 Horodatage Actuel',
            'timestamp_footer': 'bariier Bot | Utilitaires',
            'color_info': '🎨 Informations sur la couleur {}',
            'color_title': '🎨 Informations sur la couleur {}',
            'color_footer': 'bariier Bot | Informations couleur',
            'qr_code_title': '📱 Code QR',
            'qr_title': '📱 Code QR',
            'qr_footer': 'bariier Bot | Générateur QR',
            'giveaway_started': '🎁 Concours lancé!',
            'giveaway_title': '🎁 Concours',
            'giveaway_prize': '🏆 Prix: {}',
            'giveaway_winners': '👑 Gagnants: {}',
            'giveaway_duration': '⏰ Durée: {}',
            'giveaway_footer': 'bariier Bot | Bonne chance!',
            'cat_title': '🐱 Chat Aléatoire',
            'cat_title_full': '🐱 Chat aléatoire',
            'cat_footer': 'bariier Bot | Chats',
            'roll_result': '🎲 Tu as lancé {} (1-{})',
            'roll_title': '🎲 Lancer de Dés',
            'roll_footer': 'bariier Bot | Jeux',
            'eightball_result': '🎱 {}',
            'eightball_title': '🎱 Boule Magique',
            'eightball_title_full': '🎱 Boule magique',
            'eightball_question': '❓ Question',
            'eightball_footer': 'bariier Bot | Prédictions',
            'joke_title': '😂 Blague',
            'joke_title_full': '😂 Blague',
            'joke_footer': 'bariier Bot | Humour',
            'fact_title': '📖 Fait Aléatoire',
            'fact_title_full': '📖 Fait aléatoire',
            'fact_footer': 'bariier Bot | Intéressant',
            'advice_title': '💡 Conseil',
            'advice_title_full': '💡 Conseil',
            'advice_footer': 'bariier Bot | Sagesse',
            'quote_title': '📝 Citation',
            'quote_title_full': '📝 Citation',
            'quote_footer': 'bariier Bot | Inspiration',
            'trivia_question': '❓ {} (Difficulté: {})',
            'trivia_title': '❓ Quiz',
            'trivia_footer': 'bariier Bot | Quiz',
            'rps_win': 'Tu as gagné!',
            'rps_lose': 'J\'ai gagné!',
            'rps_tie': 'Égalité!',
            'rps_title': '✊ Pierre, Papier, Ciseaux',
            'rps_choice': 'Tu as choisi **{}**, j\'ai choisi **{}**.',
            'rps_footer': 'bariier Bot | Jeux',
            'flip_heads': 'Pile',
            'flip_tails': 'Face',
            'flip_title': '🪙 Lancer de Pièce',
            'flip_result': 'C\'est tombé sur **{}**!',
            'flip_footer': 'bariier Bot | Jeux',
            'welcome_configured': '✅ Bienvenue configurée dans {}',
            'welcome_disabled': '✅ Bienvenue désactivée',
            'photo_welcome_configured': '✅ Bienvenue avec photo configurée!',
            'setup_logs_title': '📋 Configuration des Logs',
            'setup_logs_footer': 'bariier Bot | Journaux',
            'setup_welcome_title': '👋 Configuration des Bienvenues',
            'setup_welcome_footer': 'bariier Bot | Bienvenues',
            'setup_photowelcome_title': '🖼️ Configuration de la Bienvenue avec Photo',
            'setup_photowelcome_footer': 'bariier Bot | Bienvenues avec Photo',
            'disable_welcome_title': '⚠️ Désactiver les Bienvenues',
            'disable_welcome_footer': 'bariier Bot | Bienvenues Désactivées',
            'captcha_configured': '✅ Captcha configuré avec le rôle {}',
            'captcha_disabled': '✅ Captcha désactivé',
            'setup_captcha_title': '🔐 Configuration du Captcha',
            'setup_captcha_footer': 'bariier Bot | Sécurité',
            'disable_captcha_title': '🔐 Désactiver le Captcha',
            'disable_captcha_footer': 'bariier Bot | Captcha Désactivé',
            'ticket_setup_success': '✅ Système configuré!',
            'ticket_setup_info': 'Type: **{}**\nCatégorie: {}\nRôle: {}',
            'ticket_created': '✅ Ticket créé: {}',
            'ticket_no_permission': '❌ Pas de permission!',
            'ticket_closing': '🔒 Fermeture du ticket...',
            'ticket_closed_user': '✅ Ton ticket **{}** a été fermé.',
            'ticket_accepted': '✅ Ticket accepté pour travail!',
            'ticket_accepted_user': '✅ Ton ticket **{}** a été accepté par {}',
            'ticket_rejected': '❌ Ticket rejeté!',
            'ticket_rejected_user': '❌ Ton ticket **{}** a été rejeté.',
            'ticket_reply_sent': '✅ Réponse envoyée!',
            'ticket_reply_user': '📩 Réponse à ton ticket **{}** de {}:\n\n{}',
            'ticket_status_pending': '⏳ En attente',
            'ticket_status_accepted': '✅ ACCEPTÉ',
            'ticket_status_rejected': '❌ REJETÉ',
            'ticket_status_answered': '✅ RÉPONDU',
            'ticket_support_title': '🎫 Système de tickets',
            'ticket_support_desc': 'Clique sur le bouton pour créer un ticket.\nNotre personnel te contactera bientôt.',
            'ticket_bug_title': '🐛 Système de signalement de bugs',
            'ticket_bug_desc': 'Tu as trouvé un bug? Clique sur le bouton pour le signaler aux développeurs.\n\n**Merci d\'aider à améliorer le bot!**',
            'ticket_idea_title': '💡 Idées pour le bot',
            'ticket_idea_desc': 'Tu as une idée pour améliorer le bot? Clique sur le bouton et partage-la!\n\n**Les meilleures idées seront implémentées!**',
            'ticket_report_title': '⚠️ Signalement du personnel',
            'ticket_report_desc': 'Clique sur le bouton pour signaler un membre du personnel.\n\n**Les faux signalements seront punis!**',
            'ticket_partnership_title': '🤝 Partenariat',
            'ticket_partnership_desc': 'Clique sur le bouton pour proposer un partenariat, de la publicité ou des événements communs.',
            'ticket_modal_support_title': '🎫 Créer un ticket',
            'ticket_modal_support_topic': 'Sujet',
            'ticket_modal_support_description': 'Description',
            'ticket_modal_bug_title': '🐛 Signalement de bug',
            'ticket_modal_bug_summary': 'Résumé',
            'ticket_modal_bug_details': 'Description détaillée',
            'ticket_modal_bug_steps': 'Étapes pour reproduire',
            'ticket_modal_idea_title': '💡 Idée pour le bot',
            'ticket_modal_idea_name': 'Titre de l\'idée',
            'ticket_modal_idea_description': 'Description',
            'ticket_modal_idea_benefit': 'Pourquoi est-ce utile?',
            'ticket_modal_report_title': '⚠️ Signalement du personnel',
            'ticket_modal_report_against': 'Qui signales-tu?',
            'ticket_modal_report_reason': 'Raison',
            'ticket_modal_report_proof': 'Preuve',
            'ticket_modal_partnership_title': '🤝 Partenariat',
            'ticket_modal_partnership_name': 'Nom du projet',
            'ticket_modal_partnership_type': 'Type de partenariat',
            'ticket_modal_partnership_description': 'Description',
            'ticket_modal_partnership_contacts': 'Contacts',
            'ticket_embed_new': '🆕 NOUVEAU TICKET',
            'ticket_embed_topic': '📌 Sujet',
            'ticket_embed_question': '📝 Description',
            'ticket_button_close': '🔒 Fermer',
            'ticket_button_accept': '✅ Accepter',
            'ticket_button_reject': '❌ Rejeter',
            'ticket_button_reply': '✏️ Répondre',
            'ticket_reply_modal_title': '📝 Répondre à l\'utilisateur',
            'ticket_reply_modal_label': 'Message',
            'application_created': '✅ Candidature créée! Bouton envoyé dans le salon.',
            'application_no_questions': '❌ Ajoute au moins 1 question!',
            'application_question_added': '✅ Question ajoutée! (Total: {})',
            'application_button_label': '📝 Postuler: {}',
            'application_embed_title': '📝 {}',
            'application_embed_desc': 'Clique sur le bouton pour postuler.\nAprès examen, tu recevras le rôle {}',
            'application_creation_title': '📝 Créer une candidature',
            'application_creation_desc': '**Nom:** {}\n**Rôle:** {}\n**Salon d\'envoi:** {}\n\nClique sur les boutons pour ajouter des questions.',
            'application_add_question_button': '➕ Ajouter une question',
            'application_finish_button': '✅ Terminer la création',
            'application_submit_button': '📝 Postuler: {}',
            'application_modal_title': '📝 {}',
            'application_submitted': '✅ Candidature envoyée! Attends une décision.',
            'application_new_title': '📥 Nouvelle candidature: {}',
            'application_new_desc': '**De:** {}\n**ID:** {}\n**Statut:** ⏳ En attente de révision',
            'application_question_field': '❓ Question {}',
            'application_footer': 'ID de candidature: {}',
            'application_approve_button': '✅ Approuver',
            'application_reject_button': '❌ Rejeter',
            'application_approve_msg_button': '✏️ Approuver avec message',
            'application_reject_msg_button': '📝 Rejeter avec message',
            'application_approved': '✅ Candidature approuvée! {} a reçu le rôle {}',
            'application_approved_simple': '✅ Candidature approuvée!',
            'application_rejected': '❌ Candidature rejetée!',
            'application_approved_with_msg': '✅ Candidature approuvée avec message!',
            'application_rejected_with_msg': '❌ Candidature rejetée avec message!',
            'application_status_approved': '✅ APPROUVÉE',
            'application_status_rejected': '❌ REJETÉE',
            'application_status_approved_msg': '✅ APPROUVÉE (avec message)',
            'application_status_rejected_msg': '❌ REJETÉE (avec message)',
            'application_reviewed_by': '✅ Révisé par',
            'application_reviewed_by_reject': '❌ Révisé par',
            'application_review_message': '📝 Message',
            'application_reject_reason': '📝 Raison',
            'application_dm_approved': '✅ Ta candidature **{}** a été **APPROUVÉE**! Tu as reçu le rôle {}',
            'application_dm_rejected': '❌ Ta candidature **{}** a été **REJETÉE**.',
            'application_dm_approved_msg': '✅ Ta candidature **{}** a été **APPROUVÉE**! Tu as reçu le rôle {}\n\n**Message de l\'administration:**\n{}',
            'application_dm_rejected_msg': '❌ Ta candidature **{}** a été **REJETÉE**.\n\n**Raison:**\n{}',
            'application_no_permission': '❌ Pas de permission!',
            'application_approve_modal_title': '✅ Approuver la candidature avec message',
            'application_approve_modal_label': 'Message à l\'utilisateur',
            'application_approve_modal_placeholder': 'Écris un message pour l\'utilisateur...',
            'application_reject_modal_title': '❌ Rejeter la candidature avec message',
            'application_reject_modal_label': 'Raison du rejet',
            'application_reject_modal_placeholder': 'Écris la raison du rejet...',
            'application_list_title': '📋 Liste des candidatures',
            'application_delete_success': '✅ Candidature #{} supprimée!',
            'application_not_found': '❌ Candidature non trouvée!',
            'application_no_apps': '❌ Aucune candidature créée!',
            'authors_title': '👑 bariier Bot | Auteurs et Développeurs',
            'authors_desc': 'Voici l\'équipe qui a rendu ce bot possible!',
            'authors_ceo': '👑 CEO / Fondateur',
            'authors_ceo_value': '**Forever**\nDéveloppeur principal et visionnaire',
            'authors_moderators': '🛠️ Modérateurs',
            'authors_moderators_value': '**D1koot** - Modérateur et Développeur\n**Andy.wirus** - Modérateur et Testeur🎉<t:1781388000:s>',
            'authors_coder': '💻 Programmeur',
            'authors_coder_value': '**D1koot**\nDéveloppeur principal du code',
            'authors_support': '🎧 Équipe de Support',
            'authors_support_value': '**K1APMI** - Support Technique\n**Artem2012rtgf** - Aide aux utilisateurs\n**Mike** - Testeur, Aide aux utilisateurs',
            'authors_thanks': '📢 Remerciements',
            'authors_thanks_value': 'Merci à tous ceux qui ont aidé à tester et développer le bot!\nLe bot a été créé pour votre confort et votre sécurité.',
            'authors_footer': 'bariier Bot • Respect aux développeurs',
            'hello_title': '✨ Salutation',
            'hello_footer': 'bariier Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latence:** `{} ms`\n**Statut:** {}',
            'ping_good': '🟢 Excellent',
            'ping_medium': '🟡 Moyenne',
            'ping_bad': '🔴 Mauvaise',
            'ping_footer': 'bariier Bot | 🌐 État du réseau',
            'blacklist_title': '⛔ ACCÈS REFUSÉ',
            'blacklist_desc': '**Tu es sur la liste noire du bot.**\nContacte l\'administrateur pour être débloqué.',
            'blacklist_footer': 'bariier Bot • Bloqué',
            'massunban_title': '🔓 Débannissement Massif',
            'massunban_success': '✅ Débannis avec succès',
            'massunban_list': '📋 Liste des débannis',
            'massunban_errors': '❌ Erreurs',
            'massunban_start': '🔄 Débannissement de **{}** utilisateurs...',
            'massunban_none': '❌ Aucun utilisateur banni sur le serveur!',
            'massunban_footer': 'Demandé par: {} • bariier Bot',
            'send_dm_title': '📨 Message Envoyé',
            'send_dm_success': '✅ Message envoyé avec succès à l\'utilisateur {} (ID: {})',
            'send_dm_text': '📝 Texte du message',
            'send_dm_footer': 'bariier Bot | Développement',
            'servers_title': '📊 Liste des Serveurs avec le Bot',
            'servers_footer': 'Total des serveurs: {} • bariier Bot',
            'servers_id': '🆔 ID: `{}`',
            'servers_owner': '👑 Propriétaire: {}',
            'servers_members': '👥 Membres: {}',
            'servers_your': '🔴 **LE TIEN**',
            'regex_title_on': '🛡️ Automodération',
            'regex_desc_on': '✅ Système **ACTIVÉ**\n\n**📝 Pour les insultes:** Muet de 1 heure ({} mots)\n**🔨 Pour insulte au serveur/publicité:** Bannissement permanent ({} phrases)',
            'regex_title_off': '🛡️ Automodération',
            'regex_desc_off': '⚫ Système **DÉSACTIVÉ**',
            'regex_title_status': '🛡️ Statut de l\'Automodération',
            'regex_desc_status': '{}\n\n**📝 Insultes:** Muet de 1 heure ({} mots)\n**🔨 Insulte au serveur:** Bannissement permanent ({} phrases)',
            'regex_status_enabled': '🔴 **ACTIVÉE**',
            'regex_status_disabled': '⚫ **DÉSACTIVÉE**',
            'regex_footer': 'bariier Bot | Protection',
            'member_join_log': '🚪 Membre a rejoint',
            'member_remove_log': '🚪 Membre est parti',
            'message_delete_log': '🗑️ Message supprimé',
            'message_edit_log': '✏️ Message modifié',
            'log_footer': 'bariier Bot | Journaux',
        },
        'en': {
            'hello_title': '✨ Greeting',
            'hello_footer': 'bariier Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latency:** `{} ms`\n**Status:** {}',
            'ping_good': '🟢 Excellent',
            'ping_medium': '🟡 Medium',
            'ping_bad': '🔴 Bad',
            'ping_footer': 'bariier Bot | 🌐 Network Status',
            'lang_changed_title': '🌐 Language Changed',
            'lang_changed_footer': 'bariier Bot | Settings',
            'lang_ru_desc': 'Change language to Russian',
            'lang_en_desc': 'Change language to English',
            'lang_es_desc': 'Change language to Spanish',
            'lang_fr_desc': 'Change language to French',
            'lang_footer': 'bariier Bot • 🔒 Administrator only',
            'serverinfo_footer': 'Server ID: {} • bariier Bot',
            'userinfo_footer': 'bariier Bot | Information',
            'avatar_footer': 'bariier Bot | User Avatar',
            'membercount_footer': 'bariier Bot | Statistics',
            'calc_footer': 'bariier Bot | Utilities',
            'poll_footer': 'bariier Bot | Poll Active',
            'afk_footer': 'bariier Bot | AFK',
            'reminder_footer': 'bariier Bot | Reminder',
            'timestamp_footer': 'bariier Bot | Utilities',
            'color_footer': 'bariier Bot | Color Info',
            'qr_footer': 'bariier Bot | QR Generator',
            'uptime_footer': 'bariier Bot | Statistics',
            'giveaway_footer': 'bariier Bot | Good luck!',
            'cat_footer': 'bariier Bot | Cats',
            'roll_footer': 'bariier Bot | Games',
            'joke_footer': 'bariier Bot | Humor',
            'fact_footer': 'bariier Bot | Interesting',
            'advice_footer': 'bariier Bot | Wisdom',
            'quote_footer': 'bariier Bot | Inspiration',
            'trivia_footer': 'bariier Bot | Trivia',
            'rps_footer': 'bariier Bot | Games',
            'setup_logs_footer': 'bariier Bot | Logging',
            'setup_welcome_footer': 'bariier Bot | Welcomes',
            'setup_photowelcome_footer': 'bariier Bot | Photo Welcomes',
            'disable_welcome_footer': 'bariier Bot | Welcomes Disabled',
            'setup_captcha_footer': 'bariier Bot | Security',
            'disable_captcha_footer': 'bariier Bot | Captcha Disabled',
            'invite_title': '🔗 Invite',
            'invite_desc': 'Thanks for inviting me to your server!',
            'invite_footer': 'bariier Bot | Invites',
            'invite_button': '🤖 Invite Bot',
            'server_button': '🌐 Support Server',
            'regex_title_on': '🛡️ Automoderation',
            'regex_desc_on': '✅ System **ENABLED**\n\n**📝 For swearing:** 1 hour mute ({} words)\n**🔨 For server insult/advertising:** Permanent ban ({} phrases)',
            'regex_title_off': '🛡️ Automoderation',
            'regex_desc_off': '⚫ System **DISABLED**',
            'regex_title_status': '🛡️ Automoderation Status',
            'regex_desc_status': '{}\n\n**📝 Swearing:** 1 hour mute ({} words)\n**🔨 Server insult:** Permanent ban ({} phrases)',
            'regex_status_enabled': '🔴 **ENABLED**',
            'regex_status_disabled': '⚫ **DISABLED**',
            'regex_footer': 'bariier Bot | Protection',
            'massunban_footer': 'Requested by: {} • bariier Bot',
            'member_join_log': '🚪 Member joined',
            'member_remove_log': '🚪 Member left',
            'message_delete_log': '🗑️ Message deleted',
            'message_edit_log': '✏️ Message edited',
            'log_footer': 'bariier Bot | Logs',
            'hello': 'Hello, {}! I am **bariier Bot** 🤖',
            'ping': '🏓 Pong! Latency: {} ms',
            'help_title': '📚 Help - {}',
            'help_desc': 'Select a category from the menu below to see the command list.\nOr use `/help all` for full list.',
            'help_cmd_count': '{} commands',
            'help_footer': 'Did you know that there are only 100 commands? :3',
            'help_all_title': '📖 All Commands',
            'help_all_desc': 'Full list of all bot commands:',
            'help_category_title': '{} - Command List',
            'help_category_desc': 'Total commands in category: {}',
            'help_select_placeholder': '📋 Choose a category...',
            'help_select_overview': '📚 Overview',
            'help_select_overview_desc': 'Back to start',
            'help_select_all': '📖 All Commands',
            'help_select_all_desc': 'Show all 100 commands',
            'help_select_mod_desc': '28 commands',
            'help_select_roles_desc': '8 commands',
            'help_select_voice_desc': '5 commands',
            'help_select_info_desc': '9 commands',
            'help_select_level_desc': '6 commands',
            'help_select_util_desc': '10 commands',
            'help_select_fun_desc': '10 commands',
            'help_select_setup_desc': '13 commands',
            'help_select_misc_desc': '2 commands',
            'info_title': '🛡️ bariier Bot',
            'info_desc': 'The guardian bot for your server',
            'info_version': 'Version',
            'info_cmds': 'Commands',
            'info_footer': 'Always keeping order 🔒',
            'no_permission': '❌ No permission!',
            'need_admin': '❌ Need admin permissions!',
            'error': '❌ Error: {}',
            'sent': '✅ Sent to {}',
            'no_roles': '❌ No roles specified!',
            'settings_saved': '✅ Settings saved',
            'log_channel_set': '✅ Log channel: {}',
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
            'clear': '✅ Cleared {} messages',
            'clear_range': '❌ 1-100 messages only!',
            'delwarn': '✅ Warning #{} removed',
            'warned': '⚠️ {} warned #{}',
            'warn_reason': 'Reason',
            'warn_total': 'Total',
            'no_warnings': '{} has no warnings',
            'warnings_title': '⚠️ Warnings for {}',
            'warnings_total': 'Total: {}',
            'warn_removed': '✅ Warning #{} removed',
            'warn_not_found': '❌ Warning #{} not found!',
            'topwarnings_desc': '🏆 Top warnings',
            'slowmode': '✅ Slowmode {}s in {}',
            'locked': '🔒 {} locked',
            'unlocked': '🔓 {} unlocked',
            'reset': '✅ {} reset',
            'report_sent': '✅ Report sent',
            'pinned': '📌 Pinned',
            'unpinned': '📌 Unpinned',
            'msg_not_found': '❌ Message not found',
            'antinuke_configured': '✅ Antinuke configured!',
            'setupantinuke_desc': '🛡️ Anti-nuke protection activated',
            'timeout_set': '⏰ {} timed out for {}min',
            'timeout_removed': '✅ {} timeout removed',
            'softbanned': '✅ {} softbanned',
            'massbanned': '✅ Banned {} users',
            'bot_messages_deleted': '✅ Deleted {} bot messages',
            'strike_given': '⚠️ {} strike #{}',
            'strike_removed': '✅ Strike #{} removed from {}',
            'no_strikes': '✅ {} has no strikes',
            'strike_not_found': '❌ Strike #{} not found',
            'strikes_title': '⚠️ Strikes for {}',
            'topstrikes_title': '🏆 Top strikes',
            'nickname_set': '✅ Nickname for {} changed to {}',
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
            'vkick_desc': '🎤 {} kicked from voice channel',
            'vmove_desc': '🔊 Moved {} to {}',
            'not_in_voice': '❌ Not in voice channel!',
            'serverinfo_owner': 'Owner',
            'serverinfo_members': 'Members',
            'serverinfo_channels': 'Channels',
            'serverinfo_roles': 'Roles',
            'serverinfo_title': '📊 Server Info | {}',
            'userinfo_title': 'Info about {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'Joined',
            'userinfo_created': 'Created',
            'userinfo_bot': 'Bot',
            'userinfo_roles_header': 'Roles',
            'avatar_title': 'Avatar of {}',
            'avatar_title_full': 'Avatar of {}',
            'membercount_total': 'Total',
            'membercount_humans': 'Humans',
            'membercount_bots': 'Bots',
            'membercount_title': '📊 Member Statistics',
            'admins_list': '👑 Administrators',
            'admins_title': '👑 Server Administrators',
            'admins_footer': 'bariier Bot | Administration',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots on Server',
            'bots_footer': 'bariier Bot | Bots',
            'none': 'None',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Invalid expression',
            'calc_title': '🧮 Calculator',
            'reminder_set': '✅ Reminder in {}',
            'reminder_invalid': '❌ Use: 10s, 5m, 1h, 1d',
            'reminder_title': '⏰ Reminder set',
            'uptime_text': '🕐 Uptime: {}d {}h {}m',
            'uptime_title': '🕐 Bot Uptime',
            'poll_created': '✅ Poll created!',
            'poll_voted': '✅ Voted!',
            'poll_total': 'Total votes: {}',
            'poll_title': '📊 Poll: {}',
            'poll_option': '{} votes',
            'announce_sent': '✅ Sent to {}',
            'lang_title': '🌐 Language Selection',
            'lang_desc': 'Click the button below to select language',
            'lang_changed_ru': '🌐 Language changed to **Russian**! Commands updated.',
            'lang_changed_en': '🌐 Language changed to **English**! Commands updated.',
            'lang_changed_es': '🌐 Language changed to **Spanish**! Commands updated.',
            'lang_changed_fr': '🌐 Language changed to **French**! Commands updated.',
            'lang_es': '🇪🇸 Spanish',
            'lang_fr': '🇫🇷 French',
            'lang_select_placeholder': '🌐 Select language',
            'lang_current': '**Current language:** {}',
            'lang_admin_only': '**For administrators only!**',
            'lang_select_menu': 'Select a language from the menu below.',
            'promotion_level': '📊 Your level: {} | XP: {}',
            'leaderboard_title': '🏆 Leaderboard',
            'xp_added': '✅ Added {} XP to {}',
            'xp_set': '✅ Set {} XP for {}',
            'level_set': '✅ Set level {} for {}',
            'afk_set': '✅ {} is now AFK: {}',
            'afk_removed': '✅ AFK removed',
            'not_afk': '❌ You are not AFK',
            'afk_title': '💤 AFK mode',
            'timestamp_current': '🕐 Current timestamp: {}',
            'timestamp_title': '🕐 Current timestamp',
            'color_info': '🎨 Color info for {}',
            'color_title': '🎨 Color info for {}',
            'qr_code_title': '📱 QR Code',
            'qr_title': '📱 QR Code',
            'giveaway_started': '🎁 Giveaway started!',
            'giveaway_title': '🎁 Giveaway',
            'giveaway_prize': '🏆 Prize: {}',
            'giveaway_winners': '👑 Winners: {}',
            'giveaway_duration': '⏰ Duration: {}',
            'cat_title': '🐱 Random Cat',
            'cat_title_full': '🐱 Random Cat',
            'roll_result': '🎲 You rolled {} (1-{})',
            'roll_title': '🎲 Dice Roll',
            'eightball_result': '🎱 {}',
            'eightball_title': '🎱 Magic 8ball',
            'eightball_title_full': '🎱 Magic 8ball',
            'eightball_question': '❓ Question',
            'eightball_footer': 'bariier Bot | Predictions',
            'joke_title': '😂 Joke',
            'joke_title_full': '😂 Joke',
            'fact_title': '📖 Fact',
            'fact_title_full': '📖 Random Fact',
            'advice_title': '💡 Advice',
            'advice_title_full': '💡 Advice',
            'quote_title': '📝 Quote',
            'quote_title_full': '📝 Quote',
            'trivia_question': '❓ {} (Difficulty: {})',
            'trivia_title': '❓ Trivia',
            'rps_win': 'You win!',
            'rps_lose': 'I win!',
            'rps_tie': 'Tie!',
            'rps_title': '✊ Rock, Paper, Scissors',
            'rps_choice': 'You chose **{}**, I chose **{}**.',
            'flip_heads': 'Heads',
            'flip_tails': 'Tails',
            'flip_title': '🪙 Coin Flip',
            'flip_result': 'It landed on **{}**!',
            'welcome_configured': '✅ Welcome configured in {}',
            'welcome_disabled': '✅ Welcome disabled',
            'photo_welcome_configured': '✅ Photo welcome configured!',
            'setup_logs_title': '📋 Logging Setup',
            'setup_welcome_title': '👋 Welcome Setup',
            'setup_photowelcome_title': '🖼️ Photo Welcome Setup',
            'disable_welcome_title': '⚠️ Disable Welcome',
            'captcha_configured': '✅ Captcha configured with role {}',
            'captcha_disabled': '✅ Captcha disabled',
            'setup_captcha_title': '🔐 Captcha Setup',
            'disable_captcha_title': '🔐 Disable Captcha',
            'ticket_setup_success': '✅ System configured!',
            'ticket_setup_info': 'Type: **{}**\nCategory: {}\nRole: {}',
            'ticket_created': '✅ Ticket created: {}',
            'ticket_no_permission': '❌ No permission!',
            'ticket_closing': '🔒 Closing ticket...',
            'ticket_closed_user': '✅ Your ticket **{}** has been closed.',
            'ticket_accepted': '✅ Ticket accepted for work!',
            'ticket_accepted_user': '✅ Your ticket **{}** has been accepted by {}',
            'ticket_rejected': '❌ Ticket rejected!',
            'ticket_rejected_user': '❌ Your ticket **{}** has been rejected.',
            'ticket_reply_sent': '✅ Reply sent!',
            'ticket_reply_user': '📩 Reply to your ticket **{}** from {}:\n\n{}',
            'ticket_status_pending': '⏳ Pending',
            'ticket_status_accepted': '✅ ACCEPTED',
            'ticket_status_rejected': '❌ REJECTED',
            'ticket_status_answered': '✅ ANSWERED',
            'ticket_support_title': '🎫 Ticket System',
            'ticket_support_desc': 'Click the button below to create a ticket.\nOur staff will contact you shortly.',
            'ticket_bug_title': '🐛 Bug Report System',
            'ticket_bug_desc': 'Found a bug? Click the button below to report it to the developers.\n\n**Thank you for helping improve the bot!**',
            'ticket_idea_title': '💡 Ideas for Bot',
            'ticket_idea_desc': 'Have an idea to improve the bot? Click the button below and share!\n\n**The best ideas will be implemented!**',
            'ticket_report_title': '⚠️ Staff Reports',
            'ticket_report_desc': 'Click the button below to report a staff member.\n\n**False reports will be punished!**',
            'ticket_partnership_title': '🤝 Partnership',
            'ticket_partnership_desc': 'Click the button below to propose partnership, advertising, or joint events.',
            'ticket_modal_support_title': '🎫 Create Ticket',
            'ticket_modal_support_topic': 'Subject',
            'ticket_modal_support_description': 'Description',
            'ticket_modal_bug_title': '🐛 Bug Report',
            'ticket_modal_bug_summary': 'Summary',
            'ticket_modal_bug_details': 'Detailed description',
            'ticket_modal_bug_steps': 'Steps to reproduce',
            'ticket_modal_idea_title': '💡 Idea for Bot',
            'ticket_modal_idea_name': 'Idea title',
            'ticket_modal_idea_description': 'Description',
            'ticket_modal_idea_benefit': 'Why is this useful?',
            'ticket_modal_report_title': '⚠️ Staff Report',
            'ticket_modal_report_against': 'Who are you reporting?',
            'ticket_modal_report_reason': 'Reason',
            'ticket_modal_report_proof': 'Evidence',
            'ticket_modal_partnership_title': '🤝 Partnership',
            'ticket_modal_partnership_name': 'Project Name',
            'ticket_modal_partnership_type': 'Partnership Type',
            'ticket_modal_partnership_description': 'Description',
            'ticket_modal_partnership_contacts': 'Contacts',
            'ticket_embed_new': '🆕 NEW TICKET',
            'ticket_embed_topic': '📌 Subject',
            'ticket_embed_question': '📝 Description',
            'ticket_button_close': '🔒 Close',
            'ticket_button_accept': '✅ Accept',
            'ticket_button_reject': '❌ Reject',
            'ticket_button_reply': '✏️ Reply',
            'ticket_reply_modal_title': '📝 Reply to user',
            'ticket_reply_modal_label': 'Message',
            'application_created': '✅ Application created! Button sent to channel.',
            'application_no_questions': '❌ Add at least 1 question!',
            'application_question_added': '✅ Question added! (Total: {})',
            'application_button_label': '📝 Apply: {}',
            'application_embed_title': '📝 {}',
            'application_embed_desc': 'Click the button below to apply.\nAfter review you will receive the role {}',
            'application_creation_title': '📝 Create Application',
            'application_creation_desc': '**Name:** {}\n**Role:** {}\n**Send channel:** {}\n\nClick the buttons below to add questions.',
            'application_add_question_button': '➕ Add Question',
            'application_finish_button': '✅ Finish Creation',
            'application_submit_button': '📝 Apply: {}',
            'application_modal_title': '📝 {}',
            'application_submitted': '✅ Application submitted! Await decision.',
            'application_new_title': '📥 New Application: {}',
            'application_new_desc': '**From:** {}\n**ID:** {}\n**Status:** ⏳ Pending review',
            'application_question_field': '❓ Question {}',
            'application_footer': 'Application ID: {}',
            'application_approve_button': '✅ Approve',
            'application_reject_button': '❌ Reject',
            'application_approve_msg_button': '✏️ Approve with message',
            'application_reject_msg_button': '📝 Reject with message',
            'application_approved': '✅ Application approved! {} received role {}',
            'application_approved_simple': '✅ Application approved!',
            'application_rejected': '❌ Application rejected!',
            'application_approved_with_msg': '✅ Application approved with message!',
            'application_rejected_with_msg': '❌ Application rejected with message!',
            'application_status_approved': '✅ APPROVED',
            'application_status_rejected': '❌ REJECTED',
            'application_status_approved_msg': '✅ APPROVED (with message)',
            'application_status_rejected_msg': '❌ REJECTED (with message)',
            'application_reviewed_by': '✅ Reviewed by',
            'application_reviewed_by_reject': '❌ Reviewed by',
            'application_review_message': '📝 Message',
            'application_reject_reason': '📝 Reason',
            'application_dm_approved': '✅ Your application **{}** has been **APPROVED**! You received the role {}',
            'application_dm_rejected': '❌ Your application **{}** has been **REJECTED**.',
            'application_dm_approved_msg': '✅ Your application **{}** has been **APPROVED**! You received the role {}\n\n**Message from staff:**\n{}',
            'application_dm_rejected_msg': '❌ Your application **{}** has been **REJECTED**.\n\n**Reason:**\n{}',
            'application_no_permission': '❌ No permission!',
            'application_approve_modal_title': '✅ Approve application with message',
            'application_approve_modal_label': 'Message to user',
            'application_approve_modal_placeholder': 'Write a message for the user...',
            'application_reject_modal_title': '❌ Reject application with message',
            'application_reject_modal_label': 'Reason for rejection',
            'application_reject_modal_placeholder': 'Write the reason for rejection...',
            'application_list_title': '📋 Application List',
            'application_delete_success': '✅ Application #{} deleted!',
            'application_not_found': '❌ Application not found!',
            'application_no_apps': '❌ No applications created!',
            'authors_title': '👑 bariier Bot | Authors & Developers',
            'authors_desc': 'Here is the team that made this bot possible!',
            'authors_ceo': '👑 CEO / Founder',
            'authors_ceo_value': '**Forever**\nLead developer and visionary',
            'authors_moderators': '🛠️ Moderators',
            'authors_moderators_value': '**D1koot** - Moderator & Developer\n**Andy.wirus** - Moderator & Tester🎉<t:1781388000:s>',
            'authors_coder': '💻 Coder',
            'authors_coder_value': '**D1koot**\nMain code developer',
            'authors_support': '🎧 Support Team',
            'authors_support_value': '**K1APMI** - Technical Support\n**Artem2012rtgf** - User Support\n**Mike** - Tester, User Support',
            'authors_thanks': '📢 Special Thanks',
            'authors_thanks_value': 'Thanks to everyone who helped test and develop the bot!\nThe bot was created for your convenience and safety.',
            'authors_footer': 'bariier Bot • Respect to the developers',
            'blacklist_title': '⛔ ACCESS DENIED',
            'blacklist_desc': '**You are in the bot\'s blacklist.**\nContact the administrator to be unblocked.',
            'blacklist_footer': 'bariier Bot • Blocked',
            'massunban_title': '🔓 Mass Unban',
            'massunban_success': '✅ Successfully unbanned',
            'massunban_list': '📋 Unbanned list',
            'autorole_no_permission': '⛔ No permission',
            'autorole_admin_only': 'Only administrators can use this command!',
            'autorole_access_denied': 'bariier Bot | Access denied',
            'autorole_error_no_role': '❌ Error',
            'autorole_error_no_role_desc': 'Specify a role to assign!\nExample: `/autorole on @Role`',
            'autorole_warning': '⚠️ Warning',
            'autorole_no_admin_role': 'Cannot automatically assign administrator role!',
            'autorole_error_role_higher': '⚠️ Error',
            'autorole_role_higher_desc': 'Role {} is higher or equal to my role!\nMove my role higher in the list.',
            'autorole_enabled': '✅ Autorole enabled',
            'autorole_enabled_desc': 'New members will automatically receive the role {}',
            'autorole_setup_by': 'Setup by: {}',
            'autorole_disabled': '⚙️ Autorole disabled',
            'autorole_disabled_desc': 'New members will no longer receive roles automatically.',
            'autorole_info': 'ℹ️ Info',
            'autorole_not_configured': 'Autorole was not configured.',
            'autorole_status_title': '📊 Autorole Status',
            'autorole_status_enabled': '✅ **Enabled**\n\nAssigned role: {}\nRole ID: `{}`',
            'autorole_status_enabled_no_role': '⚠️ **Enabled, but role not found!**\nThe role may have been deleted.\nUse `/autorole off` to disable.',
            'autorole_status_disabled': '⚫ **Disabled**\n\nUse `/autorole on @Role` to enable.',
            'autorole_footer': 'bariier Bot | Autorole',
            'massunban_errors': '❌ Errors',
            'massunban_start': '🔄 Starting unban of **{}** users...',
            'massunban_none': '❌ No banned users on the server!',
            'send_dm_title': '📨 Message sent',
            'send_dm_success': '✅ Message successfully sent to user {} (ID: {})',
            'send_dm_text': '📝 Message text',
            'send_dm_footer': 'bariier Bot | Development',
            'servers_title': '📊 List of servers with bot',
            'servers_id': '🆔 ID: `{}`',
            'servers_owner': '👑 Owner: {}',
            'servers_members': '👥 Members: {}',
            'servers_your': '🔴 **YOURS**',
            'servers_footer': 'Total servers: {} • bariier Bot',
        },
    }
    text = texts[lang].get(key, f'[{key}]')
    if args:
        return text.format(*args)
    return text

tech_work_active = False
ALLOWED_TECH_USERS = [1436760469980450816]


SETTINGS_FILE = 'bariier_settings.json'
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
    if cid and (c := bot.get_channel(cid)):
        await c.send(embed=embed)

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


@bot.tree.command(name='tech_work', description='Управление техрежимом (только для владельца)')
async def tech_work_cmd(interaction: discord.Interaction, action: str):
    global tech_work_active

    # Проверка - только владелец
    if interaction.user.id != YOUR_ID:
        await interaction.response.send_message("❌ Эта команда только для владельца бота!", ephemeral=True)
        return

    if action.lower() == 'on':
        tech_work_active = True
        embed = discord.Embed(title="🛠️ Режим техработ",
                              description="✅ **ВКЛЮЧЕН**\nТеперь только владелец может использовать команды.",
                              	color=discord.Color.from_rgb(255, 255, 255))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action.lower() == 'off':
        tech_work_active = False
        embed = discord.Embed(title="🛠️ Режим техработ",
                              description="✅ **ВЫКЛЮЧЕН**\nВсе пользователи могут использовать команды.",
                              color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action.lower() == 'status':
        status = "ВКЛЮЧЕН 🔴" if tech_work_active else "ВЫКЛЮЧЕН 🟢"
        embed = discord.Embed(title="🛠️ Статус техрежима", description=f"Текущий статус: **{status}**",
                              color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    else:
        await interaction.response.send_message("❌ Используй: `on`, `off` или `status`", ephemeral=True)


@bot.tree.command(name='lang', description='Change bot language')
async def lang_cmd(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return

    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="⛔ ДОСТУП ЗАПРЕЩЁН",
            description="**Только администраторы могут изменять язык бота!**\nОбратитесь к администратору сервера.",
            	color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text="bariier Bot • Требуются права администратора")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    class LanguageSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label='🇷🇺 Русский', value='ru', description='Изменить язык на русский',
                                     emoji='🇷🇺'),
                discord.SelectOption(label='🇬🇧 English', value='en', description='Change language to English',
                                     emoji='🇬🇧'),
                discord.SelectOption(label='🇪🇸 Español', value='es', description='Cambiar idioma a español',
                                     emoji='🇪🇸'),
                discord.SelectOption(label='🇫🇷 Français', value='fr', description='Changer la langue en français',
                                     emoji='🇫🇷')
            ]
            super().__init__(
                placeholder='🌐 Выберите язык / Select language',
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, select_interaction: discord.Interaction):
            if not select_interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="⛔ ACCESS DENIED",
                    description="Only administrators can change the language!",
                    	color=discord.Color.from_rgb(255, 255, 255)
                )
                embed.set_footer(text="bariier Bot • Insufficient permissions")
                return await select_interaction.response.send_message(embed=embed, ephemeral=True)

            selected = self.values[0]
            s = load_lang_settings()
            s[str(select_interaction.guild_id)] = selected
            save_lang_settings(s)

            messages = {
                'ru': '🌐 Язык изменён на **Русский**! Команды обновлены.',
                'en': '🌐 Language changed to **English**! Commands updated.',
                'es': '🌐 Idioma cambiado a **Español**! Comandos actualizados.',
                'fr': '🌐 Langue changée en **Français**! Commandes mises à jour.'
            }

            embed = discord.Embed(
                title="🌐 Language Changed" if selected != 'ru' else "🌐 Язык изменён",
                description=messages.get(selected, messages['en']),
                color=discord.Color.green()
            )
            embed.set_footer(text="bariier Bot • Settings" if selected != 'ru' else "bariier Bot • Настройки")
            await select_interaction.response.send_message(embed=embed, ephemeral=True)

    class LangView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(LanguageSelect())

    current_lang = get_lang(str(interaction.guild_id))
    lang_names = {
        'ru': '🇷🇺 Русский',
        'en': '🇬🇧 English',
        'es': '🇪🇸 Español',
        'fr': '🇫🇷 Français'
    }

    embed = discord.Embed(
        title="🌐 Выбор языка / Language Selection",
        description=f"**Текущий язык:** {lang_names.get(current_lang, '🇬🇧 English')}\n\n**Только для администраторов!**\nВыберите язык из меню ниже.\n\n**Current language:** {lang_names.get(current_lang, '🇬🇧 English')}\n\n**For administrators only!**\nSelect a language from the menu below.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="bariier Bot • 🔒 Требуются права администратора / Administrator only")
    await interaction.response.send_message(embed=embed, view=LangView())


# =====================================================
# 🛠️ СЕКРЕТНАЯ КОМАНДА ПАНЕЛИ РАЗРАБОТЧИКА !dp
# =====================================================
@bot.command(name='ap')
async def dev_panel(ctx):
    # Проверка - только для разработчика
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        return

    embed = discord.Embed(
        title="🛠️ AdminPandel | Панель разработчика",
        description="Добро пожаловать в панель управления ботом!",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    embed.add_field(
        name="📊 Статистика",
        value=f"• Серверов: **{len(bot.guilds)}**\n"
              f"• Пользователей: **{sum(g.member_count for g in bot.guilds)}**\n"
              f"• Команд: **{len(bot.tree.get_commands())}**",
        inline=False
    )
    embed.add_field(
        name="🔧 Быстрые команды",
        value="• `!sat` - Настроить все тикеты\n"
              "• `!cat` - Закрыть все тикеты\n"
              "• `!leave <id>` - Покинуть сервер\n"
              "• `!servers` - Список серверов",
        inline=False
    )
    embed.add_field(
        name="📋 Информация",
        value=f"• Бот: {bot.user.name}\n"
              f"• ID: {bot.user.id}\n"
              f"• Разработчик: <@{ALLOWED_IDS[0]}>",
        inline=False
    )
    embed.set_footer(text="bariier Bot | AdminPandel")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    class AdminPandelView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)

        @discord.ui.button(label="📊 Статус", style=discord.ButtonStyle.primary, emoji="📊")
        async def status_button(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            if btn_interaction.user.id not in ALLOWED_IDS:
                return await btn_interaction.response.send_message("❌ Эта кнопка только для разработчика!", ephemeral=True)

            # Информация о боте
            latency = round(bot.latency * 1000)
            status_embed = discord.Embed(
                title="📊 Статус бота",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            status_embed.add_field(name="🟢 Пинг", value=f"`{latency} ms`", inline=True)
            status_embed.add_field(name="🖥️ Серверов", value=f"`{len(bot.guilds)}`", inline=True)
            status_embed.add_field(name="👥 Пользователей", value=f"`{sum(g.member_count for g in bot.guilds)}`",
                                   inline=True)
            status_embed.add_field(name="📁 Каналов", value=f"`{sum(len(g.channels) for g in bot.guilds)}`", inline=True)
            status_embed.add_field(name="⏰ uptime", value=f"`{str(datetime.now() - start_time).split('.')[0]}`",
                                   inline=True)
            status_embed.add_field(name="💾 Память", value=f"`{round(os.getpid() / 1024 / 1024, 2)} MB`", inline=True)
            status_embed.set_footer(text="bariier Bot | Статус")

            await btn_interaction.response.send_message(embed=status_embed, ephemeral=True)

        @discord.ui.button(label="⚙️ Настройки", style=discord.ButtonStyle.secondary, emoji="⚙️")
        async def settings_button(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            if btn_interaction.user.id not in ALLOWED_IDS:
                return await btn_interaction.response.send_message("❌ Эта кнопка только для разработчика!", ephemeral=True)

            settings_embed = discord.Embed(
                title="⚙️ Настройки бота",
                description="Управление параметрами бота",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            settings_embed.add_field(
                name="🔧 Доступные команды",
                value="• `!sat` - Настроить все тикеты (ID: 1511417385595306024, 1511393460622463039)\n"
                      "• `!cat` - Закрыть все тикеты\n"
                      "• `!leave <id>` - Покинуть сервер\n"
                      "• `!servers` - Список серверов\n"
                      "• `/setup-logs` - Настроить канал логов",
                inline=False
            )
            settings_embed.add_field(
                name="📁 Файлы настроек",
                value=f"• `lang_settings.json` - Языки\n"
                      f"• `ticket_settings.json` - Тикеты\n"
                      f"• `autorole_settings.json` - Авто-роли\n"
                      f"• `warns.json` - Предупреждения",
                inline=False
            )
            settings_embed.set_footer(text="bariier Bot | Настройки")

            await btn_interaction.response.send_message(embed=settings_embed, ephemeral=True)

        @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.danger, emoji="🔒")
        async def close_button(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            if btn_interaction.user.id not in ALLOWED_IDS:
                return await btn_interaction.response.send_message("❌ Эта кнопка только для разработчика!", ephemeral=True)
            await btn_interaction.response.send_message("🔒 Панель закрыта", ephemeral=True)
            await btn_interaction.message.delete()

    view = AdminPandelView()
    await ctx.send(embed=embed, view=view)


@bot.tree.command(name='hello', description='Greet bariier bot')
async def hello(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return

    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'hello_title'),
        description=get_text(str(interaction.guild_id), 'hello', interaction.user.mention),
        color=discord.Color.purple()
    )
    embed.set_footer(text=get_text(str(interaction.guild_id), 'hello_footer'), icon_url=bot.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='ai', description='Задай вопрос — бот ответит с помощью AI')
@app_commands.describe(вопрос='Введи свой вопрос')
async def ii_command(interaction: discord.Interaction, вопрос: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return

    await interaction.response.defer(thinking=True)

    try:
        payload = {
            "model": "openai",
            "messages": [
                {"role": "system", "content": "Ты полезный помощник. Отвечай чётко и по делу на русском языке."},
                {"role": "user", "content": вопрос}
            ]
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://text.pollinations.ai/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=90)
            ) as resp:
                answer = await resp.text()

        if not answer:
            answer = "Не удалось получить ответ."

        embed = discord.Embed(
            title="🤖 Ответ AI",
            color=COLOR_BLUE
        )
        embed.add_field(name="❓ Вопрос", value=вопрос, inline=False)
        embed.add_field(name="💬 Ответ", value=answer[:1024] if len(answer) > 1024 else answer, inline=False)
        embed.set_footer(text=f"Спросил: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.followup.send(embed=embed)

    except asyncio.TimeoutError:
        try:
            await interaction.followup.send("⏳ AI отвечает слишком долго, попробуй ещё раз.")
        except Exception:
            pass
    except Exception as e:
        try:
            await interaction.followup.send(f"❌ Ошибка при запросе к AI: `{e}`")
        except Exception:
            pass


@bot.tree.command(name='ping', description='Check bot latency')
async def ping(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return

    latency = round(bot.latency * 1000)

    if latency < 100:
        status_color = COLOR_SUCCESS
        status_text = get_text(str(interaction.guild_id), 'ping_good')
    elif latency < 300:
        status_color = COLOR_WHITE
        status_text = get_text(str(interaction.guild_id), 'ping_medium')
    else:
        status_color = COLOR_WHITE
        status_text = get_text(str(interaction.guild_id), 'ping_bad')

    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'ping_title'),
        description=get_text(str(interaction.guild_id), 'ping_result', latency, status_text),
        color=status_color
    )
    embed.set_footer(text=get_text(str(interaction.guild_id), 'ping_footer'))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='info', description='Bot information')
async def info(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    e = discord.Embed(title=get_text(str(interaction.guild_id), 'info_title'), description=get_text(str(interaction.guild_id), 'info_desc'),
                      color=discord.Color.blue())
    e.add_field(name=get_text(str(interaction.guild_id), 'info_version'), value='v1.0.0', inline=True)
    e.add_field(name=get_text(str(interaction.guild_id), 'info_cmds'), value='Use `/help` to see all commands', inline=False)
    e.set_footer(text=get_text(str(interaction.guild_id), 'info_footer'))
    await interaction.response.send_message(embed=e)


@bot.tree.command(name='help', description='Все команды бота с категориями')
async def help_command(interaction: discord.Interaction, category: str = None):
    # ===== ПРОВЕРКА ТЕХРЕЖИМА =====
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    # ===============================

    if await check_blacklist(interaction): return

    lang = get_lang(str(interaction.guild_id))

    categories = {
        'overview': {'emoji': '📚', 'name_ru': 'Обзор', 'name_en': 'Overview'},
        'all': {'emoji': '📖', 'name_ru': 'Все команды', 'name_en': 'All Commands'},
        'mod': {'emoji': '🛡️', 'name_ru': 'Модерация', 'name_en': 'Moderation'},
        'roles': {'emoji': '👮', 'name_ru': 'Роли и каналы', 'name_en': 'Roles & Channels'},
        'voice': {'emoji': '🎤', 'name_ru': 'Голос', 'name_en': 'Voice'},
        'info': {'emoji': '📋', 'name_ru': 'Инфо', 'name_en': 'Info'},
        'level': {'emoji': '⭐', 'name_ru': 'Продвижение', 'name_en': 'Leveling'},
        'util': {'emoji': '🛠️', 'name_ru': 'Утилиты', 'name_en': 'Utility'},
        'fun': {'emoji': '🎉', 'name_ru': 'Развлечения', 'name_en': 'Fun'},
        'setup': {'emoji': '⚙️', 'name_ru': 'Настройки', 'name_en': 'Settings'},
        'misc': {'emoji': '🔗', 'name_ru': 'Прочее', 'name_en': 'Misc'}
    }

    commands_by_cat = {
        'mod': ['/mute', '/unmute', '/ban', '/unban', '/kick', '/clear', '/warn', '/warnings', '/topwarnings',
                '/delwarn', '/slowmode', '/lock', '/unlock', '/report', '/pin', '/unpin', '/vkick', '/timeout',
                '/untimeout', '/softban', '/massban', '/clean', '/strike', '/unstrike', '/strikes', '/topstrikes',
                '/setnick', '/setupantinuke'],
        'roles': ['/addrole', '/removerole', '/createrole', '/deleterole', '/createchannel', '/deletechannel',
                  '/clonechannel', '/movechannel'],
        'voice': ['/vmute', '/vunmute', '/vdeafen', '/vundeafen', '/vmove'],
        'info': ['/hello', '/ping', '/info', '/serverinfo', '/userinfo', '/avatar', '/membercount', '/admins', '/bots'],
        'level': ['/promotion', '/setuppromotion', '/leaderboard', '/addxp', '/setxp', '/setlevel'],
        'util': ['/calc', '/poll', '/afk', '/unafk', '/remindme', '/timestamp', '/color', '/qr-code', '/uptime',
                 '/giveaway'],
        'fun': ['/cat', '/roll', '/8ball', '/joke', '/fact', '/advice', '/quote', '/trivia', '/rps', '/flip'],
        'setup': ['/setup-logs', '/setup-welcome', '/setup-photowelcome', '/disable-welcome', '/setup-captcha',
                  '/disable-captcha', '/setup-ticket', '/setup-reportstaffticket', '/setup-partnershipticket',
                  '/create-application', '/list-applications', '/delete-application', '/invite', '/tech_work'],
        'misc': ['/help', '/lang']
    }

    if category and category in categories:
        cat = categories[category]
        name = cat['name_ru'] if lang == 'ru' else cat['name_en']
        cmds = commands_by_cat.get(category, [])

        embed = discord.Embed(
            title=f'{cat["emoji"]} **{name}**',
            description=get_text(str(interaction.guild_id), 'help_category_desc', len(cmds)),
            color=discord.Color.blue()
        )

        for j in range(0, len(cmds), 10):
            embed.add_field(
                name='‎',
                value=' '.join(cmds[j:j + 10]),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if category == 'all':
        embed = discord.Embed(
            title=get_text(str(interaction.guild_id), 'help_all_title'),
            description=get_text(str(interaction.guild_id), 'help_all_desc'),
            color=discord.Color.blue()
        )

        for cat_id, cat in categories.items():
            if cat_id in ['overview', 'all']:
                continue
            name = cat['name_ru'] if lang == 'ru' else cat['name_en']
            cmds = commands_by_cat.get(cat_id, [])
            embed.add_field(
                name=f'{cat["emoji"]} {name} ({len(cmds)})',
                value=' '.join(cmds[:8]) + ('...' if len(cmds) > 8 else ''),
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'help_title', 'bariier Bot'),
        description=get_text(str(interaction.guild_id), 'help_desc'),
        color=discord.Color.blue()
    )

    for cat_id, cat in categories.items():
        if cat_id in ['overview', 'all']:
            continue
        name = cat['name_ru'] if lang == 'ru' else cat['name_en']
        cmd_count = len(commands_by_cat.get(cat_id, []))
        embed.add_field(
            name=f'{cat["emoji"]} **{name}**',
            value=get_text(str(interaction.guild_id), 'help_cmd_count', cmd_count),
            inline=True
        )

    embed.set_footer(text=get_text(str(interaction.guild_id), 'help_footer'))

    class HelpSelect(discord.ui.Select):
        def __init__(self):
            options = []
            for cat_id, cat in categories.items():
                name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                if cat_id == 'overview':
                    desc = get_text(str(interaction.guild_id), 'help_select_overview_desc')
                elif cat_id == 'all':
                    desc = get_text(str(interaction.guild_id), 'help_select_all_desc')
                elif cat_id == 'mod':
                    desc = get_text(str(interaction.guild_id), 'help_select_mod_desc')
                elif cat_id == 'roles':
                    desc = get_text(str(interaction.guild_id), 'help_select_roles_desc')
                elif cat_id == 'voice':
                    desc = get_text(str(interaction.guild_id), 'help_select_voice_desc')
                elif cat_id == 'info':
                    desc = get_text(str(interaction.guild_id), 'help_select_info_desc')
                elif cat_id == 'level':
                    desc = get_text(str(interaction.guild_id), 'help_select_level_desc')
                elif cat_id == 'util':
                    desc = get_text(str(interaction.guild_id), 'help_select_util_desc')
                elif cat_id == 'fun':
                    desc = get_text(str(interaction.guild_id), 'help_select_fun_desc')
                elif cat_id == 'setup':
                    desc = get_text(str(interaction.guild_id), 'help_select_setup_desc')
                elif cat_id == 'misc':
                    desc = get_text(str(interaction.guild_id), 'help_select_misc_desc')
                else:
                    desc = ''

                options.append(discord.SelectOption(
                    label=name,
                    emoji=cat['emoji'],
                    value=cat_id,
                    description=desc
                ))

            super().__init__(
                placeholder=get_text(str(interaction.guild_id), 'help_select_placeholder'),
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, select_interaction: discord.Interaction):
            selected = self.values[0]

            if selected == 'overview':
                embed = discord.Embed(
                    title=get_text(str(select_interaction.guild_id), 'help_title', 'bariier Bot'),
                    description=get_text(str(select_interaction.guild_id), 'help_desc'),
                    color=discord.Color.blue()
                )
                for cat_id, cat in categories.items():
                    if cat_id in ['overview', 'all']:
                        continue
                    name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                    cmd_count = len(commands_by_cat.get(cat_id, []))
                    embed.add_field(
                        name=f'{cat["emoji"]} **{name}**',
                        value=get_text(str(select_interaction.guild_id), 'help_cmd_count', cmd_count),
                        inline=True
                    )
                embed.set_footer(text=get_text(str(select_interaction.guild_id), 'help_footer'))
                await select_interaction.response.edit_message(embed=embed, view=self.view)

            elif selected == 'all':
                embed = discord.Embed(
                    title=get_text(str(select_interaction.guild_id), 'help_all_title'),
                    description=get_text(str(select_interaction.guild_id), 'help_all_desc'),
                    color=discord.Color.blue()
                )
                for cat_id, cat in categories.items():
                    if cat_id in ['overview', 'all']:
                        continue
                    name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                    cmds = commands_by_cat.get(cat_id, [])
                    embed.add_field(
                        name=f'{cat["emoji"]} {name} ({len(cmds)})',
                        value=' '.join(cmds[:8]) + ('...' if len(cmds) > 8 else ''),
                        inline=False
                    )
                await select_interaction.response.edit_message(embed=embed, view=self.view)

            else:
                cat = categories[selected]
                name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                cmds = commands_by_cat.get(selected, [])

                embed = discord.Embed(
                    title=f'{cat["emoji"]} **{name}**',
                    description=get_text(str(select_interaction.guild_id), 'help_category_desc', len(cmds)),
                    color=discord.Color.blue()
                )

                for j in range(0, len(cmds), 10):
                    embed.add_field(
                        name='‎',
                        value=' '.join(cmds[j:j + 10]),
                        inline=False
                    )

                await select_interaction.response.edit_message(embed=embed, view=self.view)

    view = discord.ui.View(timeout=120)
    view.add_item(HelpSelect())

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    from datetime import datetime, timedelta, timezone


@bot.tree.command(name='autorole', description='Настроить автоматическую выдачу роли новым участникам')
@app_commands.choices(action=[
    app_commands.Choice(name='🔧 Включить', value='on'),
    app_commands.Choice(name='⚙️ Выключить', value='off'),
    app_commands.Choice(name='📊 Статус', value='status')
])
async def autorole(interaction: discord.Interaction, action: app_commands.Choice[str], role: discord.Role = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title=get_text(str(interaction.guild_id), 'autorole_no_permission'),
            description=get_text(str(interaction.guild_id), 'autorole_admin_only'),
            	color=discord.Color.from_rgb(255, 255, 255)
        )
        embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_access_denied'))
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    AUTOROLE_FILE = 'autorole_settings.json'

    def load_autorole():
        if os.path.exists(AUTOROLE_FILE):
            with open(AUTOROLE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_autorole(settings):
        with open(AUTOROLE_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)

    settings = load_autorole()
    gid = str(interaction.guild_id)

    if action.value == 'on':
        if role is None:
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_error_no_role'),
                description=get_text(str(interaction.guild_id), 'autorole_error_no_role_desc'),
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if role.permissions.administrator:
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_warning'),
                description=get_text(str(interaction.guild_id), 'autorole_no_admin_role'),
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        bot_member = interaction.guild.get_member(bot.user.id)
        if role.position >= bot_member.top_role.position:
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_error_role_higher'),
                description=get_text(str(interaction.guild_id), 'autorole_role_higher_desc', role.mention),
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        settings[gid] = {'enabled': True, 'role_id': role.id}
        save_autorole(settings)

        embed = discord.Embed(
            title=get_text(str(interaction.guild_id), 'autorole_enabled'),
            description=get_text(str(interaction.guild_id), 'autorole_enabled_desc', role.mention),
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_setup_by', interaction.user.name))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action.value == 'off':
        if gid in settings:
            settings[gid]['enabled'] = False
            save_autorole(settings)
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_disabled'),
                description=get_text(str(interaction.guild_id), 'autorole_disabled_desc'),
                color=discord.Color.orange()
            )
            embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_info'),
                description=get_text(str(interaction.guild_id), 'autorole_not_configured'),
                color=discord.Color.blue()
            )
            embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
            await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action.value == 'status':
        if gid in settings and settings[gid].get('enabled', False):
            role_id = settings[gid].get('role_id')
            role_obj = interaction.guild.get_role(role_id)
            if role_obj:
                embed = discord.Embed(
                    title=get_text(str(interaction.guild_id), 'autorole_status_title'),
                    description=get_text(str(interaction.guild_id), 'autorole_status_enabled', role_obj.mention, role_id),
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title=get_text(str(interaction.guild_id), 'autorole_status_title'),
                    description=get_text(str(interaction.guild_id), 'autorole_status_enabled_no_role'),
                    color=discord.Color.orange()
                )
        else:
            embed = discord.Embed(
                title=get_text(str(interaction.guild_id), 'autorole_status_title'),
                description=get_text(str(interaction.guild_id), 'autorole_status_disabled'),
                	color=discord.Color.from_rgb(255, 255, 255)
            )
        embed.set_footer(text=get_text(str(interaction.guild_id), 'autorole_footer'))
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-ticket', description='🎫 Настроить систему тикетов')
async def setup_ticket(interaction: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    save(TICKET_SETTINGS_FILE, {str(interaction.guild_id): {'category': category.id, 'role': support_role.id}})

    class TicketView(discord.ui.View):
        @discord.ui.button(label='🎫 Создать тикет', style=discord.ButtonStyle.primary)
        async def create(self, binteraction: discord.Interaction, button: discord.ui.Button):
            s = load(TICKET_SETTINGS_FILE).get(str(binteraction.guild_id), {})
            cat = binteraction.guild.get_channel(s.get('category'))
            role = binteraction.guild.get_role(s.get('role'))
            name = f'ticket-{binteraction.user.name.lower()}-{random.randint(100, 999)}'

            ow = {
                binteraction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                binteraction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

            ch = await binteraction.guild.create_text_channel(name, category=cat, overwrites=ow)

            embed = discord.Embed(
                title='🎫 Новый тикет',
                description=f'**От:** {binteraction.user.mention}\n**ID:** {binteraction.user.id}\n**Статус:** ⏳ Ожидает ответа',
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name='📝 Вопрос', value='Опишите вашу проблему...', inline=False)
            embed.set_footer(text=f'ID: {name} • bariier Bot')

            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                async def close(self, button_interaction: discord.Interaction, btn: discord.ui.Button):
                    if not button_interaction.user.guild_permissions.administrator and button_interaction.user.id != binteraction.user.id:
                        return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)

                    await button_interaction.response.send_message('🔒 Закрытие тикета...', ephemeral=True)
                    try:
                        await binteraction.user.send(f'✅ Ваш тикет **{name}** был закрыт.')
                    except:
                        pass
                    await asyncio.sleep(2)
                    await ch.delete()

                @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅')
                async def accept(self, button_interaction: discord.Interaction, btn: discord.ui.Button):
                    if not button_interaction.user.guild_permissions.administrator:
                        return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)

                    embed.color = discord.Color.green()
                    embed.description = f'**От:** {binteraction.user.mention}\n**Статус:** ✅ ПРИНЯТ В РАБОТУ'
                    embed.add_field(name='👨‍💻 Принял', value=button_interaction.user.mention, inline=False)
                    await button_interaction.message.edit(embed=embed, view=self)
                    await button_interaction.response.send_message('✅ Тикет принят в работу!', ephemeral=True)
                    try:
                        await binteraction.user.send(f'✅ Ваш тикет **{name}** принят в работу сотрудником {button_interaction.user.mention}')
                    except:
                        pass

                @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.secondary, emoji='❌')
                async def reject(self, button_interaction: discord.Interaction, btn: discord.ui.Button):
                    if not button_interaction.user.guild_permissions.administrator:
                        return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)

                    embed.color = discord.Color.red()
                    embed.description = f'**От:** {binteraction.user.mention}\n**Статус:** ❌ ОТКЛОНЁН'
                    embed.add_field(name='👨‍💻 Отклонил', value=button_interaction.user.mention, inline=False)
                    await button_interaction.message.edit(embed=embed, view=self)
                    await button_interaction.response.send_message('❌ Тикет отклонён!', ephemeral=True)
                    try:
                        await binteraction.user.send(f'❌ Ваш тикет **{name}** был отклонён.')
                    except:
                        pass

                @discord.ui.button(label='✏️ Ответить с сообщением', style=discord.ButtonStyle.primary, emoji='✏️')
                async def reply(self, button_interaction: discord.Interaction, btn: discord.ui.Button):
                    if not button_interaction.user.guild_permissions.administrator:
                        return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)

                    class ReplyModal(discord.ui.Modal):
                        def __init__(self):
                            super().__init__(title='📝 Ответ пользователю')
                            self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                               placeholder='Ваш ответ...', required=True))

                        async def on_submit(self, modal_interaction: discord.Interaction):
                            msg = self.children[0].value
                            embed.color = discord.Color.green()
                            embed.description = f'**От:** {binteraction.user.mention}\n**Статус:** ✅ ОТВЕЧЕНО'
                            embed.add_field(name='📝 Ответ сотрудника', value=msg, inline=False)
                            embed.add_field(name='👨‍💻 Ответил', value=modal_interaction.user.mention, inline=False)
                            await button_interaction.message.edit(embed=embed)
                            await modal_interaction.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                            try:
                                await binteraction.user.send(
                                    f'📩 Ответ на ваш тикет **{name}** от {modal_interaction.user.mention}:\n\n{msg}')
                            except:
                                pass

                    await button_interaction.response.send_modal(ReplyModal())

            await ch.send(embed=embed, view=TicketButtons())
            await binteraction.response.send_message(f'✅ Тикет создан: {ch.mention}', ephemeral=True)

    embed = discord.Embed(
        title='🎫 Система тикетов',
        description='Нажми на кнопку ниже, чтобы создать тикет.\nСотрудники ответят в ближайшее время.',
        color=discord.Color.blue()
    )
    embed.set_footer(text="bariier Bot | Поддержка")
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message('✅ Система тикетов настроена!', ephemeral=True)


@bot.tree.command(name='mute', description='Заглушить участника')
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int, rule: str, reason: str = "Не указана"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return

    # ... все ваши проверки прав ...

    until = discord.utils.utcnow() + timedelta(minutes=minutes)

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

    audit_reason = f"Модератор: {interaction.user} (ID: {interaction.user.id}) | Правило: {rule} | Причина: {reason}"

    try:
        await user.timeout(until, reason=audit_reason)

        embed = discord.Embed(
            title='🔇 Мут | Наказание',
            description=f'**{user.mention}** получил мут на `{time_text}`',
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name='📋 Правило', value=rule, inline=False)
        embed.add_field(name='📝 Причина', value=reason, inline=False)
        embed.add_field(name='👮 Модератор', value=interaction.user.mention, inline=False)
        embed.set_footer(text=f'ID: {user.id} • bariier Bot')

        await interaction.response.send_message(embed=embed)

        # 🔥 ЛОГ В КАНАЛ ЛОГОВ
        await send_mod_log(interaction.guild_id, "Мут", interaction.user, user, reason, rule, time_text)

    except discord.Forbidden:
        embed = discord.Embed(title="❌ Ошибка",
                              description=f"Не хватает прав для мута {user.mention}!\nПроверьте, что моя роль выше его роли.",
                              	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не удалось замутить пользователя: {str(e)[:100]}",
                              	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unmute', description='Снять мут с участника')
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    if member.timed_out_until is None:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_muted'), ephemeral=True)

    await member.timeout(None)

    embed = discord.Embed(
        title="🔊 Снятие мута",
        description=get_text(str(interaction.guild_id), 'unmuted', member.mention),
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
    embed.set_footer(text="bariier Bot | Модерация")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, "Снятие мута", interaction.user, member, "Мут снят")


@bot.tree.command(name='ban', description='Забанить участника')
async def ban(interaction: discord.Interaction, user: discord.Member, rule: str, reason: str = "Не указана"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)

    if user.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        return await interaction.response.send_message('❌ Нельзя забанить пользователя с ролью выше или равной вашей!',
                                             ephemeral=True)

    audit_reason = f"Модератор: {interaction.user} (ID: {interaction.user.id}) | Правило: {rule} | Причина: {reason}"
    await user.ban(reason=audit_reason)

    embed = discord.Embed(
        title='🔨 Бан | Наказание',
        description=f'{user.mention} был забанен',
        	color=discord.Color.from_rgb(255, 255, 255),
        timestamp=datetime.now()
    )
    embed.add_field(name='📋 Правило', value=rule, inline=False)
    embed.add_field(name='📝 Причина', value=reason, inline=False)
    embed.add_field(name='👮 Модератор', value=interaction.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id} • bariier Bot')

    await interaction.response.send_message(embed=embed)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, "Бан", interaction.user, user, reason, rule)

    try:
        await user.send(f'🔨 Вы были забанены на сервере **{interaction.guild.name}**\n📋 Правило: {rule}\n📝 Причина: {reason}')
    except:
        pass


@bot.tree.command(name='unban', description='Разбанить пользователя по ID')
async def unban(interaction: discord.Interaction, userid: str, reason: str = "Не указана"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)

    try:
        user_id = int(userid)
        user = await bot.fetch_user(user_id)

        banned = [entry async for entry in interaction.guild.bans()]
        if not any(str(entry.user.id) == userid for entry in banned):
            return await interaction.response.send_message(f'❌ Пользователь с ID `{userid}` не в бане!', ephemeral=True)

        await interaction.guild.unban(user, reason=reason)

        embed = discord.Embed(
            title='🔓 Разбан',
            description=f'{user.mention} был разбанен',
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name='📝 Причина', value=reason, inline=False)
        embed.add_field(name='👮 Модератор', value=interaction.user.mention, inline=False)
        embed.set_footer(text=f'ID: {user.id} • bariier Bot')

        await interaction.response.send_message(embed=embed)

        # 🔥 ЛОГ В КАНАЛ ЛОГОВ
        await send_mod_log(interaction.guild_id, "Разбан", interaction.user, user, reason)

    except ValueError:
        await interaction.response.send_message('❌ Неверный формат ID!', ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message(f'❌ Пользователь с ID `{userid}` не найден!', ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


@bot.tree.command(name='kick', description='Kick a member')
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    audit_reason = f"Модератор: {interaction.user} (ID: {interaction.user.id}) | Причина: {reason}"
    await member.kick(reason=audit_reason)

    embed = discord.Embed(
        title="👢 Кик",
        description=get_text(str(interaction.guild_id), 'kicked', member.mention),
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📝 Причина", value=reason)
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
    embed.set_footer(text="bariier Bot | Модерация")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, "Кик", interaction.user, member, reason)


@bot.tree.command(name='warn', description='Warn a member')
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    w = load(WARNS_FILE)
    gid, uid = str(interaction.guild_id), str(member.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    wid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': wid, 'reason': reason, 'mod': interaction.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)

    embed = discord.Embed(
        title="⚠️ Выдано предупреждение",
        description=get_text(str(interaction.guild_id), 'warned', member.mention, wid),
        color=discord.Color.yellow(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📝 Причина", value=reason)
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
    embed.set_footer(text=f"ID: {member.id} • bariier Bot")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, f"Предупреждение #{wid}", interaction.user, member, reason)


@bot.tree.command(name='warnings', description='Show warnings')
async def warnings(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(interaction.guild_id), {}).get(str(member.id), [])
    if not w:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_warnings', member.mention), ephemeral=True)
    e = discord.Embed(title=get_text(str(interaction.guild_id), 'warnings_title', member.name), description=get_text(str(interaction.guild_id), 'warnings_total', len(w)), color=0xe67e22)
    for ww in w[-5:]:
        mod = interaction.guild.get_member(ww['mod'])
        e.add_field(name=f"Warning #{ww['id']}", value=f"**Reason:** {ww['reason']}\n**Mod:** {mod.name if mod else 'Unknown'}", inline=False)
    e.set_footer(text="bariier Bot | Система предупреждений")
    await interaction.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topwarnings', description='Top warnings')
async def topwarnings(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(interaction.guild_id), {})
    if not w:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_warnings', ''), ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := interaction.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Top warnings', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} warnings', inline=False)
    e.set_footer(text="bariier Bot | Рейтинг")
    await interaction.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='unwarn', description='Снять предупреждение')
async def unwarn(interaction: discord.Interaction, member: discord.Member, warn_id: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    w = load(WARNS_FILE)
    gid, uid = str(interaction.guild_id), str(member.id)
    if gid not in w or uid not in w[gid]:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_warnings', member.mention), ephemeral=True)

    for idx, ww in enumerate(w[gid][uid]):
        if ww['id'] == warn_id:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)

            embed = discord.Embed(
                title="✅ Предупреждение снято",
                description=get_text(str(interaction.guild_id), 'warn_removed', warn_id),
                color=discord.Color.green()
            )
            embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
            embed.set_footer(text="bariier Bot | Модерация")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # 🔥 ЛОГ В КАНАЛ ЛОГОВ
            await send_mod_log(interaction.guild_id, f"Снятие предупреждения #{warn_id}", interaction.user, member, "Предупреждение снято")
            return

    await interaction.response.send_message(get_text(str(interaction.guild_id), 'warn_not_found', warn_id), ephemeral=True)


@bot.tree.command(name='slowmode', description='Set slowmode')
async def slowmode(interaction: discord.Interaction, channel: discord.TextChannel, seconds: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(title="🐢 Режим slowmode", description=get_text(str(interaction.guild_id), 'slowmode', seconds, channel.mention), color=discord.Color.blue(), timestamp=datetime.now())
    embed.set_footer(text="bariier Bot | Управление каналом")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='lock', description='Lock channel')
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=False)
    embed = discord.Embed(title="🔒 Канал заблокирован", description=get_text(str(interaction.guild_id), 'locked', channel.mention), 	color=discord.Color.from_rgb(255, 255, 255), timestamp=datetime.now())
    embed.set_footer(text="bariier Bot | Модерация")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unlock', description='Unlock channel')
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(interaction.guild.default_role, send_messages=None)
    embed = discord.Embed(title="🔓 Канал разблокирован", description=get_text(str(interaction.guild_id), 'unlocked', channel.mention), color=discord.Color.green(), timestamp=datetime.now())
    embed.set_footer(text="bariier Bot | Модерация")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='report', description='Report user')
async def report(interaction: discord.Interaction, user: discord.Member, reason: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    e = discord.Embed(title='📢 Report', description=f'{interaction.user.mention} reported {user.mention}', 	color=discord.Color.from_rgb(255, 255, 255))
    e.add_field(name='Reason', value=reason)
    e.set_footer(text="bariier Bot | Жалоба")
    await send_log(interaction.guild_id, e)
    await interaction.response.send_message(get_text(str(interaction.guild_id), 'report_sent'), ephemeral=True)


@bot.tree.command(name='pin', description='Pin message')
async def pin(interaction: discord.Interaction, message_id: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.pin()
        embed = discord.Embed(title="📌 Сообщение закреплено", description=get_text(str(interaction.guild_id), 'pinned'), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='unpin', description='Unpin message')
async def unpin(interaction: discord.Interaction, message_id: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.unpin()
        embed = discord.Embed(title="📌 Закрепление снято", description=get_text(str(interaction.guild_id), 'unpinned'), color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='vmute', description='Заглушить в голосовом канале')
async def vmute(interaction: discord.Interaction, user: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.mute_members:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)

    if not user.voice:
        return await interaction.response.send_message(f'❌ {user.mention} не в голосовом канале!', ephemeral=True)

    await user.edit(mute=True)

    embed = discord.Embed(title='🔇 Голосовой мут', description=f'{user.mention} заглушен в голосовом канале', color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name='👮 Модератор', value=interaction.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id} • bariier Bot')
    await interaction.response.send_message(embed=embed)
    await send_log(interaction.guild_id, embed)


@bot.tree.command(name='vunmute', description='Unmute in voice')
async def vunmute(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.mute_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(mute=False)
        embed = discord.Embed(title="🔊 Снятие голосового мута", description=get_text(str(interaction.guild_id), 'voice_unmuted', member.mention), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vdeafen', description='Deafen in voice')
async def vdeafen(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.deafen_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=True)
        embed = discord.Embed(title="🔇 Голосовая глухота", description=get_text(str(interaction.guild_id), 'voice_deafened', member.mention), color=discord.Color.orange())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vundeafen', description='Undeafen in voice')
async def vundeafen(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.deafen_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=False)
        embed = discord.Embed(title="🔊 Снятие голосовой глухоты", description=get_text(str(interaction.guild_id), 'voice_undeafened', member.mention), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vkick', description='Kick from voice')
async def vkick(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.move_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(None)
        embed = discord.Embed(title="🎤 Выгон из голосового", description=get_text(str(interaction.guild_id), 'voice_kicked', member.mention), 	color=discord.Color.from_rgb(255, 255, 255))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vmove', description='Move in voice')
async def vmove(interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.move_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(channel)
        embed = discord.Embed(title="🔊 Перемещение в голосовом", description=get_text(str(interaction.guild_id), 'voice_moved', member.mention, channel.name), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='serverinfo', description='Server info')
async def serverinfo(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    g = interaction.guild
    e = discord.Embed(
        title=get_text(str(interaction.guild_id), 'serverinfo_title', g.name),
        color=COLOR_BLUE,
        timestamp=datetime.now()
    )
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name=get_text(str(interaction.guild_id), 'serverinfo_owner'), value=g.owner.mention if g.owner else 'Unknown')
    e.add_field(name=get_text(str(interaction.guild_id), 'serverinfo_members'), value=g.member_count)
    e.add_field(name=get_text(str(interaction.guild_id), 'serverinfo_channels'), value=len(g.channels))
    e.add_field(name=get_text(str(interaction.guild_id), 'serverinfo_roles'), value=len(g.roles))
    e.set_footer(text=get_text(str(interaction.guild_id), 'serverinfo_footer', g.id))
    await interaction.response.send_message(embed=e)


@bot.tree.command(name='userinfo', description='User info')
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if await check_blacklist(interaction): return
    m = member or interaction.user
    e = discord.Embed(
        title=get_text(str(interaction.guild_id), 'userinfo_title', m.name),
        color=m.color if m.color else COLOR_BLUE,
        timestamp=datetime.now()
    )
    if m.avatar: e.set_thumbnail(url=m.avatar.url)
    e.add_field(name=get_text(str(interaction.guild_id), 'userinfo_id'), value=m.id)
    e.add_field(name=get_text(str(interaction.guild_id), 'userinfo_joined'),
                value=m.joined_at.strftime('%d.%m.%Y %H:%M') if m.joined_at else 'Unknown')
    e.add_field(name=get_text(str(interaction.guild_id), 'userinfo_created'),
                value=m.created_at.strftime('%d.%m.%Y %H:%M'))
    e.add_field(name=get_text(str(interaction.guild_id), 'userinfo_bot'), value='✅ Да' if m.bot else '❌ Нет')
    e.set_footer(text=get_text(str(interaction.guild_id), 'userinfo_footer'))
    await interaction.response.send_message(embed=e)


@bot.tree.command(name='avatar', description='Show avatar')
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    m = member or interaction.user
    e = discord.Embed(
        title=get_text(str(interaction.guild_id), 'avatar_title', m.name),
        color=COLOR_BLUE
    )
    e.set_image(url=m.display_avatar.url)
    e.set_footer(text=get_text(str(interaction.guild_id), 'avatar_footer'))
    await interaction.response.send_message(embed=e)


@bot.tree.command(name='admins', description='Server admins')
async def admins(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    admins_list = [m.mention for m in interaction.guild.members if m.guild_permissions.administrator]
    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'admins_title'),
        description=' '.join(admins_list) or get_text(str(interaction.guild_id), 'none'),
        color=discord.Color.gold()
    )
    embed.set_footer(text=get_text(str(interaction.guild_id), 'admins_footer'))
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='bots', description='Bots on server')
async def bots(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    bots_list = [m.mention for m in interaction.guild.members if m.bot]
    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'bots_title'),
        description=' '.join(bots_list) or get_text(str(interaction.guild_id), 'none'),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=get_text(str(interaction.guild_id), 'bots_footer'))
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='timeout', description='Timeout member')
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Not specified"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    audit_reason = f"Модератор: {interaction.user} (ID: {interaction.user.id}) | Причина: {reason}"
    await member.timeout(datetime.now() + timedelta(minutes=minutes), reason=audit_reason)

    time_text = f"{minutes} мин"

    embed = discord.Embed(
        title="⏰ Таймаут",
        description=get_text(str(interaction.guild_id), 'timeout_set', member.mention, minutes),
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="📝 Причина", value=reason)
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
    embed.set_footer(text="bariier Bot | Модерация")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, "Таймаут", interaction.user, member, reason, None, time_text)


@bot.tree.command(name='untimeout', description='Снять таймаут')
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    # Проверка, есть ли таймаут
    if member.timed_out_until is None:
        embed = discord.Embed(title="ℹ️ Информация", description="У пользователя нет активного таймаута!",
                              color=discord.Color.blue())
        embed.set_footer(text="bariier Bot | Модерация")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    await member.timeout(None)

    embed = discord.Embed(
        title="✅ Таймаут снят",
        description=get_text(str(interaction.guild_id), 'timeout_removed', member.mention),
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
    embed.set_footer(text="bariier Bot | Модерация")

    await interaction.response.send_message(embed=embed, ephemeral=True)

    # 🔥 ЛОГ В КАНАЛ ЛОГОВ
    await send_mod_log(interaction.guild_id, "Снятие таймаута", interaction.user, member, "Таймаут снят")


@bot.tree.command(name='softban', description='Softban')
async def softban(interaction: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await member.ban(reason=reason)
    await interaction.guild.unban(member, reason="Softban")
    embed = discord.Embed(title="🔄 Софтбан", description=get_text(str(interaction.guild_id), 'softbanned', member.mention), color=discord.Color.purple())
    embed.set_footer(text="bariier Bot | Модерация")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='authors', description='Показать список авторов и разработчиков бота')
async def authors(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    # Проверяем, не наступило ли 14 июня 2 часа ночи (день рождения Andy.wirus)
    now = datetime.now()
    birthday = datetime(now.year, 6, 14, 2, 0, 0)

    # Если сегодня 14 июня и время после 2 часов ночи
    if now.month == 6 and now.day == 14 and now.hour >= 2:
        birthday_text = "\n\n**🎉 С ДНЁМ РОЖДЕНИЯ, ANDY.WIRUS! 🎉**\n*Желаем счастья, здоровья и успехов!*"
    else:
        birthday_text = ""

    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'authors_title'),
        description=get_text(str(interaction.guild_id), 'authors_desc') + birthday_text,
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name=get_text(str(interaction.guild_id), 'authors_ceo'),
        value=get_text(str(interaction.guild_id), 'authors_ceo_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(interaction.guild_id), 'authors_moderators'),
        value=get_text(str(interaction.guild_id), 'authors_moderators_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(interaction.guild_id), 'authors_coder'),
        value=get_text(str(interaction.guild_id), 'authors_coder_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(interaction.guild_id), 'authors_support'),
        value=get_text(str(interaction.guild_id), 'authors_support_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(interaction.guild_id), 'authors_thanks'),
        value=get_text(str(interaction.guild_id), 'authors_thanks_value'),
        inline=False
    )

    embed.set_footer(text=get_text(str(interaction.guild_id), 'authors_footer'))
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='massban', description='Mass ban')
async def massban(interaction: discord.Interaction, ids: str, reason: str = "Not specified"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    ids_list = ids.split()
    count = 0
    for uid in ids_list:
        try:
            user = await bot.fetch_user(int(uid))
            await interaction.guild.ban(user, reason=reason)
            count += 1
        except:
            pass
    embed = discord.Embed(title="🔨 Масс-бан", description=get_text(str(interaction.guild_id), 'massbanned', count), 	color=discord.Color.from_rgb(255, 255, 255))
    embed.set_footer(text="bariier Bot | Модерация")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='clean', description='Clean bot messages')
async def clean(interaction: discord.Interaction, amount: int = 10):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    deleted = 0
    async for msg in i.channel.history(limit=amount):
        if msg.author == bot.user:
            await msg.delete()
            deleted += 1
    embed = discord.Embed(title="🧹 Очистка сообщений", description=get_text(str(interaction.guild_id), 'bot_messages_deleted', deleted), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Утилиты")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='strike', description='Give strike')
async def strike(interaction: discord.Interaction, user: discord.Member, reason: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE)
    gid, uid = str(interaction.guild_id), str(user.id)
    if gid not in w: w[gid] = {}
    if uid not in w[gid]: w[gid][uid] = []
    sid = len(w[gid][uid]) + 1
    w[gid][uid].append({'id': sid, 'reason': reason, 'mod': interaction.user.id, 'date': datetime.now().isoformat()})
    save(WARNS_FILE, w)
    embed = discord.Embed(title="⚠️ Страйк выдан", description=get_text(str(interaction.guild_id), 'strike_given', user.mention, sid), color=discord.Color.orange())
    embed.add_field(name="📝 Причина", value=reason)
    embed.set_footer(text="bariier Bot | Модерация")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unstrike', description='Снять страйк')
async def unstrike(interaction: discord.Interaction, user: discord.Member, sid: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    w = load(WARNS_FILE)
    gid, uid = str(interaction.guild_id), str(user.id)
    if gid not in w or uid not in w[gid]:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_strikes', user.mention), ephemeral=True)

    for idx, s in enumerate(w[gid][uid]):
        if s['id'] == sid:
            w[gid][uid].pop(idx)
            save(WARNS_FILE, w)

            embed = discord.Embed(
                title="✅ Страйк снят",
                description=get_text(str(interaction.guild_id), 'strike_removed', sid, user.mention),
                color=discord.Color.green()
            )
            embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
            embed.set_footer(text="bariier Bot | Модерация")

            await interaction.response.send_message(embed=embed, ephemeral=True)

            # 🔥 ЛОГ В КАНАЛ ЛОГОВ
            await send_mod_log(interaction.guild_id, f"Снятие страйка #{sid}", interaction.user, user, "Страйк снят")
            return

    await interaction.response.send_message(get_text(str(interaction.guild_id), 'strike_not_found', sid), ephemeral=True)


@bot.tree.command(name='strikes', description='Show strikes')
async def strikes(interaction: discord.Interaction, user: discord.Member):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(interaction.guild_id), {}).get(str(user.id), [])
    if not w:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_strikes', user.mention), ephemeral=True)
    e = discord.Embed(title=f'⚠️ Страйки пользователя {user.name}', description=f'Всего: {len(w)}', color=0xe67e22)
    for s in w[-5:]:
        mod = interaction.guild.get_member(s['mod'])
        e.add_field(name=f"Страйк #{s['id']}", value=f"Причина: {s['reason']}\nМодератор: {mod.name if mod else 'Unknown'}", inline=False)
    e.set_footer(text="bariier Bot | Система страйков")
    await interaction.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topstrikes', description='Top strikes')
async def topstrikes(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(interaction.guild_id), {})
    if not w: return await interaction.response.send_message('Нет страйков', ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := interaction.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Топ страйков', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} страйков', inline=False)
    e.set_footer(text="bariier Bot | Рейтинг")
    await interaction.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='setnick', description='Set nickname')
async def setnick(interaction: discord.Interaction, member: discord.Member, nick: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_nicknames:
        embed = discord.Embed(title="❌ Ошибка", description=get_text(str(interaction.guild_id), 'no_permission'), 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if len(nick) > 32:
        embed = discord.Embed(title="❌ Ошибка", description=f"Никнейм не может быть длиннее **32 символов**!\nТвой никнейм: `{nick}` ({len(nick)} символов)", 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if not nick.strip():
        embed = discord.Embed(title="❌ Ошибка", description="Никнейм не может быть пустым!", 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    try:
        await member.edit(nick=nick)
        embed = discord.Embed(title="✏️ Смена никнейма", description=get_text(str(interaction.guild_id), 'nickname_set', member.mention, nick), color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
        embed.set_footer(text=f"ID: {member.id} • bariier Bot")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        log_embed = discord.Embed(title="✏️ Смена никнейма", description=f"{member.mention} изменил никнейм", color=discord.Color.blue(), timestamp=datetime.now())
        log_embed.add_field(name="Новый никнейм", value=nick, inline=False)
        log_embed.add_field(name="👮 Модератор", value=interaction.user.mention, inline=False)
        log_embed.set_footer(text=f"ID: {member.id}")
        await send_log(interaction.guild_id, log_embed)

    except discord.Forbidden:
        embed = discord.Embed(title="❌ Ошибка", description="У меня нет прав менять никнейм этому пользователю!\n(Возможно, его роль выше моей)", 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не удалось изменить никнейм: {str(e)[:100]}", 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Модерация")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setupantinuke', description='Setup antinuke')
async def setupantinuke(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    embed = discord.Embed(title="🛡️ Анти-нук", description=get_text(str(interaction.guild_id), 'antinuke_configured'), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Защита")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='addrole', description='Add role')
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await member.add_roles(role)
    embed = discord.Embed(title="➕ Выдача роли", description=get_text(str(interaction.guild_id), 'role_added', role.mention, member.mention), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Управление ролями")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='removerole', description='Remove role')
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await member.remove_roles(role)
    embed = discord.Embed(title="➖ Снятие роли", description=get_text(str(interaction.guild_id), 'role_removed', role.mention, member.mention), color=discord.Color.orange())
    embed.set_footer(text="bariier Bot | Управление ролями")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='createrole', description='Create role')
async def createrole(interaction: discord.Interaction, name: str, color: str = "default"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    cols = {'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff, 'yellow': 0xffff00, 'purple': 0xff00ff, 'default': 0x99aab5}
    r = await interaction.guild.create_role(name=name, color=cols.get(color, 0x99aab5))
    embed = discord.Embed(title="✨ Создание роли", description=get_text(str(interaction.guild_id), 'role_created', r.mention), color=discord.Color.green())
    embed.add_field(name="🎨 Цвет", value=color, inline=True)
    embed.set_footer(text="bariier Bot | Управление ролями")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='deleterole', description='Delete role')
async def deleterole(interaction: discord.Interaction, role: discord.Role):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await role.delete()
    embed = discord.Embed(title="🗑️ Удаление роли", description=get_text(str(interaction.guild_id), 'role_deleted'), 	color=discord.Color.from_rgb(255, 255, 255))
    embed.set_footer(text="bariier Bot | Управление ролями")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='reactionrole', description='Reaction role')
async def reactionrole(interaction: discord.Interaction, msg_id: str, role: discord.Role, emoji: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(msg_id))
        await msg.add_reaction(emoji)
        rr = load(REACTION_ROLES_FILE)
        rr[f"{interaction.guild_id}_{msg_id}_{emoji}"] = role.id
        save(REACTION_ROLES_FILE, rr)
        embed = discord.Embed(title="⚙️ Роль по реакции", description=get_text(str(interaction.guild_id), 'reaction_role_set', emoji, role.mention), color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'error', 'Message not found'), ephemeral=True)


@bot.tree.command(name='createchannel', description='Create channel')
async def createchannel(interaction: discord.Interaction, name: str, category: discord.CategoryChannel = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await interaction.guild.create_text_channel(name, category=category)
    embed = discord.Embed(title="#️⃣ Создание канала", description=get_text(str(interaction.guild_id), 'channel_created', name), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='deletechannel', description='Delete channel')
async def deletechannel(interaction: discord.Interaction, ch: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await ch.delete()
    embed = discord.Embed(title="#️⃣ Удаление канала", description=get_text(str(interaction.guild_id), 'channel_deleted'), 	color=discord.Color.from_rgb(255, 255, 255))
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='clonechannel', description='Clone channel')
async def clonechannel(interaction: discord.Interaction, ch: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await ch.clone()
    embed = discord.Embed(title="#️⃣ Клонирование канала", description=get_text(str(interaction.guild_id), 'channel_cloned', ch.name), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='movechannel', description='Move channel')
async def movechannel(interaction: discord.Interaction, ch: discord.TextChannel, pos: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    await ch.edit(position=pos)
    embed = discord.Embed(title="#️⃣ Перемещение канала", description=get_text(str(interaction.guild_id), 'channel_moved', ch.name, pos), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


level_data = {}


@bot.tree.command(name='promotion', description='Your level')
async def promotion(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    uid = str(interaction.user.id)
    lvl = level_data.get(uid, {}).get('level', 0)
    xp = level_data.get(uid, {}).get('xp', 0)
    embed = discord.Embed(title="📊 Ваш прогресс", description=get_text(str(interaction.guild_id), 'promotion_level', lvl, xp), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Система уровней")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setuppromotion', description='Setup leveling')
async def setuppromotion(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    embed = discord.Embed(title="⚙️ Настройка уровней", description=get_text(str(interaction.guild_id), 'settings_saved'), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='leaderboard', description='Level leaderboard')
async def leaderboard(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    sorted_users = sorted(level_data.items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:10]
    text = ''
    for idx, (uid, data) in enumerate(sorted_users, 1):
        m = interaction.guild.get_member(int(uid))
        if m:
            text += f'{idx}. {m.name} - Level {data.get("level", 0)} ({data.get("xp", 0)} XP)\n'
    if not text:
        text = 'Нет данных'
    e = discord.Embed(title=get_text(str(interaction.guild_id), 'leaderboard_title'), description=text, color=0x3498db)
    e.set_footer(text="bariier Bot | Рейтинг")
    await interaction.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='addxp', description='Add XP')
async def addxp(interaction: discord.Interaction, member: discord.Member, xp: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] += xp
    embed = discord.Embed(title="✨ Добавление XP", description=get_text(str(interaction.guild_id), 'xp_added', xp, member.mention), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setxp', description='Set XP')
async def setxp(interaction: discord.Interaction, member: discord.Member, xp: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] = xp
    embed = discord.Embed(title="🔧 Установка XP", description=get_text(str(interaction.guild_id), 'xp_set', xp, member.mention), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setlevel', description='Set level')
async def setlevel(interaction: discord.Interaction, member: discord.Member, lvl: int):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['level'] = lvl
    embed = discord.Embed(title="🔧 Установка уровня", description=get_text(str(interaction.guild_id), 'level_set', lvl, member.mention), color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='calc', description='Calculate')
async def calc(interaction: discord.Interaction, expression: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    try:
        res = eval(expression.replace('^', '**'))
        embed = discord.Embed(title="🧮 Калькулятор", description=get_text(str(interaction.guild_id), 'calc_result', expression, res), color=discord.Color.green())
        embed.set_footer(text="bariier Bot | Утилиты")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'calc_invalid'), ephemeral=True)


@bot.tree.command(name='poll', description='Create a poll')
async def poll(interaction: discord.Interaction, question: str, opt1: str, opt2: str, opt3: str = None, opt4: str = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    opts = [opt1, opt2]
    if opt3: opts.append(opt3)
    if opt4: opts.append(opt4)
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    e = discord.Embed(title=f'📊 Голосование: {question}', color=0x3498db, timestamp=datetime.now())
    for idx, opt in enumerate(opts):
        e.add_field(name=f'{emojis[idx]} {opt}', value='0 голосов', inline=False)
    e.set_footer(text=f"Автор: {interaction.user.name} • bariier Bot")
    msg = await i.channel.send(embed=e)
    for idx in range(len(opts)):
        await msg.add_reaction(emojis[idx])
    embed = discord.Embed(title="✅ Голосование создано", description=get_text(str(interaction.guild_id), 'poll_created'), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


afk_data = {}


@bot.tree.command(name='afk', description='Set AFK')
async def afk(interaction: discord.Interaction, reason: str = "AFK"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    afk_data[str(interaction.user.id)] = reason
    embed = discord.Embed(title="💤 AFK режим", description=get_text(str(interaction.guild_id), 'afk_set', interaction.user.mention, reason), color=discord.Color.orange())
    embed.set_footer(text="bariier Bot | AFK")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unafk', description='Remove AFK')
async def unafk(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if str(interaction.user.id) in afk_data:
        del afk_data[str(interaction.user.id)]
        embed = discord.Embed(title="✅ AFK снят", description=get_text(str(interaction.guild_id), 'afk_removed'), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'not_afk'), ephemeral=True)


@bot.tree.command(name='remindme', description='Set reminder')
async def remindme(interaction: discord.Interaction, time: str, reminder: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    try:
        unit = time[-1]
        amount = int(time[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        embed = discord.Embed(title="⏰ Напоминание установлено", description=get_text(str(interaction.guild_id), 'reminder_set', time), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await asyncio.sleep(sec)
        await interaction.user.send(f'⏰ **Напоминание:** {reminder}')
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'reminder_invalid'), ephemeral=True)


@bot.tree.command(name='timestamp', description='Current timestamp')
async def timestamp(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    embed = discord.Embed(title="🕐 Текущий timestamp", description=get_text(str(interaction.guild_id), 'timestamp_current', int(datetime.now().timestamp())), color=discord.Color.blue())
    embed.set_footer(text="bariier Bot | Утилиты")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='color', description='Color info')
async def color(interaction: discord.Interaction, hex_code: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    try:
        color = int(hex_code.strip('#'), 16)
        e = discord.Embed(title=get_text(str(interaction.guild_id), 'color_info', hex_code), color=color)
        e.add_field(name='RGB', value=f'{(color >> 16) & 255}, {(color >> 8) & 255}, {color & 255}')
        e.set_footer(text="bariier Bot | Информация о цвете")
        await interaction.response.send_message(embed=e)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'error', 'Invalid hex'), ephemeral=True)


@bot.tree.command(name='qr-code', description='Generate QR code')
async def qr_code(interaction: discord.Interaction, text: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
    e = discord.Embed(title=get_text(str(interaction.guild_id), 'qr_code_title'), color=0x3498db)
    e.set_image(url=url)
    e.set_footer(text="bariier Bot | QR Генератор")
    await interaction.response.send_message(embed=e)


start_time = datetime.now()


@bot.tree.command(name='uptime', description='Bot uptime')
async def uptime(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    delta = datetime.now() - start_time
    embed = discord.Embed(title="🕐 Время работы бота", description=get_text(str(interaction.guild_id), 'uptime_text', delta.days, delta.seconds // 3600, (delta.seconds % 3600) // 60), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Статистика")
    await interaction.response.send_message(embed=embed)


giveaways = {}


@bot.tree.command(name='giveaway', description='Start a giveaway')
async def giveaway(interaction: discord.Interaction, duration: str, prize: str, winners: int = 1):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        e = discord.Embed(title='🎁 Розыгрыш', description=f'**Приз:** {prize}\n**Победителей:** {winners}\n**Длительность:** {duration}', color=0x00ff00, timestamp=datetime.now())
        e.set_footer(text="bariier Bot | Удачи!")
        msg = await i.channel.send(embed=e)
        await msg.add_reaction('🎉')
        giveaways[str(msg.id)] = {'channel': i.channel.id, 'prize': prize, 'winners': winners, 'end': datetime.now() + timedelta(seconds=sec)}
        embed = discord.Embed(title="✅ Розыгрыш запущен", description=get_text(str(interaction.guild_id), 'giveaway_started'), color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        await interaction.response.send_message(get_text(str(interaction.guild_id), 'invalid_time'), ephemeral=True)


@bot.tree.command(name='cat', description='Random cat')
async def cat(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.thecatapi.com/v1/images/search') as r:
            data = await r.json()
            e = discord.Embed(title=get_text(str(interaction.guild_id), 'cat_title'), color=0x3498db)
            e.set_image(url=data[0]['url'])
            e.set_footer(text="bariier Bot | Котики")
            await interaction.response.send_message(embed=e)


@bot.tree.command(name='roll', description='Roll dice')
async def roll(interaction: discord.Interaction, sides: int = 6):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    result = random.randint(1, sides)
    embed = discord.Embed(title="🎲 Бросок кубика", description=get_text(str(interaction.guild_id), 'roll_result', result, sides), color=discord.Color.blue())
    embed.set_footer(text="bariier Bot | Игры")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='8ball', description='Magic 8ball')
async def eightball(interaction: discord.Interaction, question: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return

    answers_ru = [
        'Да', 'Нет', 'Возможно', 'Определённо да!',
        'Маловероятно', 'Спроси позже', 'Конечно!', 'Никогда',
        'Да, безусловно', 'Перспективы хорошие', 'Знаки говорят да',
        'Пока не ясно', 'Сосредоточься и спроси еще раз', 'Лучше не сейчас',
        'Мой ответ нет', 'Весьма сомнительно'
    ]

    answers_en = [
        'Yes', 'No', 'Maybe', 'Definitely yes!',
        'Unlikely', 'Ask later', 'Of course!', 'Never',
        'Yes, definitely', 'Outlook good', 'Signs point to yes',
        'Cannot predict now', 'Concentrate and ask again', 'Better not tell you now',
        'My reply is no', 'Very doubtful'
    ]

    lang = get_lang(str(interaction.guild_id))
    answers = answers_ru if lang == 'ru' else answers_en

    embed = discord.Embed(
        title=get_text(str(interaction.guild_id), 'eightball_title'),
        description=get_text(str(interaction.guild_id), 'eightball_result', random.choice(answers)),
        color=discord.Color.purple()
    )
    embed.add_field(name=get_text(str(interaction.guild_id), 'eightball_question'), value=question, inline=False)
    embed.set_footer(text=get_text(str(interaction.guild_id), 'eightball_footer'))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='joke', description='Random joke')
async def joke(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://v2.jokeapi.dev/joke/Any?safe-mode') as r:
            data = await r.json()
            if data['type'] == 'single':
                embed = discord.Embed(title="😂 Шутка", description=data["joke"], color=discord.Color.green())
            else:
                embed = discord.Embed(title="😂 Шутка", description=f'{data["setup"]}\n\n||{data["delivery"]}||', color=discord.Color.green())
            embed.set_footer(text="bariier Bot | Юмор")
            await interaction.response.send_message(embed=embed)


@bot.tree.command(name='fact', description='Random fact')
async def fact(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://uselessfacts.jsph.pl/random.json?language=en') as r:
            data = await r.json()
            embed = discord.Embed(title="📖 Случайный факт", description=data["text"], color=discord.Color.blue())
            embed.set_footer(text="bariier Bot | Интересно")
            await interaction.response.send_message(embed=embed)


@bot.tree.command(name='advice', description='Random advice')
async def advice(interaction: discord.Interaction):
    i = interaction

    if tech_work_active and i.user.id != YOUR_ID:
        await i.response.send_message("🔧 Техработы", ephemeral=True)
        return

    if await check_blacklist(i): return

    # Запасные советы на случай, если API не работает
    fallback_advice = [
        "Пей больше воды 💧",
        "Высыпайся 😴",
        "Делай зарядку по утрам 🏃",
        "Читай книги 📚",
        "Будь вежлив с окружающими 🤝",
        "Не откладывай на завтра то, что можно сделать сегодня ⏰",
        "Улыбайся чаще 😊",
        "Цени время ⌛",
        "Учись новому каждый день 📖",
        "Будь благодарен за то, что имеешь 🙏"
    ]

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get('https://api.adviceslip.com/advice', timeout=5) as r:
                if r.status == 200:
                    try:
                        data = await r.json()
                        advice_text = data["slip"]["advice"]
                    except:
                        advice_text = random.choice(fallback_advice)
                else:
                    advice_text = random.choice(fallback_advice)
    except:
        advice_text = random.choice(fallback_advice)

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'advice_title'),
        description=advice_text,
        color=discord.Color.gold()
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'advice_footer'))
    await i.response.send_message(embed=embed)


@bot.tree.command(name='quote', description='Random quote')
async def quote(interaction: discord.Interaction):
    i = interaction

    if tech_work_active and i.user.id != YOUR_ID:
        await i.response.send_message("🔧 Техработы", ephemeral=True)
        return

    if await check_blacklist(i): return

    # Запасные цитаты
    fallback_quotes = [
        "Будь изменением, которое хочешь видеть в мире - Махатма Ганди",
        "Жизнь - это то, что с тобой происходит, пока ты строишь планы - Джон Леннон",
        "Не суди о каждом дне по собранному урожаю, а по посеянным семенам - Роберт Стивенсон",
        "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма - Уинстон Черчилль",
        "Единственный способ сделать великую работу - любить то, что ты делаешь - Стив Джобс",
        "Будущее зависит от того, что ты делаешь сегодня - Махатма Ганди",
        "Сложнее всего начать действовать, остальное зависит только от упорства - Амелия Эрхарт",
        "Верь в себя и ты будешь непобедим - -",
        "Не ждите идеального момента, возьмите момент и сделайте его идеальным - -",
        "Твоё время ограничено, не трать его на чужую жизнь - Стив Джобс"
    ]

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get('https://api.quotable.io/random', timeout=5) as r:
                if r.status == 200:
                    try:
                        data = await r.json()
                        quote_text = f'"{data["content"]}"\n- **{data["author"]}**'
                    except:
                        quote_text = random.choice(fallback_quotes)
                else:
                    quote_text = random.choice(fallback_quotes)
    except:
        quote_text = random.choice(fallback_quotes)

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'quote_title'),
        description=quote_text,
        color=discord.Color.purple()
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'quote_footer'))
    await i.response.send_message(embed=embed)


# ========== ПЕРЕВОДЫ ДЛЯ СТАТИСТИКИ ==========
STATS_LANGUAGES = {
    'ru': {
        'all_members': 'Все участники',
        'members': 'Участники',
        'bots': 'Боты',
        'online': 'Онлайн',
        'boosts': 'Бусты',
        'level_boosts': 'Уровень бустов',
        'category_name': '📊 СТАТИСТИКА СЕРВЕРА'
    },
    'en': {
        'all_members': 'All members',
        'members': 'Members',
        'bots': 'Bots',
        'online': 'Online',
        'boosts': 'Boosts',
        'level_boosts': 'Level boosts',
        'category_name': '📊 SERVER STATS'
    },
    'es': {
        'all_members': 'Todos los miembros',
        'members': 'Miembros',
        'bots': 'Bots',
        'online': 'En línea',
        'boosts': 'Impulsos',
        'level_boosts': 'Nivel de impulsos',
        'category_name': '📊 ESTADÍSTICAS DEL SERVIDOR'
    },
    'fr': {
        'all_members': 'Tous les membres',
        'members': 'Membres',
        'bots': 'Bots',
        'online': 'En ligne',
        'boosts': 'Boosts',
        'level_boosts': 'Niveau des boosts',
        'category_name': '📊 STATISTIQUES DU SERVEUR'
    },
    'de': {
        'all_members': 'Alle Mitglieder',
        'members': 'Mitglieder',
        'bots': 'Bots',
        'online': 'Online',
        'boosts': 'Boosts',
        'level_boosts': 'Boost-Level',
        'category_name': '📊 SERVER-STATISTIK'
    }
}


async def update_stats_channels():
    STATS_FILE = 'stats_channels.json'
    if not os.path.exists(STATS_FILE):
        return
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
    except Exception:
        return

    for guild_id_str, data in all_data.items():
        guild = bot.get_guild(int(guild_id_str))
        if not guild:
            continue
        lang = data.get('language', 'en')
        texts = STATS_LANGUAGES.get(lang, STATS_LANGUAGES['en'])

        async def rename(ch_id, new_name):
            ch = guild.get_channel(ch_id)
            if ch and ch.name != new_name:
                try:
                    await ch.edit(name=new_name)
                except Exception:
                    pass

        if 'members' in data:
            await rename(data['members'], f"{texts['all_members']}: {guild.member_count}")
        if 'humans' in data:
            humans_count = len([m for m in guild.members if not m.bot])
            await rename(data['humans'], f"{texts['members']}: {humans_count}")
        if 'bots' in data:
            bots_count = len([m for m in guild.members if m.bot])
            await rename(data['bots'], f"{texts['bots']}: {bots_count}")
        if 'online' in data:
            online_count = len([m for m in guild.members if m.status != discord.Status.offline and not m.bot])
            await rename(data['online'], f"{texts['online']}: {online_count}")
        if 'boosts' in data:
            await rename(data['boosts'], f"{texts['boosts']}: {guild.premium_subscription_count or 0}")
        if 'level' in data:
            await rename(data['level'], f"{texts['level_boosts']}: {guild.premium_tier}")


@bot.tree.command(name='setup-stats', description='📊 Создать голосовые каналы со статистикой сервера')
@app_commands.describe(
    language="Язык для названий каналов",
    category="Категория для каналов",
    members="All members",
    humans="Members",
    bots="Bots",
    online="Online",
    boosts="Boosts",
    level="Level boosts"
)
@app_commands.choices(language=[
    app_commands.Choice(name='🇷🇺 Русский', value='ru'),
    app_commands.Choice(name='🇬🇧 English', value='en'),
    app_commands.Choice(name='🇪🇸 Español', value='es'),
    app_commands.Choice(name='🇫🇷 Français', value='fr'),
    app_commands.Choice(name='🇩🇪 Deutsch', value='de')
])
async def setup_stats(
        interaction: discord.Interaction,
        language: app_commands.Choice[str],
        category: discord.CategoryChannel = None,
        members: bool = True,
        humans: bool = True,
        bots: bool = True,
        online: bool = True,
        boosts: bool = True,
        level: bool = True
):
    i = interaction
    lang = language.value
    texts = STATS_LANGUAGES.get(lang, STATS_LANGUAGES['en'])

    if tech_work_active and i.user.id != YOUR_ID:
        await i.response.send_message("🔧 Техработы", ephemeral=True)
        return

    if not i.user.guild_permissions.administrator:
        await i.response.send_message("❌ Нужны права администратора!", ephemeral=True)
        return

    if category is None:
        category = await i.guild.create_category(texts['category_name'])

    overwrites = {
        i.guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)
    }

    created_channels = []
    stats_data = {'guild_id': i.guild.id, 'category_id': category.id, 'language': lang}

    if members:
        ch = await category.create_voice_channel(
            f"{texts['all_members']}: {i.guild.member_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['all_members']}")
        stats_data['members'] = ch.id

    if humans:
        humans_count = len([m for m in i.guild.members if not m.bot])
        ch = await category.create_voice_channel(
            f"{texts['members']}: {humans_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['members']}")
        stats_data['humans'] = ch.id

    if bots:
        bots_count = len([m for m in i.guild.members if m.bot])
        ch = await category.create_voice_channel(
            f"{texts['bots']}: {bots_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['bots']}")
        stats_data['bots'] = ch.id

    if online:
        online_count = len([m for m in i.guild.members if m.status != discord.Status.offline and not m.bot])
        ch = await category.create_voice_channel(
            f"{texts['online']}: {online_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['online']}")
        stats_data['online'] = ch.id

    if boosts:
        boost_count = i.guild.premium_subscription_count or 0
        ch = await category.create_voice_channel(
            f"{texts['boosts']}: {boost_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['boosts']}")
        stats_data['boosts'] = ch.id

    if level:
        level_count = i.guild.premium_tier
        ch = await category.create_voice_channel(
            f"{texts['level_boosts']}: {level_count}",
            overwrites=overwrites
        )
        created_channels.append(f"{texts['level_boosts']}")
        stats_data['level'] = ch.id

    STATS_FILE = 'stats_channels.json'

    def save_stats(data):
        all_data = {}
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        all_data[str(i.guild.id)] = data
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

    save_stats(stats_data)

    lang_flag = {
        'ru': '🇷🇺',
        'en': '🇬🇧',
        'es': '🇪🇸',
        'fr': '🇫🇷',
        'de': '🇩🇪'
    }.get(lang, '🌐')

    embed = discord.Embed(
        title="📊 Голосовая статистика создана",
        description=f"{lang_flag} **Язык:** {language.name}\n"
                    f"📁 **Категория:** {category.mention}\n\n"
                    f"✅ **Создано каналов:** {len(created_channels)}\n"
                    f"└ " + "\n└ ".join(created_channels),
        color=discord.Color.green()
    )
    embed.set_footer(text="Статистика будет обновляться автоматически")

    await i.response.send_message(embed=embed, ephemeral=True)

    await update_stats_channels()


@bot.tree.command(name='trivia', description='Trivia question')
async def trivia(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://opentdb.com/api.php?amount=1&type=multiple') as r:
            data = await r.json()
            q = data['results'][0]
            embed = discord.Embed(title="❓ Викторина", description=get_text(str(interaction.guild_id), 'trivia_question', q['question'], q['difficulty']), color=discord.Color.blue())
            embed.set_footer(text="bariier Bot | Викторины")
            await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='rps', description='Rock Paper Scissors')
async def rps(interaction: discord.Interaction, choice: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    choices = ['rock', 'paper', 'scissors']
    if choice.lower() not in choices:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'error', 'Choose: rock, paper, scissors'), ephemeral=True)
    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = get_text(str(interaction.guild_id), 'rps_tie')
    elif (choice.lower() == 'rock' and bot_choice == 'scissors') or (choice.lower() == 'paper' and bot_choice == 'rock') or (choice.lower() == 'scissors' and bot_choice == 'paper'):
        result = get_text(str(interaction.guild_id), 'rps_win')
    else:
        result = get_text(str(interaction.guild_id), 'rps_lose')
    embed = discord.Embed(title="✊ Камень, ножницы, бумага", description=f'Вы выбрали **{choice}**, я выбрал **{bot_choice}**.\n{result}', color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Игры")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='flip', description='Flip coin')
async def flip(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    result = random.choice([get_text(str(interaction.guild_id), 'flip_heads'), get_text(str(interaction.guild_id), 'flip_tails')])
    embed = discord.Embed(title="🪙 Монетка", description=f'Выпал **{result}**!', color=discord.Color.blue())
    embed.set_footer(text="bariier Bot | Игры")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='setup-logs', description='Setup logging channel')
async def setup_logs(interaction: discord.Interaction, channel: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    save(LOGS_SETTINGS_FILE, {str(interaction.guild_id): channel.id})

    embed = discord.Embed(title="📋 Настройка логов", description=get_text(str(interaction.guild_id), 'log_channel_set', channel.mention), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Логирование")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-welcome', description='Setup welcome message')
async def setup_welcome(interaction: discord.Interaction, channel: discord.TextChannel, message: str = "Welcome {member}!"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    s = load(WELCOME_SETTINGS_FILE)
    gid = str(interaction.guild_id)
    if gid not in s:
        s[gid] = {}

    s[gid]['welcome_enabled'] = True
    s[gid]['welcome_channel_id'] = channel.id
    s[gid]['welcome_message'] = message
    save(WELCOME_SETTINGS_FILE, s)

    embed = discord.Embed(title="👋 Настройка приветствий", description=get_text(str(interaction.guild_id), 'welcome_configured', channel.mention), color=discord.Color.green())
    embed.add_field(name="📝 Сообщение", value=message, inline=False)
    embed.set_footer(text="bariier Bot | Приветствия")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='disable-welcome', description='Disable welcome')
async def disable_welcome(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    s = load(WELCOME_SETTINGS_FILE)
    gid = str(interaction.guild_id)
    if gid in s:
        s[gid]['welcome_enabled'] = False
        if 'photo_welcome' in s[gid]:
            s[gid]['photo_welcome']['enabled'] = False
        save(WELCOME_SETTINGS_FILE, s)
        embed = discord.Embed(title="⚠️ Отключение приветствий", description=get_text(str(interaction.guild_id), 'welcome_disabled'), 	color=discord.Color.from_rgb(255, 255, 255))
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-captcha', description='Setup captcha')
async def setup_captcha(interaction: discord.Interaction, role: discord.Role):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)

    s = load(CAPTCHA_SETTINGS_FILE)
    s[str(interaction.guild_id)] = {'enabled': True, 'verify_role_id': role.id}
    save(CAPTCHA_SETTINGS_FILE, s)

    embed = discord.Embed(title="🔐 Настройка капчи", description=get_text(str(interaction.guild_id), 'captcha_configured', role.mention), color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Безопасность")
    await interaction.response.send_message(embed=embed, ephemeral=True)
APPLICATIONS_FILE = 'applications.json'
REGEX_SETTINGS_FILE = 'regex_settings.json'

def load_applications():
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_applications(apps):
    with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=4, ensure_ascii=False)

def load_regex_settings():
    if os.path.exists(REGEX_SETTINGS_FILE):
        with open(REGEX_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_regex_settings(settings):
    with open(REGEX_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


BAD_WORDS_RU = ['хуй', 'пизда', 'бля', 'залупа', 'ебать', 'ебет', 'ебень', 'лох', 'ебаный', 'нахуй', 'охуел', 'хуесос', 'гандон', 'мудак', 'ублюдок', 'сука', 'блять', 'пиздец', 'хер', 'долбоеб', 'пидор', 'пидарас', 'шлюха', 'курва', 'блядина', 'ебучий', 'заебать', 'отъебись', 'подъеб', 'срака', 'жопа', 'пердеж']
BAD_WORDS_EN = ['fuck', 'shit', 'bitch', 'asshole', 'bastard', 'dick', 'pussy', 'cunt', 'motherfucker', 'faggot', 'whore', 'slut', 'damn', 'hell', 'cock', 'suck', 'ass', 'dumbass', 'douche', 'prick', 'crap', 'bullshit']
PERMANENT_BAN_PHRASES = ['ваш сервер', 'твой сервер', 'свой сервер', 'его сервер', 'их сервер', 'ваша гильдия', 'твоя гильдия', 'своя гильдия', 'ваш дискорд', 'твой дискорд', 'свой дискорд', 'реклама сервера', 'чужой сервер', 'другой сервер', 'забери свой сервер', 'иди на свой сервер', 'вали на свой сервер', 'создай свой сервер', 'сделай свой сервер', 'открой свой сервер', 'свой дискорд сервер', 'свой дс сервер', 'свой дс', 'ебаный сервер', 'хуевый сервер', 'гнилой сервер', 'ты сам создай сервер', 'ты сам сделай сервер', 'ваш сервер говно', 'твой сервер говно', 'это сервер говно', 'server sucks', 'your server sucks', 'his server sucks', 'bad server', 'shitty server', 'garbage server']
ALL_BAD_WORDS = BAD_WORDS_RU + BAD_WORDS_EN


@bot.tree.command(name='create-application', description='Создать заявку с вопросами до 8 вопросов')
async def create_application(interaction: discord.Interaction, название: str, роль: discord.Role, канал: discord.TextChannel):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)

    apps = load_applications()
    gid = str(interaction.guild_id)

    if gid not in apps:
        apps[gid] = {}

    app_id = len(apps[gid]) + 1

    apps[gid][str(app_id)] = {
        'name': название,
        'role_id': роль.id,
        'questions': [],
        'channel_id': interaction.channel_id,
        'send_channel_id': канал.id,
        'creator_id': interaction.user.id
    }
    save_applications(apps)

    class AddQuestionView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label='➕ Добавить вопрос', style=discord.ButtonStyle.primary)
        async def add_question(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
            class AddQuestionModal(discord.ui.Modal):
                def __init__(self, app_id, app_name, role, gid, channel_id):
                    self.app_id = app_id
                    self.app_name = app_name
                    self.role = role
                    self.gid = gid
                    self.channel_id = channel_id
                    super().__init__(title='📝 Добавить вопрос')
                    self.add_item(discord.ui.TextInput(label='Вопрос', style=discord.TextStyle.paragraph, placeholder='Напиши вопрос для заявки...'))
                async def on_submit(self, modal_interaction: discord.Interaction):
                    question = self.children[0].value
                    apps = load_applications()
                    if self.gid not in apps: apps[self.gid] = {}
                    if str(self.app_id) not in apps[self.gid]: apps[self.gid][str(self.app_id)] = {'questions': []}
                    current_questions = apps[self.gid][str(self.app_id)].get('questions', [])
                    if len(current_questions) >= 8:
                        return await modal_interaction.response.send_message('❌ Максимум 8 вопросов!', ephemeral=True)
                    apps[self.gid][str(self.app_id)]['questions'].append(question)
                    save_applications(apps)
                    total = len(apps[self.gid][str(self.app_id)]['questions'])
                    embed = discord.Embed(title="✅ Вопрос добавлен", description=f'Вопрос добавлен! (Всего: {total}/8)', color=discord.Color.green())
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
            await btn_interaction.response.send_modal(AddQuestionModal(app_id, название, роль, gid, i.channel.id))

        @discord.ui.button(label='✅ Завершить создание', style=discord.ButtonStyle.success)
        async def finish(self, btn_i: discord.Interaction, button: discord.ui.Button):
            apps_check = load_applications()
            questions = apps_check.get(gid, {}).get(str(app_id), {}).get('questions', [])
            if len(questions) < 1:
                return await btn_interaction.response.send_message('❌ Добавь хотя бы 1 вопрос!', ephemeral=True)
            if len(questions) > 8:
                return await btn_interaction.response.send_message('❌ Максимум 8 вопросов!', ephemeral=True)

            class ApplicationMenu(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)
                @discord.ui.button(label=f'📝 Подать заявку: {название[:35]}', style=discord.ButtonStyle.primary)
                async def apply(self, apply_i: discord.Interaction, button: discord.ui.Button):
                    class ApplicationModal(discord.ui.Modal):
                        def __init__(self, app_id, guild_id, send_channel_id, page=0):
                            title = f'📝 Заявка - Страница {page + 1}'
                            if len(title) > 45: title = f'Стр.{page + 1}'
                            super().__init__(title=title)
                            self.app_id = app_id
                            self.guild_id = guild_id
                            self.send_channel_id = send_channel_id
                            self.page = page
                            self.app_data = load_applications().get(guild_id, {}).get(str(app_id), {})
                            self.questions = self.app_data.get('questions', [])
                            start = page * 4
                            end = start + 4
                            page_questions = self.questions[start:end]
                            for i, q in enumerate(page_questions, 1):
                                label = q[:42] + '..' if len(q) > 45 else q
                                self.add_item(discord.ui.TextInput(label=label, style=discord.TextStyle.paragraph, required=True, max_length=1000))
                        async def on_submit(self, interaction: discord.Interaction):
                            if not hasattr(interaction.client, 'application_answers'): interaction.client.application_answers = {}
                            user_key = f"{self.guild_id}_{self.app_id}_{interaction.user.id}"
                            if user_key not in interaction.client.application_answers: interaction.client.application_answers[user_key] = {}
                            start = self.page * 4
                            for i, child in enumerate(self.children):
                                question_index = start + i
                                interaction.client.application_answers[user_key][question_index] = child.value
                            total_questions = len(self.questions)
                            next_page = self.page + 1
                            start_next = next_page * 4
                            if start_next < total_questions:
                                next_modal = ApplicationModal(self.app_id, self.guild_id, self.send_channel_id, page=next_page)
                                await interaction.response.send_modal(next_modal)
                            else:
                                await self.submit_application(interaction, interaction.client.application_answers[user_key])
                                del interaction.client.application_answers[user_key]
                        async def submit_application(self, interaction: discord.Interaction, answers):
                            app_data = load_applications().get(self.guild_id, {}).get(str(self.app_id), {})
                            role_id = app_data.get('role_id')
                            app_name = app_data.get('name', 'Заявка')
                            role = interaction.guild.get_role(role_id) if role_id else None
                            send_channel = interaction.guild.get_channel(self.send_channel_id)
                            if not send_channel: send_channel = interaction.channel
                            answers_list = []
                            for i, q in enumerate(self.questions): answers_list.append({'question': q, 'answer': answers.get(i, '')})
                            all_apps = load_applications()
                            if 'submissions' not in all_apps: all_apps['submissions'] = {}
                            submission_id = f"{self.guild_id}_{self.app_id}_{interaction.user.id}_{int(datetime.now().timestamp())}"
                            all_apps['submissions'][submission_id] = {'guild_id': self.guild_id, 'app_id': self.app_id, 'user_id': interaction.user.id, 'user_name': str(interaction.user), 'answers': answers_list, 'status': 'pending', 'created_at': datetime.now().isoformat()}
                            save_applications(all_apps)
                            embed = discord.Embed(title=f'📥 Новая заявка: {app_name}', description=f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ⏳ Ожидает рассмотрения', color=discord.Color.blue(), timestamp=datetime.now())
                            for i, ans in enumerate(answers_list, 1): embed.add_field(name=f'❓ Вопрос {i}', value=f'**{ans["question"][:50]}**\n{ans["answer"][:500]}', inline=False)
                            embed.set_footer(text=f'ID заявки: {submission_id} • bariier Bot')
                            class ReviewView(discord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=86400)
                                @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅')
                                async def approve(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_interaction.user.guild_permissions.administrator: return await btn_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                                    all_apps = load_applications()
                                    if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                        all_apps['submissions'][submission_id]['status'] = 'approved'
                                        all_apps['submissions'][submission_id]['reviewed_by'] = btn_interaction.user.id
                                        all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                        save_applications(all_apps)
                                    if role:
                                        await interaction.user.add_roles(role)
                                        await btn_interaction.response.send_message(f'✅ Заявка одобрена! {interaction.user.mention} получил роль {role.mention}', ephemeral=True)
                                    else:
                                        await btn_interaction.response.send_message('✅ Заявка одобрена!', ephemeral=True)
                                    embed.color = discord.Color.green()
                                    embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ✅ ПРИНЯТА'
                                    embed.add_field(name='👮 Рассмотрел', value=btn_interaction.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed, view=None)
                                    try: await interaction.user.send(f'✅ Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}')
                                    except: pass
                                @discord.ui.button(label='❌ Отказать', style=discord.ButtonStyle.danger, emoji='❌')
                                async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_interaction.user.guild_permissions.administrator: return await btn_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                                    all_apps = load_applications()
                                    if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                        all_apps['submissions'][submission_id]['status'] = 'rejected'
                                        all_apps['submissions'][submission_id]['reviewed_by'] = btn_interaction.user.id
                                        all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                        save_applications(all_apps)
                                    await btn_interaction.response.send_message('❌ Заявка отклонена!', ephemeral=True)
                                    embed.color = discord.Color.red()
                                    embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ❌ ОТКЛОНЕНА'
                                    embed.add_field(name='👮 Рассмотрел', value=btn_interaction.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed, view=None)
                                    try: await interaction.user.send(f'❌ Ваша заявка **{app_name}** была ОТКЛОНЕНА.')
                                    except: pass
                                @discord.ui.button(label='✏️ Принять с сообщением', style=discord.ButtonStyle.primary, emoji='✏️')
                                async def approve_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_interaction.user.guild_permissions.administrator: return await btn_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                                    class ApproveMessageModal(discord.ui.Modal):
                                        def __init__(self):
                                            super().__init__(title='✅ Принять заявку')
                                            self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph, placeholder='Сообщение пользователю...', required=True))
                                        async def on_submit(self, modal_i: discord.Interaction):
                                            message_text = self.children[0].value
                                            all_apps = load_applications()
                                            if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                                all_apps['submissions'][submission_id]['status'] = 'approved_with_message'
                                                all_apps['submissions'][submission_id]['reviewed_by'] = modal_interaction.user.id
                                                all_apps['submissions'][submission_id]['review_message'] = message_text
                                                all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                                save_applications(all_apps)
                                            if role: await interaction.user.add_roles(role)
                                            embed.color = discord.Color.green()
                                            embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ✅ ПРИНЯТА (с сообщением)'
                                            embed.add_field(name='👮 Рассмотрел', value=modal_interaction.user.mention, inline=False)
                                            embed.add_field(name='📝 Сообщение', value=message_text[:500], inline=False)
                                            await btn_i.message.edit(embed=embed, view=None)
                                            await modal_interaction.response.send_message('✅ Заявка одобрена с сообщением!', ephemeral=True)
                                            try: await interaction.user.send(f'✅ Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}\n\n**Сообщение:**\n{message_text}')
                                            except: pass
                                    await btn_interaction.response.send_modal(ApproveMessageModal())
                                @discord.ui.button(label='📝 Отказать с сообщением', style=discord.ButtonStyle.secondary, emoji='📝')
                                async def reject_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_interaction.user.guild_permissions.administrator: return await btn_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                                    class RejectMessageModal(discord.ui.Modal):
                                        def __init__(self):
                                            super().__init__(title='❌ Отказать заявке')
                                            self.add_item(discord.ui.TextInput(label='Причина', style=discord.TextStyle.paragraph, placeholder='Причина отказа...', required=True))
                                        async def on_submit(self, modal_i: discord.Interaction):
                                            message_text = self.children[0].value
                                            all_apps = load_applications()
                                            if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                                all_apps['submissions'][submission_id]['status'] = 'rejected_with_message'
                                                all_apps['submissions'][submission_id]['reviewed_by'] = modal_interaction.user.id
                                                all_apps['submissions'][submission_id]['review_message'] = message_text
                                                all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                                save_applications(all_apps)
                                            embed.color = discord.Color.red()
                                            embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ❌ ОТКАЗАНО (с сообщением)'
                                            embed.add_field(name='👮 Рассмотрел', value=modal_interaction.user.mention, inline=False)
                                            embed.add_field(name='📝 Причина', value=message_text[:500], inline=False)
                                            await btn_i.message.edit(embed=embed, view=None)
                                            await modal_interaction.response.send_message('❌ Заявка отклонена с сообщением!', ephemeral=True)
                                            try: await interaction.user.send(f'❌ Ваша заявка **{app_name}** была ОТКЛОНЕНА.\n\n**Причина:**\n{message_text}')
                                            except: pass
                                    await btn_interaction.response.send_modal(RejectMessageModal())
                            await send_channel.send(embed=embed, view=ReviewView())
                            await interaction.response.send_message('✅ Заявка отправлена! Ожидай решения.', ephemeral=True)
                    await apply_interaction.response.send_modal(ApplicationModal(app_id, gid, канал.id, page=0))
            embed = discord.Embed(title=f'📝 Заявка: {название}', description=f'Нажми на кнопку ниже, чтобы подать заявку.\nПосле проверки ты получишь роль {роль.mention}\n\nВсего вопросов: {len(questions)}', color=discord.Color.blue())
            embed.set_footer(text="bariier Bot | Заявки")
            await i.channel.send(embed=embed, view=ApplicationMenu())
            await btn_interaction.response.send_message('✅ Заявка создана! Кнопка отправлена в канал.', ephemeral=True)
            self.stop()

    embed = discord.Embed(title='📝 Создание заявки', description=f'**Название:** {название}\n**Роль:** {роль.mention}\n**Канал отправки:** {канал.mention}\n\nНажми на кнопки ниже, чтобы добавить вопросы.\n**Максимум 8 вопросов** (по 4 на страницу)', color=discord.Color.green())
    embed.set_footer(text="bariier Bot | Система заявок")
    await interaction.response.send_message(embed=embed, view=AddQuestionView(), ephemeral=True)


@bot.tree.command(name='list-applications', description='Показать список созданных заявок')
async def list_applications(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)
    apps = load_applications().get(str(interaction.guild_id), {})
    if not apps:
        return await interaction.response.send_message('❌ Нет созданных заявок!', ephemeral=True)
    embed = discord.Embed(title='📋 Список заявок', color=discord.Color.blue())
    for app_id, app_data in apps.items():
        role = interaction.guild.get_role(app_data.get('role_id'))
        embed.add_field(name=f'ID: {app_id} - {app_data.get("name")}', value=f'Роль: {role.mention if role else "Не указана"}\nВопросов: {len(app_data.get("questions", []))}', inline=False)
    embed.set_footer(text="bariier Bot | Заявки")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='delete-application', description='Удалить заявку по ID')
async def delete_application(interaction: discord.Interaction, id_заявки: str):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)
    apps = load_applications()
    gid = str(interaction.guild_id)
    if gid not in apps or id_заявки not in apps[gid]:
        return await interaction.response.send_message('❌ Заявка не найдена!', ephemeral=True)
    del apps[gid][id_заявки]
    save_applications(apps)
    embed = discord.Embed(title="✅ Заявка удалена", description=f'Заявка #{id_заявки} удалена!', color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='massunban', description='Разбан всех пользователей на сервере')
async def massunban(interaction: discord.Interaction, reason: str = "Массовый разбан"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    banned_users = [entry async for entry in interaction.guild.bans()]
    if len(banned_users) == 0:
        return await interaction.response.send_message('❌ На сервере нет забаненных пользователей!', ephemeral=True)
    await interaction.response.send_message(f'🔄 Начинаю разбан **{len(banned_users)}** пользователей...', ephemeral=True)
    success = []
    failed = []
    for entry in banned_users:
        user = entry.user
        try:
            await interaction.guild.unban(user, reason=reason)
            success.append(f'{user.name} ({user.id})')
        except Exception as e:
            failed.append(f'{user.name} ({user.id}) - {str(e)[:30]}')
    embed = discord.Embed(title='🔓 Массовый разбан', color=discord.Color.green() if not failed else discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name='✅ Успешно разбанены', value=f'**{len(success)}** из **{len(banned_users)}** пользователей', inline=False)
    if success: embed.add_field(name='📋 Список разбаненных', value='\n'.join(success[:15]) + ('\n...' if len(success) > 15 else ''), inline=False)
    if failed: embed.add_field(name='❌ Ошибки', value='\n'.join(failed[:10]), inline=False)
    embed.set_footer(text=f'Запросил: {interaction.user.name} • bariier Bot')
    await i.edit_original_response(content=None, embed=embed)


@bot.tree.command(name='disable-captcha', description='Disable captcha')
async def disable_captcha(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    gid = str(interaction.guild_id)
    if gid in s:
        s[gid]['enabled'] = False
        save(CAPTCHA_SETTINGS_FILE, s)
        embed = discord.Embed(title="🔐 Отключение капчи", description=get_text(str(interaction.guild_id), 'captcha_disabled'), 	color=discord.Color.from_rgb(255, 255, 255))
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-application', description='Setup roles for applications')
async def setup_application(interaction: discord.Interaction, moderator: discord.Role = None, administrator: discord.Role = None):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE)
    gid = str(interaction.guild_id)
    if gid not in s: s[gid] = {}
    if moderator: s[gid]['moderator_role'] = moderator.id
    if administrator: s[gid]['admin_role'] = administrator.id
    save(SETTINGS_FILE, s)
    embed = discord.Embed(title="⚙️ Настройка заявок", description=get_text(str(interaction.guild_id), 'settings_saved'), color=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='create-apps', description='Create application menu')
async def create_apps(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE).get(str(interaction.guild_id), {})
    if not s:
        return await interaction.response.send_message(get_text(str(interaction.guild_id), 'no_roles'), ephemeral=True)
    class AppSelect(discord.ui.Select):
        def __init__(self):
            opts = []
            if s.get('moderator_role'): opts.append(discord.SelectOption(label='Moderator', emoji='🛡️', value='moderator'))
            if s.get('admin_role'): opts.append(discord.SelectOption(label='Administrator', emoji='👑', value='admin'))
            super().__init__(placeholder='📋 Choose a position...', options=opts, min_values=1, max_values=1)
        async def callback(self, select_interaction: discord.Interaction):
            class AppModal(discord.ui.Modal):
                def __init__(self, role_type, s):
                    self.role_type = role_type
                    self.s = s
                    super().__init__(title=f'Application for {role_type.title()}')
                    self.add_item(discord.ui.TextInput(label='Why do you want this position?', style=discord.TextStyle.paragraph))
                    self.add_item(discord.ui.TextInput(label='What experience do you have?', style=discord.TextStyle.paragraph))
                async def on_submit(self, modal_interaction: discord.Interaction):
                    rid = self.s.get(f'{self.role_type}_role')
                    if rid and (r := modal_interaction.guild.get_role(rid)):
                        await modal_interaction.response.send_message(f'✅ Application sent to {r.mention}!', ephemeral=True)
                        e = discord.Embed(title=f'📥 New application for {self.role_type.title()}', description=f'From: {modal_interaction.user.mention}', color=0x00ff00)
                        e.add_field(name='Why?', value=self.children[0].value[:500])
                        e.add_field(name='Experience', value=self.children[1].value[:500])
                        e.set_footer(text="bariier Bot | Заявки")
                        await modal_i.channel.send(r.mention, embed=e)
                    else:
                        await modal_interaction.response.send_message(get_text(str(modal_interaction.guild_id), 'error', 'Role not found'), ephemeral=True)
            await select_interaction.response.send_modal(AppModal(self.values[0], s))
    view = discord.ui.View()
    view.add_item(AppSelect())
    e = discord.Embed(title='📝 Applications', description='Select a position from the menu below to apply.', color=0x2b2d31)
    await interaction.response.send_message(embed=e, view=view)


SAT_TICKET_TYPES = ['support', 'bug', 'idea', 'report_staff', 'partnership']
SAT_BUTTON_CONFIGS = {
    'support':      ('🎫 Поддержка', discord.ButtonStyle.primary),
    'bug':          ('🐛 Сообщить об ошибке', discord.ButtonStyle.danger),
    'idea':         ('💡 Предложить идею', discord.ButtonStyle.success),
    'report_staff': ('⚠️ Пожаловаться на персонал', discord.ButtonStyle.danger),
    'partnership':  ('🤝 Предложить сотрудничество', discord.ButtonStyle.success),
}
SAT_COLORS = {
    'support': discord.Color.blue(), 'bug': discord.Color.red(),
    'idea': discord.Color.green(), 'report_staff': discord.Color.red(),
    'partnership': discord.Color.green()
}

class SatTicketPersistentView(discord.ui.View):
    def __init__(self, ticket_type: str, guild_id: int):
        super().__init__(timeout=None)
        self.ticket_type = ticket_type
        self.guild_id = guild_id
        label, style = SAT_BUTTON_CONFIGS.get(ticket_type, ('🎫 Тикет', discord.ButtonStyle.primary))
        btn = discord.ui.Button(label=label, style=style, custom_id=f'ticket_{ticket_type}_{guild_id}')
        btn.callback = self.create_ticket
        self.add_item(btn)

    async def create_ticket(self, interaction: discord.Interaction):
        CATEGORY_ID = 1512867735330361374
        SUPPORT_ROLE_ID = 1511393460622463039
        category = interaction.guild.get_channel(CATEGORY_ID)
        role = interaction.guild.get_role(SUPPORT_ROLE_ID)
        name = f'{self.ticket_type}-{interaction.user.name.lower()}-{random.randint(100, 999)}'
        ow = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        }
        if role:
            ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
        try:
            ch = await interaction.guild.create_text_channel(name, category=category, overwrites=ow)
            embed = discord.Embed(
                title='🆕 НОВЫЙ ТИКЕТ',
                description=f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ⏳ Ожидает ответа',
                color=SAT_COLORS.get(self.ticket_type, discord.Color.blue()),
                timestamp=datetime.now()
            )
            embed.set_footer(text=f'bariier Bot • {name}')
            await ch.send(embed=embed)
            await interaction.response.send_message(f'✅ Тикет создан: {ch.mention}', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')

    bot.add_view(TicketView())

    # Авто-регистрация persistent views для sat-тикетов всех серверов
    for guild in bot.guilds:
        for tt in SAT_TICKET_TYPES:
            try:
                bot.add_view(SatTicketPersistentView(tt, guild.id))
            except Exception:
                pass

    # Авто-регистрация панели приватных голосовых каналов
    try:
        bot.add_view(VoicePanelPersistentView())
    except Exception:
        pass


@bot.tree.command(name='invite', description='Invite bot')
async def invite(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return

    e = discord.Embed(
        title=get_text(str(interaction.guild_id) if interaction.guild else '0', 'invite_title'),
        description=get_text(str(interaction.guild_id) if interaction.guild else '0', 'invite_desc'),
        color=discord.Color.blue()
    )

    # Проверяем, есть ли иконка у сервера (и выполняется ли команда НЕ в ЛС)
    if interaction.guild and interaction.guild.icon:
        e.set_thumbnail(url=interaction.guild.icon.url)

    e.set_footer(text=get_text(str(interaction.guild_id) if interaction.guild else '0', 'invite_footer'))

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label=get_text(str(interaction.guild_id) if interaction.guild else '0', 'invite_button'),
        style=discord.ButtonStyle.link,
        url=f'https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands'
    ))
    view.add_item(discord.ui.Button(
        label=get_text(str(interaction.guild_id) if interaction.guild else '0', 'server_button'),
        style=discord.ButtonStyle.link,
        url='https://discord.gg/invite'
    ))

    await interaction.response.send_message(embed=e, view=view)





VIP_USER_ID = 1436760469980450816
VIP_NICKNAME = "Ceo.bariIER Forever.morgan"
VIP_ROLE_NAME = "CEO.bariIER.BOT👑"
VIP_ROLE_COLOR = 0xffffff

WHITELIST_USERS = [1436760469980450816]

@bot.tree.command(name='regex', description='Включить/выключить авто-мут/бан за нарушения')
@app_commands.choices(attribute=[
    app_commands.Choice(name='🔴 Включить', value='on'),
    app_commands.Choice(name='⚫ Выключить', value='off'),
    app_commands.Choice(name='📊 Статус', value='status')
])
async def regex_cmd(interaction: discord.Interaction, attribute: app_commands.Choice[str]):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message('❌ Нет прав!', ephemeral=True)
    settings = load_regex_settings()
    gid = str(interaction.guild_id)
    if attribute.value == 'on':
        settings[gid] = {'enabled': True, 'action': 'mute', 'duration': 60}
        save_regex_settings(settings)
        embed = discord.Embed(title='🛡️ Автомодерация', description='✅ Система **ВКЛЮЧЕНА**\n\n**📝 За маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n**🔨 За рекламу/оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)', color=discord.Color.green())
        embed.set_footer(text="bariier Bot | Защита")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif attribute.value == 'off':
        if gid in settings: settings[gid]['enabled'] = False
        save_regex_settings(settings)
        embed = discord.Embed(title='🛡️ Автомодерация', description='⚫ Система **ВЫКЛЮЧЕНА**', 	color=discord.Color.from_rgb(255, 255, 255))
        embed.set_footer(text="bariier Bot | Защита")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif attribute.value == 'status':
        is_enabled = settings.get(gid, {}).get('enabled', False)
        status_text = '🔴 **ВКЛЮЧЕНА**' if is_enabled else '⚫ **ВЫКЛЮЧЕНА**'
        embed = discord.Embed(title='🛡️ Статус автомодерации', description=f'{status_text}\n\n**📝 Маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n**🔨 Оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)', color=discord.Color.green() if is_enabled else discord.Color.red())
        embed.set_footer(text="bariier Bot | Защита")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_message(message):
    if message.author.bot:
        return await bot.process_commands(message)
    if not message.guild:
        return await bot.process_commands(message)
    if message.author.id in WHITELIST_USERS:
        return await bot.process_commands(message)
    settings = load_regex_settings()
    gid = str(message.guild.id)
    if settings.get(gid, {}).get('enabled', False):
        content_lower = message.content.lower()
        for phrase in PERMANENT_BAN_PHRASES:
            if phrase in content_lower:
                try:
                    await message.delete()
                    audit_reason = f"Автомодерация bariier Bot | Нарушение: '{phrase}' | Автор: {message.author}"
                    await message.author.ban(reason=audit_reason)
                    embed = discord.Embed(title='🔨 ПЕРМАНЕНТНЫЙ БАН', description=f'{message.author.mention} был **НАВСЕГДА ЗАБАНЕН** за сообщение:\n```{message.content[:100]}```\n**Причина:** Оскорбление/реклама сервера', 	color=discord.Color.from_rgb(255, 255, 255))
                    embed.set_footer(text="bariier Bot • Автомодерация")
                    await message.channel.send(embed=embed)
                    try: await message.author.send(f'🔨 Вы получили **ПЕРМАНЕНТНЫЙ БАН** на сервере **{message.guild.name}** за сообщение: "{message.content[:100]}"')
                    except: pass
                except Exception as e: print(f'Ошибка при бане: {e}')
                return await bot.process_commands(message)
        for bad_word in ALL_BAD_WORDS:
            if bad_word in content_lower:
                try:
                    await message.delete()
                    until = discord.utils.utcnow() + timedelta(hours=1)
                    audit_reason = f"Автомодерация bariier Bot | Мат: '{bad_word}' | Автор: {message.author}"
                    await message.author.timeout(until, reason=audit_reason)
                    embed = discord.Embed(title='🛡️ Авто-мут', description=f'{message.author.mention} получил **МУТ на 1 час** за использование мата: `{bad_word}`', color=discord.Color.orange())
                    embed.set_footer(text="bariier Bot • Автомодерация")
                    await message.channel.send(embed=embed, delete_after=10)
                    try: await message.author.send(f'⏰ Вы получили мут на 1 час на сервере **{message.guild.name}** за использование мата: `{bad_word}`')
                    except: pass
                except Exception as e: print(f'Ошибка при выдаче мута: {e}')
                break
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    if member.id in WHITELIST_USERS:
        cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
        if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
            role = member.guild.get_role(rid)
            if role:
                await member.add_roles(role)
        try: await member.edit(nick=VIP_NICKNAME)
        except: pass
        ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
        if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
            await ch.send(f'👑 **{member.mention} (Владелец)** присоединился к серверу!')
        return
    cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
    if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
        code = gen_captcha()
        active_captchas[str(member.id)] = {'code': code, 'attempts': 0, 'guild_id': member.guild.id, 'verify_role_id': rid}
        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
            @discord.ui.button(label='✅ I am human', style=discord.ButtonStyle.green)
            async def btn(self, bi: discord.Interaction, button: discord.ui.Button):
                if binteraction.user.id != member.id: return await binteraction.response.send_message("❌ Not for you!", ephemeral=True)
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
                        if not d: return await minteraction.response.send_message("❌ Expired!", ephemeral=True)
                        if self.children[0].value == d['code']:
                            g = bot.get_guild(self.gid)
                            if g and (r := g.get_role(self.rid)) and (mo := g.get_member(self.uid)):
                                await mo.add_roles(r)
                                await minteraction.response.send_message("✅ Verified! Welcome!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                        else:
                            d['attempts'] += 1
                            if d['attempts'] >= 3:
                                if (g := bot.get_guild(self.gid)) and (mo := g.get_member(self.uid)): await mo.kick(reason="Failed captcha")
                                await minteraction.response.send_message("❌ Kicked for 3 failed attempts!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                            else: await minteraction.response.send_message(f"❌ Invalid! {3 - d['attempts']} attempts left", ephemeral=True)
                await binteraction.response.send_modal(Modal(code, member.id, member.guild.id, rid))
        e = discord.Embed(title='🔐 Verification Required', description=f'Welcome to {member.guild.name}!', color=0x3498db)
        e.add_field(name='Code', value=f'||{code}||')
        e.set_footer(text='5 minutes | 3 attempts • bariier Bot')
        try: await member.send(embed=e, view=View())
        except: pass
    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('welcome_message', 'Welcome {member}!')
        msg = msg.replace('{member}', member.mention)
        await ch.send(msg)
    await update_stats_channels()


@bot.event
async def on_member_remove(member):
    ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
    if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
        msg = ws.get('goodbye_message', '{member} left')
        msg = msg.replace('{member}', member.name)
        await ch.send(msg)
    e = discord.Embed(title='🚪 Member left', description=f'{member.mention} left', color=0xe74c3c, timestamp=datetime.now())
    e.set_footer(text="bariier Bot | Логи")
    await send_log(member.guild.id, e)
    await update_stats_channels()


@bot.event
async def on_message_delete(msg):
    if msg.author.bot: return
    e = discord.Embed(title='🗑️ Message deleted', description=f'{msg.author.mention} in {msg.channel.mention}', color=0xe74c3c, timestamp=datetime.now())
    e.add_field(name='Content', value=msg.content[:500] if msg.content else '*No text*')
    e.set_footer(text="bariier Bot | Логи")
    await send_log(msg.guild.id, e)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    e = discord.Embed(title='✏️ Message edited', description=f'{before.author.mention}', color=0xe67e22, timestamp=datetime.now())
    e.add_field(name='Before', value=before.content[:500] if before.content else '*No text*')
    e.add_field(name='After', value=after.content[:500] if after.content else '*No text*')
    e.set_footer(text="bariier Bot | Логи")
    await send_log(before.guild.id, e)


@bot.tree.command(name='servers', description='Показать список серверов и их владельцев')
async def servers_cmd(interaction: discord.Interaction):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
    if await check_blacklist(interaction): return
    if interaction.user.id != VIP_USER_ID:
        return await interaction.response.send_message('❌ Эта команда только для разработчика!', ephemeral=True)
    embed = discord.Embed(title='📊 Список серверов с ботом', color=discord.Color.blue(), timestamp=datetime.now())
    for guild in bot.guilds:
        owner = guild.owner
        is_my = "🔴 **ВАШ**" if owner.id == VIP_USER_ID else ""
        embed.add_field(name=f"{guild.name}", value=f"🆔 ID: `{guild.id}`\n👑 Владелец: {owner.mention if owner else 'Неизвестен'}\n👥 Участников: {guild.member_count}\n{is_my}", inline=False)
    embed.set_footer(text=f'Всего серверов: {len(bot.guilds)} • bariier Bot')
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command(name='sat')
async def setup_all_ticket(ctx):
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        return

    CATEGORY_ID = 1512867735330361374
    SUPPORT_ROLE_ID = 1511393460622463039

    category = ctx.guild.get_channel(CATEGORY_ID)
    support_role = ctx.guild.get_role(SUPPORT_ROLE_ID)

    if not category:
        await ctx.send(f'❌ Категория с ID `{CATEGORY_ID}` не найдена!')
        return
    if not support_role:
        await ctx.send(f'❌ Роль с ID `{SUPPORT_ROLE_ID}` не найдена!')
        return

    logs_channel_id = load(LOGS_SETTINGS_FILE).get(str(ctx.guild.id))
    logs_channel = ctx.guild.get_channel(logs_channel_id) if logs_channel_id else None

    deleted_count = 0
    async for msg in ctx.channel.history(limit=50):
        if deleted_count >= 5:
            break
        if msg.author == bot.user and msg.components:
            try:
                await msg.delete()
                deleted_count += 1
                await asyncio.sleep(0.5)
            except:
                pass

    if deleted_count > 0:
        await ctx.send(f"🗑️ Удалено {deleted_count} старых сообщений с тикетами...", delete_after=3)

    ticket_types = [
        ('support', '🎫 Поддержка'),
        ('bug', '🐛 Баг-репорт'),
        ('idea', '💡 Идея'),
        ('report_staff', '⚠️ Жалоба на персонал'),
        ('partnership', '🤝 Партнёрство')
    ]

    button_labels = {
        'support': {'label': '🎫 Поддержка', 'style': discord.ButtonStyle.primary, 'emoji': '🎫'},
        'bug': {'label': '🐛 Сообщить об ошибке', 'style': discord.ButtonStyle.danger, 'emoji': '🐛'},
        'idea': {'label': '💡 Предложить идею', 'style': discord.ButtonStyle.success, 'emoji': '💡'},
        'report_staff': {'label': '⚠️ Пожаловаться на персонал', 'style': discord.ButtonStyle.danger, 'emoji': '⚠️'},
        'partnership': {'label': '🤝 Предложить сотрудничество', 'style': discord.ButtonStyle.success, 'emoji': '🤝'}
    }

    titles = {
        'support': '🎫 Система тикетов',
        'bug': '🐛 Баг-репорт система',
        'idea': '💡 Идеи для бота',
        'report_staff': '⚠️ Жалобы на персонал',
        'partnership': '🤝 Сотрудничество'
    }

    descriptions = {
        'support': 'Нажми на кнопку ниже, чтобы создать тикет.\nСотрудники ответят в ближайшее время.',
        'bug': 'Нашли баг? Нажми на кнопку ниже и сообщи разработчикам.\n\n**Спасибо за помощь в развитии бота!**',
        'idea': 'Есть идея по улучшению бота? Нажми на кнопку ниже и поделись!\n\n**Лучшие идеи будут реализованы!**',
        'report_staff': 'Нажми на кнопку ниже, чтобы пожаловаться на сотрудника.\n\n**Ложные жалобы караются!**',
        'partnership': 'Нажми на кнопку ниже, чтобы предложить сотрудничество, рекламу или совместные ивенты.'
    }

    colors = {
        'support': discord.Color.blue(),
        'bug': discord.Color.red(),
        'idea': discord.Color.green(),
        'report_staff': discord.Color.red(),
        'partnership': discord.Color.green()
    }

    settings = load(TICKET_SETTINGS_FILE)
    gid = str(ctx.guild.id)
    if gid not in settings:
        settings[gid] = {}

    sent_messages = []

    for ticket_type, type_name in ticket_types:
        settings[gid][ticket_type] = {
            'category': CATEGORY_ID,
            'role': SUPPORT_ROLE_ID,
            'type': ticket_type
        }

        class TicketView(discord.ui.View):
            def __init__(self, tt):
                super().__init__(timeout=None)
                self.ticket_type = tt
                btn_info = button_labels[tt]
                button = discord.ui.Button(
                    label=btn_info['label'],
                    style=btn_info['style'],
                    emoji=btn_info['emoji'],
                    custom_id=f'ticket_{tt}_{ctx.guild.id}'
                )
                button.callback = self.create_ticket
                self.add_item(button)

            async def create_ticket(self, button_interaction: discord.Interaction):
                await self.handle_ticket_creation(button_interaction, self.ticket_type)

            async def handle_ticket_creation(self, button_interaction: discord.Interaction, ticket_type_value: str):
                s = load(TICKET_SETTINGS_FILE).get(str(button_interaction.guild.id), {}).get(ticket_type_value, {})
                cat = button_interaction.guild.get_channel(s.get('category'))
                role = button_interaction.guild.get_role(s.get('role'))

                prefix = ticket_type_value
                name = f'{prefix}-{button_interaction.user.name.lower()}-{random.randint(100, 999)}'

                ow = {
                    button_interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    button_interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                                         read_messages=True)
                }
                if role:
                    ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

                ch = await button_interaction.guild.create_text_channel(name, category=cat, overwrites=ow)

                embed = discord.Embed(
                    title='🆕 НОВЫЙ ТИКЕТ',
                    description=f'**От:** {button_interaction.user.mention}\n**ID:** {button_interaction.user.id}\n**Статус:** ⏳ Ожидает ответа',
                    color=colors.get(ticket_type_value, discord.Color.blue()),
                    timestamp=datetime.now()
                )
                embed.set_footer(text=f'ID: {name} • bariier Bot')

                class TicketButtons(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒',
                                       custom_id=f'ticket_close_{name}')
                    async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not button_interaction.user.guild_permissions.administrator and button_interaction.user.id != button_interaction.user.id:
                            return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                        await button_interaction.response.send_message('🔒 Закрытие тикета...', ephemeral=True)
                        try:
                            await button_interaction.user.send(f'✅ Ваш тикет **{name}** был закрыт.')
                        except:
                            pass
                        await asyncio.sleep(2)
                        await ch.delete()

                    @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅',
                                       custom_id=f'ticket_accept_{name}')
                    async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not button_interaction.user.guild_permissions.administrator:
                            return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                        embed.color = discord.Color.green()
                        embed.description = f'**От:** {button_interaction.user.mention}\n**Статус:** ✅ ПРИНЯТ В РАБОТУ'
                        embed.add_field(name='👨‍💻 Принял', value=button_interaction.user.mention, inline=False)
                        await btn_i.message.edit(embed=embed, view=self)
                        await button_interaction.response.send_message('✅ Тикет принят в работу!', ephemeral=True)
                        try:
                            await button_interaction.user.send(
                                f'✅ Ваш тикет **{name}** принят в работу сотрудником {button_interaction.user.mention}')
                        except:
                            pass

                    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.secondary, emoji='❌',
                                       custom_id=f'ticket_reject_{name}')
                    async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not button_interaction.user.guild_permissions.administrator:
                            return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)
                        embed.color = discord.Color.red()
                        embed.description = f'**От:** {button_interaction.user.mention}\n**Статус:** ❌ ОТКЛОНЁН'
                        embed.add_field(name='👨‍💻 Отклонил', value=button_interaction.user.mention, inline=False)
                        await btn_i.message.edit(embed=embed, view=self)
                        await button_interaction.response.send_message('❌ Тикет отклонён!', ephemeral=True)
                        try:
                            await button_interaction.user.send(f'❌ Ваш тикет **{name}** был отклонён.')
                        except:
                            pass

                    @discord.ui.button(label='✏️ Ответить', style=discord.ButtonStyle.primary, emoji='✏️',
                                       custom_id=f'ticket_reply_{name}')
                    async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not button_interaction.user.guild_permissions.administrator:
                            return await button_interaction.response.send_message('❌ Нет прав!', ephemeral=True)

                        class ReplyModal(discord.ui.Modal):
                            def __init__(self):
                                super().__init__(title='📝 Ответ пользователю')
                                self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                                   placeholder='Ваш ответ...', required=True))

                            async def on_submit(self, modal_i: discord.Interaction):
                                msg = self.children[0].value
                                embed.color = discord.Color.green()
                                embed.description = f'**От:** {button_interaction.user.mention}\n**Статус:** ✅ ОТВЕЧЕНО'
                                embed.add_field(name='📝 Ответ сотрудника', value=msg, inline=False)
                                embed.add_field(name='👨‍💻 Ответил', value=modal_interaction.user.mention, inline=False)
                                await btn_i.message.edit(embed=embed)
                                await modal_interaction.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                                try:
                                    await button_interaction.user.send(
                                        f'📩 Ответ на ваш тикет **{name}** от {modal_interaction.user.mention}:\n\n{msg}')
                                except:
                                    pass

                        await button_interaction.response.send_modal(ReplyModal())

                await ch.send(f'{role.mention if role else ""}', embed=embed, view=TicketButtons())
                await button_interaction.response.send_message(f'✅ Тикет создан: {ch.mention}', ephemeral=True)

        embed_msg = discord.Embed(
            title=titles[ticket_type],
            description=descriptions[ticket_type],
            color=colors[ticket_type]
        )
        embed_msg.set_footer(text="bariier Bot • Тикет-система")
        msg = await ctx.send(embed=embed_msg, view=TicketView(ticket_type))
        sent_messages.append(msg)

        await asyncio.sleep(1)

    save(TICKET_SETTINGS_FILE, settings)

    log_embed = discord.Embed(
        title="🔧 Настройка тикет-систем",
        description=f"✅ **Все 5 систем тикетов успешно настроены!**\n\n"
                    f"📁 **Категория:** {category.mention}\n"
                    f"👮 **Роль поддержки:** {support_role.mention}\n\n"
                    f"**📋 Настроенные тикеты:**\n"
                    f"• 🎫 Поддержка\n"
                    f"• 🐛 Баг-репорт\n"
                    f"• 💡 Идея\n"
                    f"• ⚠️ Жалоба на персонал\n"
                    f"• 🤝 Партнёрство",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    log_embed.set_footer(text=f"Настроил: {ctx.author.name}")
    log_embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    if logs_channel:
        await logs_channel.send(embed=log_embed)
    else:
        await ctx.send(embed=log_embed)

    sent_message = await channel.send(message_content)
    await sent_message.add_reaction("✅")
    print(f"[{datetime.datetime.now()}] Отправлено сообщение в {channel.name} | Участников: {member_count}")


@bot.command(name='cat')
async def close_all_tickets(ctx):
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        return

    CLOSED_CATEGORY_ID = 1512112447673339904

    closed_category = ctx.guild.get_channel(CLOSED_CATEGORY_ID)
    if not closed_category:
        await ctx.send(f"❌ Категория с ID `{CLOSED_CATEGORY_ID}` не найдена!")
        return

    logs_channel_id = load(LOGS_SETTINGS_FILE).get(str(ctx.guild.id))
    logs_channel = ctx.guild.get_channel(logs_channel_id) if logs_channel_id else None

    ticket_prefixes = ['support-', 'bug-', 'idea-', 'report_staff-', 'partnership-', 'ticket-']

    ticket_channels = []
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            for prefix in ticket_prefixes:
                if channel.name.startswith(prefix) and not channel.name.startswith('[closed]'):
                    ticket_channels.append(channel)
                    break

    if not ticket_channels:
        await ctx.send("❌ На сервере нет активных тикетов для закрытия!")
        return

    confirm_msg = await ctx.send(f"⚠️ **Внимание!** Вы собираетесь закрыть **{len(ticket_channels)}** тикетов.\n"
                                 f"Тикеты будут перемещены в категорию {closed_category.mention}\n"
                                 f"**🔒 Доступ к просмотру будет только у администраторов!**\n"
                                 f"(Роль поддержки и все остальные потеряют доступ)\n\n"
                                 f"Напишите `yes` в течение 15 секунд для подтверждения.")

    def check(m):
        return m.author == ctx.author and m.content.lower() == 'yes' and m.channel == ctx.channel

    try:
        await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="⏰ Время вышло. Операция отменена.")
        return

    closed_count = 0
    failed_count = 0
    closed_list = []

    await confirm_msg.edit(content=f"🔒 Начинаю закрытие **{len(ticket_channels)}** тикетов...")

    for channel in ticket_channels:
        try:

            await channel.set_permissions(ctx.guild.default_role, view_channel=False)

            for role in ctx.guild.roles:
                if not role.permissions.administrator:
                    try:
                        await channel.set_permissions(role, overwrite=None)
                    except:
                        pass

            for member in channel.members:
                if not member.guild_permissions.administrator:
                    try:
                        await channel.set_permissions(member, overwrite=None)
                    except:
                        pass

            new_name = f"[closed]{channel.name}"
            if len(new_name) > 100:
                new_name = new_name[:97] + "..."
            await channel.edit(name=new_name, category=closed_category)

            await closed_category.set_permissions(ctx.guild.default_role, view_channel=False)

            closed_count += 1
            closed_list.append(f"• {channel.name}")
            await asyncio.sleep(0.5)
        except Exception as e:
            failed_count += 1
            print(f"Ошибка при закрытии {channel.name}: {e}")

    result_embed = discord.Embed(
        title="🔒 Закрытие тикетов",
        description=f"✅ **Операция завершена!**\n\n"
                    f"**📊 Статистика:**\n"
                    f"• Закрыто: **{closed_count}** тикетов\n"
                    f"• Ошибок: **{failed_count}**\n\n"
                    f"**📁 Перемещены в:** {closed_category.mention}\n"
                    f"**👁️ Доступ:** Только у администраторов\n"
                    f"**🔒 Роль поддержки больше не видит тикеты**",
        color=discord.Color.green() if failed_count == 0 else discord.Color.orange(),
        timestamp=datetime.now()
    )

    if closed_list:
        closed_text = '\n'.join(closed_list[:15])
        if len(closed_list) > 15:
            closed_text += f'\n... и ещё {len(closed_list) - 15}'
        result_embed.add_field(name="📋 Закрытые тикеты", value=closed_text, inline=False)

    result_embed.set_footer(text=f"Закрыл: {ctx.author.name}")

    await ctx.send(embed=result_embed)

    if logs_channel:
        log_embed = discord.Embed(
            title="🔒 Массовое закрытие тикетов",
            description=f"**Закрыто тикетов:** {closed_count}\n"
                        f"**Ошибок:** {failed_count}\n"
                        f"**Категория:** {closed_category.mention}\n"
                        f"**Доступ:** Только у администраторов\n"
                        f"**Роль поддержки:** Доступ ЗАБРАН\n"
                        f"**Инициатор:** {ctx.author.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await logs_channel.send(embed=log_embed)

    await ctx.send(f"✅ **Готово!** Все тикеты закрыты.\n"
                   f"🔒 Теперь их могут видеть только **администраторы**.\n"
                   f"🚫 Роль поддержки и все остальные потеряли доступ.")


@bot.command(name='leave')
async def leave_guild(ctx, guild_id: str = None):
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        return

    if guild_id is None:
        if ctx.guild is not None:
            guild = ctx.guild
            await ctx.send(f"👋 Покидаю сервер **{guild.name}**...")
            await guild.leave()
        else:
            await ctx.send("❌ Укажите ID сервера: `!leave 123456789012345678`")
        return

    try:
        guild_id_int = int(guild_id)
        guild = bot.get_guild(guild_id_int)

        if guild is None:
            await ctx.send(
                f"❌ Не удалось найти сервер с ID `{guild_id}`. Возможно, бот там уже не состоит, или ID введен неверно.")
            return

        await ctx.send(f"👋 Покидаю сервер **{guild.name}** (ID: `{guild_id}`)...")
        await guild.leave()

    except ValueError:
        await ctx.send("❌ ID сервера должен быть числом.")
    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка: {e}")


# =====================================================
# 🔴 КРАСНО-ЧЁРНАЯ DEV ПАНЕЛЬ 🔴
# =====================================================

@bot.command(name='dev')
async def dev_panel(ctx):
    if ctx.author.id != 1436760469980450816:
        return
    if ctx.guild is not None:
        await ctx.send("❌ Эта команда работает только в личных сообщениях с ботом!")
        return

    # ========== КРАСНО-ЧЁРНЫЙ EMBED ==========
    embed = discord.Embed(
        title="🔴 **АДМИНИСТРАТИВНАЯ ПАНЕЛЬ** 🔴",
        description="**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                    "👑 **Добро пожаловать, Владелец бота!**\n"
                    "**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
                    "🎮 **Выбери команду из меню ниже**\n"
                    "⚡ **Управляй ботом как хочешь!**",
        color=COLOR_WHITE,
        timestamp=datetime.now()
    )

    total_members = sum(g.member_count for g in bot.guilds)
    embed.add_field(
        name="📊 **━━━━━━ СТАТИСТИКА ━━━━━━**",
        value=f"```yml\n"
              f"• Серверов:    {len(bot.guilds)}\n"
              f"• Пользователей: {total_members}\n"
              f"• Команд:      {len(bot.tree.get_commands())}\n"
              f"• Пинг:        {round(bot.latency * 1000)} ms\n"
              f"• uptime:      {str(datetime.now() - start_time).split('.')[0]}\n"
              f"• Память:      {round(os.getpid() / 1024 / 1024, 2)} MB```",
        inline=False
    )

    embed.add_field(
        name="⚡ **━━━━━ БЫСТРЫЕ КОМАНДЫ ━━━━━**",
        value="```fix\n"
              "📊 bari servers      - Список серверов\n"
              "📈 bari stats       - Детальная статистика\n"
              "💬 bari say         - Отправить сообщение\n"
              "🎨 bari embed       - Красивый embed\n"
              "📨 bari dm          - ЛС пользователю\n"
              "📢 bari broadcast   - Массовая рассылка\n"
              "📋 bari announce    - Анонс на сервер\n"
              "🚪 bari leaveg      - Покинуть сервер\n"
              "⚡ bari eval        - Выполнить код\n"
              "🗑️ bari clear       - Очистить чат\n"
              "🔧 bari gcmd        - Создать команду\n"
              "📋 bari listcmds    - Список команд\n"
              "🗑️ bari delcmd      - Удалить команду\n"
              "💾 bari backup      - Бэкап сервера\n"
              "🔄 bari reload      - Перезагрузить\n"
              "📊 bari dev         - Это меню```",
        inline=False
    )

    embed.add_field(
        name="📋 **━━━━━ ИНФОРМАЦИЯ ━━━━━**",
        value=f"```py\n"
              f"Бот:     {bot.user.name}\n"
              f"ID:      {bot.user.id}\n"
              f"Разработчик:  @{ctx.author.name}\n"
              f"Версия:  v3.0.0```",
        inline=False
    )

    embed.set_footer(text="bariier Bot | 🔴 АДМИНИСТРАТИВНАЯ ПАНЕЛЬ  🔴", icon_url=bot.user.avatar.url)
    embed.set_thumbnail(url=bot.user.avatar.url)

    # ========== ВЫПАДАЮЩЕЕ МЕНЮ ==========
    class DevSelect(discord.ui.Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="📊 Список серверов", value="servers",
                                     description="Показать все серверы с ID", emoji="📊"),
                discord.SelectOption(label="📈 Детальная статистика", value="stats",
                                     description="Полная статистика бота", emoji="📈"),
                discord.SelectOption(label="💬 Отправить сообщение", value="say",
                                     description="Отправить сообщение в канал", emoji="💬"),
                discord.SelectOption(label="🎨 Красивый embed", value="embed", description="Отправить красивый embed",
                                     emoji="🎨"),
                discord.SelectOption(label="📨 ЛС пользователю", value="dm",
                                     description="Отправить ЛС любому пользователю", emoji="📨"),
                discord.SelectOption(label="📢 Массовая рассылка", value="broadcast",
                                     description="Рассылка по всем серверам", emoji="📢"),
                discord.SelectOption(label="📋 Анонс на сервер", value="announce", description="Анонс в системный канал",
                                     emoji="📋"),
                discord.SelectOption(label="🚪 Покинуть сервер", value="leave", description="Бот покидает сервер",
                                     emoji="🚪"),
                discord.SelectOption(label="⚡ Выполнить код", value="eval", description="Выполнить Python код",
                                     emoji="⚡"),
                discord.SelectOption(label="🗑️ Очистить чат", value="clear", description="Очистить текущий канал",
                                     emoji="🗑️"),
                discord.SelectOption(label="🔧 Создать команду", value="gcmd", description="Создать глобальную команду",
                                     emoji="🔧"),
                discord.SelectOption(label="📋 Список команд", value="listcmds", description="Список созданных команд",
                                     emoji="📋"),
                discord.SelectOption(label="🗑️ Удалить команду", value="delcmd",
                                     description="Удалить созданную команду", emoji="🗑️"),
                discord.SelectOption(label="💾 Бэкап сервера", value="backup", description="Создать бэкап сервера",
                                     emoji="💾"),
                discord.SelectOption(label="🔄 Перезагрузить", value="reload", description="Перезагрузить команды",
                                     emoji="🔄"),
                discord.SelectOption(label="❌ Закрыть", value="cancel", description="Закрыть меню", emoji="❌"),
            ]
            super().__init__(placeholder="🔽 ВЫБЕРИ КОМАНДУ 🔽", options=options, min_values=1, max_values=1)

        async def callback(self, select_interaction: discord.Interaction):
            if select_interaction.user.id != ctx.author.id:
                return await select_interaction.response.send_message("❌ Это меню не для тебя!", ephemeral=True)

            selected = self.values[0]
            commands = {
                "servers": show_servers, "stats": show_stats, "say": ask_for_say,
                "embed": ask_for_embed, "dm": ask_for_dm, "broadcast": ask_for_broadcast,
                "announce": ask_for_announce, "leave": ask_for_leave, "eval": ask_for_eval,
                "clear": ask_for_clear, "gcmd": ask_for_gcmd, "listcmds": ask_for_listcmds,
                "delcmd": ask_for_delcmd, "backup": ask_for_backup, "reload": ask_for_reload,
                "cancel": cancel_menu,
            }
            if selected in commands:
                await commands[selected](select_interaction)

    class DevView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=120)
            self.add_item(DevSelect())

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)

    view = DevView()
    view.message = await ctx.send(embed=embed, view=view)


# =====================================================
# 🔴 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (КРАСНО-ЧЁРНЫЙ СТИЛЬ)
# =====================================================

async def show_servers(interaction: discord.Interaction):
    embed = discord.Embed(title="📊 **СПИСОК СЕРВЕРОВ**", description=f"```yml\nВсего серверов: {len(bot.guilds)}```",
                          color=COLOR_WHITE, timestamp=datetime.now())
    for guild in list(bot.guilds)[:25]:
        owner = guild.owner
        is_my = "👑" if owner and owner.id == interaction.user.id else "🔹"
        embed.add_field(name=f"{is_my} {guild.name}", value=f"🆔 `{guild.id}`\n👥 {guild.member_count} участников",
                        inline=True)
    if len(bot.guilds) > 25:
        embed.set_footer(text=f"Показано 25 из {len(bot.guilds)} серверов")

    class CloseView(discord.ui.View):
        @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.danger)
        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Панель закрыта", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=CloseView())


async def show_stats(interaction: discord.Interaction):
    total_members = sum(g.member_count for g in bot.guilds)
    total_channels = sum(len(g.channels) for g in bot.guilds)
    total_roles = sum(len(g.roles) for g in bot.guilds)
    embed = discord.Embed(title="📈 **ДЕТАЛЬНАЯ СТАТИСТИКА**", color=COLOR_WHITE, timestamp=datetime.now())
    embed.add_field(name="🖥️ **Сервера**", value=f"```yaml\n{len(bot.guilds)} серверов```", inline=True)
    embed.add_field(name="👥 **Пользователи**", value=f"```yaml\n{total_members} всего```", inline=True)
    embed.add_field(name="📁 **Каналы**", value=f"```yaml\n{total_channels} каналов```", inline=True)
    embed.add_field(name="🎭 **Роли**", value=f"```yaml\n{total_roles} ролей```", inline=True)
    embed.add_field(name="⚙️ **Команды**", value=f"```yaml\n{len(bot.tree.get_commands())} команд```", inline=True)
    embed.add_field(name="🟢 **Пинг**", value=f"```yaml\n{round(bot.latency * 1000)} ms```", inline=True)
    embed.add_field(name="⏰ **uptime**", value=f"```yaml\n{str(datetime.now() - start_time).split('.')[0]}```",
                    inline=True)
    embed.add_field(name="💾 **Память**", value=f"```yaml\n{round(os.getpid() / 1024 / 1024, 2)} MB```", inline=True)
    embed.set_footer(text="bariier Bot | 🔴 СТАТИСТИКА 🔴")

    class CloseView(discord.ui.View):
        @discord.ui.button(label="🔒 Закрыть", style=discord.ButtonStyle.danger)
        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Панель закрыта", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=CloseView())


async def ask_for_say(interaction: discord.Interaction):
    embed = discord.Embed(title="💬 **ОТПРАВИТЬ СООБЩЕНИЕ**",
                          description="```fix\nbari say <ID_КАНАЛА> <ТЕКСТ>\n```\n**Пример:**\n```py\n!say 123456789 Привет всем!```\n\n📝 **Как получить ID канала?**\nВключи режим разработчика → ПКМ по каналу → Копировать ID",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда say")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_embed(interaction: discord.Interaction):
    embed = discord.Embed(title="🎨 **ОТПРАВИТЬ EMBED**",
                          description="```fix\nbari embed <ID_КАНАЛА> <ЗАГОЛОВОК> | <ОПИСАНИЕ>\n```\n**Пример:**\n```py\n!embed 123456789 Важно! | Это важное сообщение```\n\n📝 **Разделитель:** `|` между заголовком и описанием",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда embed")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_dm(interaction: discord.Interaction):
    embed = discord.Embed(title="📨 **ЛС ПОЛЬЗОВАТЕЛЮ**",
                          description="```fix\nbari dm <ID_ПОЛЬЗОВАТЕЛЯ> <ТЕКСТ>\n```\n**Пример:**\n```py\n!dm 123456789 Привет! Как дела?```\n\n📝 **Как получить ID пользователя?**\nВключи режим разработчика → ПКМ по пользователю → Копировать ID",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда dm")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_broadcast(interaction: discord.Interaction):
    embed = discord.Embed(title="📢 **МАССОВАЯ РАССЫЛКА**",
                          description="```fix\nbari broadcast <ТЕКСТ>\n```\n**Пример:**\n```py\n!broadcast Внимание! У бота новое обновление!```\n\n⚠️ **Сообщение будет отправлено на ВСЕ сервера!**",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда broadcast")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_announce(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 **АНОНС НА СЕРВЕР**",
                          description="```fix\nbari announce <ID_СЕРВЕРА> <ТЕКСТ>\n```\n**Пример:**\n```py\n!announce 123456789 Внимание! Важное объявление!```\n\n📝 Анонс будет отправлен в **системный канал** сервера",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда announce")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_leave(interaction: discord.Interaction):
    embed = discord.Embed(title="🚪 **ПОКИНУТЬ СЕРВЕР**",
                          description="```fix\nbari leaveg <ID_СЕРВЕРА>\n```\n**Пример:**\n```py\n!leaveg 123456789```\n\n⚠️ **ВНИМАНИЕ!**\nБот **навсегда покинет сервер**! Вернуть можно только через повторное приглашение.",
                          color=COLOR_WHITE)
    embed.add_field(name="📝 Как получить ID сервера?",
                    value="Включи режим разработчика → ПКМ по серверу → Копировать ID", inline=False)
    embed.set_footer(text="bariier Bot | 🔴 Команда leaveg")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_eval(interaction: discord.Interaction):
    embed = discord.Embed(title="⚡ **ВЫПОЛНИТЬ PYTHON КОД**",
                          description="```fix\nbari eval <КОД>\n```\n**Пример:**\n```py\n!eval print('Hello World!')```\n\n**Многострочный код:**\n```py\n!eval \nfor i in range(5):\n    print(i)```\n\n⚠️ **ОСТОРОЖНО!**\nНеправильный код может сломать бота!",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда eval")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_clear(interaction: discord.Interaction):
    embed = discord.Embed(title="🗑️ **ОЧИСТИТЬ ЧАТ**",
                          description="```fix\nbari clear <КОЛИЧЕСТВО>\n```\n**Пример:**\n```py\n!clear 50```\n\n📊 **Лимит:** максимум 100 сообщений\n📍 **Работает только на сервере, не в ЛС!**",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда clear")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_gcmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🔧 **СОЗДАТЬ КОМАНДУ**",
                          description="```fix\nbari gcmd <НАЗВАНИЕ> <ОПИСАНИЕ>\n```\n**Пример:**\n```py\n!gcmd hello Приветствие от бота```\n\n✨ Команда появится на **всех серверах** после перезапуска!",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда gcmd")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_listcmds(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 **СПИСОК КОМАНД**",
                          description="```fix\nbari listcmds\n```\n\n📋 Покажет все созданные вами команды", color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда listcmds")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_delcmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🗑️ **УДАЛИТЬ КОМАНДУ**",
                          description="```fix\nbari delcmd <НАЗВАНИЕ>\n```\n**Пример:**\n```py\n!delcmd hello```\n\n⚠️ Команда будет удалена после перезапуска бота!",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда delcmd")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_backup(interaction: discord.Interaction):
    embed = discord.Embed(title="💾 **СОЗДАТЬ БЭКАП**",
                          description="```fix\nbari backup <ID_СЕРВЕРА>\n```\n**Пример:**\n```py\n!backup 123456789```\n\n📦 **Будут сохранены:**\n• Все настройки бота (JSON файлы)\n• Структура сервера (роли, каналы)\n• Конфигурация команд\n\n✅ Бэкап отправится сюда в ЛС!",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда backup")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def ask_for_reload(interaction: discord.Interaction):
    embed = discord.Embed(title="🔄 **ПЕРЕЗАГРУЗИТЬ КОМАНДЫ**",
                          description="```fix\nbari reload\n```\n\n🔄 **Что произойдёт:**\n• Синхронизация слеш-команд\n• Перезагрузка всех команд бота\n• Обновление статуса\n\n⏱️ Процесс займёт несколько секунд!",
                          color=COLOR_WHITE)
    embed.set_footer(text="bariier Bot | 🔴 Команда reload")

    class ActionView(discord.ui.View):
        @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.danger)
        async def cancel(self, btn_i: discord.Interaction, button: discord.ui.Button):
            await btn_interaction.response.edit_message(content="🔒 Команда отменена", embed=None, view=None)

    await interaction.response.edit_message(embed=embed, view=ActionView())


async def cancel_menu(interaction: discord.Interaction):
    embed = discord.Embed(title="🔒 **МЕНЮ ЗАКРЫТО**", description="Для вызова меню снова напишите `!dev`",
                          color=COLOR_WHITE)
    await interaction.response.edit_message(embed=embed, view=None)


# =====================================================
# 🔴 ОСНОВНЫЕ КОМАНДЫ (КРАСНО-ЧЁРНЫЙ СТИЛЬ)
# =====================================================

@bot.command(name='servers')
async def dev_servers(ctx):
    if ctx.author.id != 1436760469980450816:
        return
    embed = discord.Embed(title="📊 Список серверов", description=f"Всего серверов: **{len(bot.guilds)}**",
                          color=COLOR_WHITE, timestamp=datetime.now())
    for guild in bot.guilds:
        owner = guild.owner
        is_my = "👑 **ВАШ**" if owner and owner.id == ctx.author.id else ""
        embed.add_field(name=f"{guild.name}",
                        value=f"🆔 ID: `{guild.id}`\n👑 Владелец: {owner.name if owner else 'Неизвестен'}\n👥 Участников: {guild.member_count}\n{is_my}",
                        inline=False)
    await ctx.send(embed=embed)


@bot.command(name='stats')
async def dev_stats(ctx):
    if ctx.author.id != 1436760469980450816:
        return
    total_members = sum(g.member_count for g in bot.guilds)
    total_channels = sum(len(g.channels) for g in bot.guilds)
    total_roles = sum(len(g.roles) for g in bot.guilds)
    embed = discord.Embed(title="📊 Детальная статистика", color=COLOR_WHITE, timestamp=datetime.now())
    embed.add_field(name="🖥️ Серверов", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="👥 Пользователей", value=f"`{total_members}`", inline=True)
    embed.add_field(name="📁 Каналов", value=f"`{total_channels}`", inline=True)
    embed.add_field(name="🎭 Ролей", value=f"`{total_roles}`", inline=True)
    embed.add_field(name="⚙️ Команд", value=f"`{len(bot.tree.get_commands())}`", inline=True)
    embed.add_field(name="🟢 Пинг", value=f"`{round(bot.latency * 1000)} ms`", inline=True)
    embed.add_field(name="⏰ uptime", value=f"`{str(datetime.now() - start_time).split('.')[0]}`", inline=True)
    embed.add_field(name="💾 Память", value=f"`{round(os.getpid() / 1024 / 1024, 2)} MB`", inline=True)
    embed.set_footer(text="bariier Bot | 🔴 DEV STATS")
    await ctx.send(embed=embed)


@bot.command(name='say')
async def dev_say(ctx, channel_id: int, *, message: str):
    if ctx.author.id != 1436760469980450816:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)
        await ctx.send(f"✅ Сообщение отправлено в канал `{channel.name}` (ID: {channel_id})")
    else:
        await ctx.send("❌ Канал не найден!")


@bot.command(name='embed')
async def dev_embed(ctx, channel_id: int, *, title_desc: str):
    if ctx.author.id != 1436760469980450816:
        return
    if "|" not in title_desc:
        await ctx.send("❌ Используй формат: `!embed <ID> <ЗАГОЛОВОК> | <ОПИСАНИЕ>`")
        return
    title, description = title_desc.split("|", 1)
    title = title.strip()
    description = description.strip()
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("❌ Канал не найден!")
        return
    embed = discord.Embed(title=title, description=description, color=COLOR_WHITE, timestamp=datetime.now())
    embed.set_footer(text="Отправлено через bariier Bot")
    await channel.send(embed=embed)
    await ctx.send(f"✅ Embed отправлен в канал `{channel.name}` (ID: {channel_id})")


@bot.command(name='dm')
async def dev_dm(ctx, user_id: int, *, message: str):
    if ctx.author.id != 1436760469980450816:
        return
    try:
        user = await bot.fetch_user(user_id)
        await user.send(message)
        await ctx.send(f"✅ Сообщение отправлено пользователю **{user.name}** (ID: {user_id})")
    except discord.NotFound:
        await ctx.send("❌ Пользователь не найден!")
    except discord.Forbidden:
        await ctx.send("❌ Не могу отправить сообщение (закрыты ЛС)")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")


@bot.command(name='broadcast')
async def dev_broadcast(ctx, *, message: str):
    if ctx.author.id != 1436760469980450816:
        return
    await ctx.send(f"📢 Начинаю рассылку на **{len(bot.guilds)}** серверов...")
    success = 0
    failed = 0
    for guild in bot.guilds:
        try:
            channel = guild.system_channel or guild.text_channels[0]
            await channel.send(f"📢 **Анонс от разработчика:**\n{message}")
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1
    await ctx.send(f"✅ Рассылка завершена!\n• Успешно: {success}\n• Ошибок: {failed}")


@bot.command(name='announce')
async def dev_announce(ctx, guild_id: int, *, message: str):
    if ctx.author.id != 1436760469980450816:
        return
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден!")
        return
    channel = guild.system_channel or guild.text_channels[0]
    if not channel:
        await ctx.send(f"❌ На сервере **{guild.name}** нет доступных каналов!")
        return
    embed = discord.Embed(title="📢 **АНОНС**", description=message, color=COLOR_WHITE, timestamp=datetime.now())
    embed.set_footer(text="bariier Bot | Администрация")
    await channel.send(embed=embed)
    await ctx.send(f"✅ Анонс отправлен на сервер **{guild.name}** в канал `{channel.name}`")


@bot.command(name='leaveg')
async def dev_leave(ctx, guild_id: int):
    if ctx.author.id != 1436760469980450816:
        return
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден!")
        return
    await ctx.send(f"👋 Покидаю сервер **{guild.name}** (ID: `{guild_id}`)...")
    await guild.leave()
    await ctx.send(f"✅ Бот покинул сервер **{guild.name}**")


@bot.command(name='eval')
async def dev_eval(ctx, *, code: str):
    if ctx.author.id != 1436760469980450816:
        return
    if code.startswith("```") and code.endswith("```"):
        code = code[3:-3]
        if code.startswith("python"):
            code = code[6:]
    try:
        result = eval(code)
        if result is not None:
            await ctx.send(f"```\n{result}```")
    except Exception as e:
        await ctx.send(f"❌ Ошибка: ```\n{e}```")


@bot.command(name='clear')
async def dev_clear(ctx, amount: int = 10):
    if ctx.author.id != 1436760469980450816:
        return
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ Удалено {len(deleted) - 1} сообщений")
    await asyncio.sleep(2)
    await msg.delete()


@bot.command(name='gcmd')
async def dev_gcmd(ctx, name: str, *, description: str = "Нет описания"):
    if tech_work_active and interaction.user.id != YOUR_ID:
        await interaction.response.send_message("🔧 Идут технические работы. Бот временно недоступен.", ephemeral=True)
        return
    if ctx.author.id != 1436760469980450816:
        return

    CUSTOM_COMMANDS_FILE = 'custom_commands.json'

    def load_custom_commands():
        if os.path.exists(CUSTOM_COMMANDS_FILE):
            with open(CUSTOM_COMMANDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_custom_commands(cmds):
        with open(CUSTOM_COMMANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(cmds, f, indent=4, ensure_ascii=False)

    @bot.tree.command(name=name, description=description)
    async def custom_cmd(i: discord.Interaction):
        await interaction.response.send_message(f"✅ Команда `/{name}` работает! (пока без логики)", ephemeral=True)

    cmds = load_custom_commands()
    cmds[name] = {'description': description, 'created': str(datetime.now())}
    save_custom_commands(cmds)

    try:
        await bot.tree.sync()
        embed = discord.Embed(title="✅ Глобальная команда создана", description=f"**/{name}** - {description}",
                              color=COLOR_WHITE)
        embed.add_field(name="📝 Примечание", value="Команда появится на всех серверах в течение нескольких минут",
                        inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Ошибка при создании команды: {e}")


@bot.command(name='listcmds')
async def dev_listcmds(ctx):
    if ctx.author.id != 1436760469980450816:
        return
    CUSTOM_COMMANDS_FILE = 'custom_commands.json'
    if not os.path.exists(CUSTOM_COMMANDS_FILE):
        await ctx.send("❌ Нет созданных пользовательских команд!")
        return
    with open(CUSTOM_COMMANDS_FILE, 'r', encoding='utf-8') as f:
        cmds = json.load(f)
    if not cmds:
        await ctx.send("❌ Нет созданных пользовательских команд!")
        return
    embed = discord.Embed(title="📋 **ПОЛЬЗОВАТЕЛЬСКИЕ КОМАНДЫ**", description=f"Всего команд: {len(cmds)}",
                          color=COLOR_WHITE)
    for name, data in cmds.items():
        embed.add_field(name=f"/{name}",
                        value=f"📝 {data.get('description', 'Нет описания')}\n🕐 Создана: {data.get('created', 'Неизвестно')}",
                        inline=False)
    await ctx.send(embed=embed)


@bot.command(name='delcmd')
async def dev_delcmd(ctx, name: str):
    if ctx.author.id != 1436760469980450816:
        return
    CUSTOM_COMMANDS_FILE = 'custom_commands.json'
    if not os.path.exists(CUSTOM_COMMANDS_FILE):
        await ctx.send("❌ Нет созданных пользовательских команд!")
        return
    with open(CUSTOM_COMMANDS_FILE, 'r', encoding='utf-8') as f:
        cmds = json.load(f)
    if name not in cmds:
        await ctx.send(f"❌ Команда `/{name}` не найдена!")
        return
    del cmds[name]
    with open(CUSTOM_COMMANDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(cmds, f, indent=4, ensure_ascii=False)
    await ctx.send(f"✅ Команда `/{name}` удалена! Перезапусти бота для применения изменений.")


@bot.command(name='backup')
async def dev_backup(ctx, guild_id: int = None):
    if ctx.author.id != 1436760469980450816:
        return
    if guild_id is None:
        if len(bot.guilds) == 0:
            await ctx.send("❌ Бот не состоит ни на одном сервере!")
            return
        guild = bot.guilds[0]
        await ctx.send(f"⚠️ ID сервера не указан! Создаю бэкап сервера **{guild.name}** (ID: {guild.id})")
    else:
        guild = bot.get_guild(guild_id)
        if not guild:
            await ctx.send(f"❌ Сервер с ID `{guild_id}` не найден!")
            return
    await ctx.send(f"📦 **Начинаю создание бэкапа сервера `{guild.name}`...**\nЭто может занять некоторое время ⏳")
    backup_data = {
        'backup_info': {'created_at': str(datetime.now()), 'server_name': guild.name, 'server_id': guild.id,
                        'owner_id': guild.owner_id, 'owner_name': str(guild.owner) if guild.owner else 'Unknown',
                        'member_count': guild.member_count, 'bot_name': bot.user.name, 'bot_id': bot.user.id},
        'roles': [], 'categories': [], 'channels': [], 'emojis': [], 'stickers': []
    }
    await ctx.send("📋 Сохраняю роли...")
    for role in guild.roles:
        backup_data['roles'].append(
            {'name': role.name, 'id': role.id, 'color': role.color.value, 'position': role.position,
             'hoist': role.hoist, 'mentionable': role.mentionable, 'permissions': role.permissions.value,
             'created_at': str(role.created_at)})
    await ctx.send("📁 Сохраняю категории...")
    for category in guild.categories:
        backup_data['categories'].append({'name': category.name, 'id': category.id, 'position': category.position,
                                          'created_at': str(category.created_at)})
    await ctx.send("💬 Сохраняю каналы...")
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            backup_data['channels'].append(
                {'type': 'text', 'name': channel.name, 'id': channel.id, 'category_id': channel.category_id,
                 'position': channel.position, 'topic': channel.topic, 'slowmode_delay': channel.slowmode_delay,
                 'is_nsfw': channel.is_nsfw(), 'created_at': str(channel.created_at)})
        elif isinstance(channel, discord.VoiceChannel):
            backup_data['channels'].append(
                {'type': 'voice', 'name': channel.name, 'id': channel.id, 'category_id': channel.category_id,
                 'position': channel.position, 'bitrate': channel.bitrate, 'user_limit': channel.user_limit,
                 'created_at': str(channel.created_at)})
    await ctx.send("😀 Сохраняю эмодзи...")
    for emoji in guild.emojis:
        backup_data['emojis'].append(
            {'name': emoji.name, 'id': emoji.id, 'animated': emoji.animated, 'created_at': str(emoji.created_at)})
    await ctx.send("🎨 Сохраняю стикеры...")
    for sticker in guild.stickers:
        backup_data['stickers'].append({'name': sticker.name, 'id': sticker.id, 'description': sticker.description,
                                        'created_at': str(sticker.created_at)})
    await ctx.send("⚙️ Сохраняю настройки бота...")
    settings_files = ['lang_settings.json', 'bariier_settings.json', 'logs_settings.json', 'captcha_settings.json',
                      'welcome_settings.json', 'warns.json', 'tickets.json', 'ticket_settings.json',
                      'reaction_roles.json', 'autorole_settings.json', 'regex_settings.json', 'applications.json']
    backup_data['bot_settings'] = {}
    for file in settings_files:
        if os.path.exists(file):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    backup_data['bot_settings'][file] = json.load(f)
            except:
                backup_data['bot_settings'][file] = f"Ошибка при чтении файла {file}"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{guild.name}_{guild.id}_{timestamp}.json"
    import re
    backup_filename = re.sub(r'[<>:"/\\|?*]', '_', backup_filename)
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    file_size = os.path.getsize(backup_filename) / 1024
    embed = discord.Embed(title="💾 **БЭКАП СОЗДАН**",
                          description=f"✅ Сервер: **{guild.name}**\n🆔 ID: `{guild.id}`\n📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n📦 Размер: `{round(file_size, 2)} KB`\n\n**📊 Статистика бэкапа:**\n• Ролей: `{len(backup_data['roles'])}`\n• Категорий: `{len(backup_data['categories'])}`\n• Каналов: `{len(backup_data['channels'])}`\n• Эмодзи: `{len(backup_data['emojis'])}`\n• Стикеров: `{len(backup_data['stickers'])}`\n• Файлов настроек: `{len(backup_data['bot_settings'])}`",
                          color=COLOR_WHITE, timestamp=datetime.now())
    embed.set_footer(text="bariier Bot | 🔴 Бэкап сервера")
    await ctx.send(embed=embed)
    with open(backup_filename, 'rb') as f:
        await ctx.send(file=discord.File(f, backup_filename))
    os.remove(backup_filename)
    await ctx.send("✅ **Бэкап завершён!** Файл сохранён в этом чате. Храни его в надёжном месте.")


# ========== КОМАНДА НАСТРОЙКИ ==========
@bot.tree.command(name='setup-private-voice', description='🎤 Настроить систему личных голосовых каналов')
@app_commands.describe(
    join_channel="Канал для создания личного войса (зайди чтобы создать свой канал)",
    panel_channel="Канал, куда отправить панель управления",
    category="Категория для личных каналов (опционально)"
)
async def setup_private_voice(
        interaction: discord.Interaction,
        join_channel: discord.VoiceChannel,
        panel_channel: discord.TextChannel,
        category: discord.CategoryChannel = None
):
    i = interaction

    if tech_work_active and i.user.id != YOUR_ID:
        await i.response.send_message("🔧 Техработы", ephemeral=True)
        return

    if not i.user.guild_permissions.administrator:
        await i.response.send_message("❌ Нужны права администратора!", ephemeral=True)
        return

    # Сохраняем настройки
    settings = load_private_voice_settings()
    gid = str(i.guild.id)

    settings[gid] = {
        'join_channel_id': join_channel.id,
        'panel_channel_id': panel_channel.id,
        'category_id': category.id if category else None,
    }
    save_private_voice_settings(settings)

    # Отправляем панель управления в указанный канал
    await send_voice_panel(panel_channel, i.guild, join_channel)

    # Подтверждение админу
    embed = discord.Embed(
        title="🎤 Личные голосовые каналы настроены",
        description=f"✅ **Канал входа:** {join_channel.mention}\n"
                    f"✅ **Канал панели:** {panel_channel.mention}\n"
                    f"✅ **Категория:** {category.mention if category else 'Та же, что и канал входа'}\n\n"
                    f"📌 **Как работает:**\n"
                    f"1. Любой пользователь заходит в {join_channel.mention}\n"
                    f"2. Бот создаёт личный канал с его ником\n"
                    f"3. В {panel_channel.mention} появилась панель управления\n"
                    f"4. Когда выходит — канал удаляется",
        color=discord.Color.green()
    )
    await i.response.send_message(embed=embed, ephemeral=True)


# ========== ФУНКЦИЯ ОТПРАВКИ ПАНЕЛИ В КАНАЛ ==========
class VoicePanelPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎤 Управлять каналом", style=discord.ButtonStyle.primary, emoji="🎤", row=0,
                       custom_id="voice_panel_manage")
    async def open_panel(self, btn_i: discord.Interaction, button: discord.ui.Button):
        if str(btn_i.user.id) not in user_voice_channels:
            # Пытаемся найти join_channel из настроек
            settings = load_private_voice_settings()
            gid = str(btn_i.guild.id)
            join_ch_mention = "канал входа"
            if gid in settings:
                jcid = settings[gid].get('join_channel_id')
                if jcid:
                    jc = btn_i.guild.get_channel(jcid)
                    if jc:
                        join_ch_mention = jc.mention
            embed_error = discord.Embed(
                title="❌ **ОШИБКА**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  У тебя нет личного голосового   │\n"
                            f"│  канала! Зайди в {join_ch_mention}   │\n"
                            f"└─────────────────────────────────┘",
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            await btn_i.response.send_message(embed=embed_error, ephemeral=True)
            return

        channel_id = user_voice_channels[str(btn_i.user.id)]
        voice_channel = btn_i.guild.get_channel(channel_id)

        if not voice_channel:
            await btn_i.response.send_message("❌ Твой голосовой канал не найден!", ephemeral=True)
            return

        await send_control_panel(btn_i, voice_channel)


async def send_voice_panel(channel: discord.TextChannel, guild: discord.Guild, join_channel: discord.VoiceChannel):
    """Отправляет панель управления голосовыми каналами"""

    embed = discord.Embed(
        title="**VoiceMaster Interface**",
        description="Manage your voice channel by using the buttons below.\n"
                    "**Button Usage**\n"
                    "     🔒-`Lock`         Закрыть канал\n"
                    "     🔓-`Unlock`       Открыть канал\n"
                    "     👻-`Hide`         Скрыть канал\n"
                    "     👁️-`Reveal`       Показать канал\n"
                    "     📝-`Rename`       Переименовать\n"
                    "     👥-`Limit +`      Увеличить лимит\n"
                    "     👥-`Limit -`      Уменьшить лимит\n"
                    "     🎤-`Bitrate`      Качество звука\n"
                    "     👑-`Transfer`     Передать владельца\n"
                    "     🗑️-`Delete`       Удалить канал",
        color=discord.Color.from_rgb(114, 137, 218)
    )
    embed.set_footer(text="VoiceMaster • Нажми на кнопку чтобы управлять своим каналом", icon_url=bot.user.avatar.url)

    await channel.send(embed=embed, view=VoicePanelPersistentView())


# ========== ФУНКЦИЯ ПАНЕЛИ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ==========
async def send_control_panel(interaction: discord.Interaction, channel: discord.VoiceChannel):
    """Отправляет панель управления личным каналом"""
    i = interaction
    owner_id = None

    for uid, cid in user_voice_channels.items():
        if cid == channel.id:
            owner_id = int(uid)
            break

    if not owner_id:
        await i.response.send_message("❌ Владелец канала не найден!", ephemeral=True)
        return

    is_owner = (i.user.id == owner_id)
    member_count = len(channel.members)
    user_limit = channel.user_limit if channel.user_limit else "∞"

    # Проверяем статусы
    is_locked = False
    is_hidden = False
    for overwrite, perms in channel.overwrites.items():
        if overwrite == i.guild.default_role:
            if perms.connect is False:
                is_locked = True
            if perms.view_channel is False:
                is_hidden = True

    embed = discord.Embed(
        title=f"🎤 **━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
              f"          **{channel.name[:50]}**\n"
              f"**━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━**",
        description="═══════════════════════════════════\n"
                    "            **ИНФОРМАЦИЯ**\n"
                    "═══════════════════════════════════\n\n"
                    f"┌─────────────────────────────────┐\n"
                    f"│  📢 **Канал:**      {channel.mention}   │\n"
                    f"│  👥 **Участники:**  {member_count}/{user_limit}            │\n"
                    f"│  🎤 **Битрейт:**    {channel.bitrate // 1000} kbps              │\n"
                    f"└─────────────────────────────────┘\n\n"
                    "═══════════════════════════════════\n"
                    "            **СТАТУСЫ**\n"
                    "═══════════════════════════════════\n\n"
                    f"┌─────────────────────────────────┐\n"
                    f"│  🔒 **Закрыт:**      {'✅ ДА' if is_locked else '❌ НЕТ'}                │\n"
                    f"│  👻 **Скрыт:**       {'✅ ДА' if is_hidden else '❌ НЕТ'}                │\n"
                    f"│  👑 **Владелец:**    <@{owner_id}>    │\n"
                    f"└─────────────────────────────────┘\n\n"
                    "═══════════════════════════════════\n"
                    "          **🎮 УПРАВЛЕНИЕ**\n"
                    "═══════════════════════════════════",
        color=discord.Color.from_rgb(114, 137, 218)
    )
    embed.set_footer(text="VoiceMaster • Только владелец может управлять каналом", icon_url=bot.user.avatar.url)

    class ControlPanel(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=180)

        async def check_owner(self, btn_i: discord.Interaction):
            if not is_owner:
                embed_error = discord.Embed(
                    title="⛔ **ДОСТУП ЗАПРЕЩЁН**",
                    description="┌─────────────────────────────────┐\n"
                                "│  Эта команда доступна только    │\n"
                                "│  владельцу голосового канала!   │\n"
                                "└─────────────────────────────────┘",
                    	color=discord.Color.from_rgb(255, 255, 255)
                )
                await btn_i.response.send_message(embed=embed_error, ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Lock", style=discord.ButtonStyle.danger, emoji="🔒", row=0)
        async def lock_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            await channel.set_permissions(btn_i.guild.default_role, connect=False)
            embed_success = discord.Embed(
                title="🔒 **КАНАЛ ЗАКРЫТ**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Канал **{channel.name}** закрыт!     │\n"
                            f"│  Никто не сможет зайти.           │\n"
                            f"└─────────────────────────────────┘",
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success, emoji="🔓", row=0)
        async def unlock_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            await channel.set_permissions(btn_i.guild.default_role, connect=None)
            embed_success = discord.Embed(
                title="🔓 **КАНАЛ ОТКРЫТ**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Канал **{channel.name}** открыт!     │\n"
                            f"│  Теперь все могут заходить.      │\n"
                            f"└─────────────────────────────────┘",
                color=discord.Color.green()
            )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Hide", style=discord.ButtonStyle.secondary, emoji="👻", row=1)
        async def hide_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            await channel.set_permissions(btn_i.guild.default_role, view_channel=False)
            embed_success = discord.Embed(
                title="👻 **КАНАЛ СКРЫТ**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Канал **{channel.name}** скрыт!      │\n"
                            f"│  Его никто не видит в списке.    │\n"
                            f"└─────────────────────────────────┘",
                color=discord.Color.dark_gray()
            )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Reveal", style=discord.ButtonStyle.primary, emoji="👁️", row=1)
        async def reveal_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            await channel.set_permissions(btn_i.guild.default_role, view_channel=True)
            embed_success = discord.Embed(
                title="👁️ **КАНАЛ ПОКАЗАН**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Канал **{channel.name}** снова виден! │\n"
                            f"└─────────────────────────────────┘",
                color=discord.Color.blue()
            )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary, emoji="📝", row=2)
        async def rename_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return

            class RenameModal(discord.ui.Modal):
                def __init__(self, ch):
                    super().__init__(title="📝 Переименовать канал")
                    self.ch = ch
                    self.add_item(discord.ui.TextInput(
                        label="Новое название",
                        placeholder="Введи новое название канала...",
                        default=ch.name,
                        max_length=100,
                        required=True,
                        style=discord.TextStyle.short
                    ))

                async def on_submit(self, modal_i: discord.Interaction):
                    new_name = self.children[0].value
                    await self.ch.edit(name=new_name)
                    embed_success = discord.Embed(
                        title="✅ **ПЕРЕИМЕНОВАНО**",
                        description=f"┌─────────────────────────────────┐\n"
                                    f"│  Канал переименован в           │\n"
                                    f"│  **{new_name}** │\n"
                                    f"└─────────────────────────────────┘",
                        color=discord.Color.green()
                    )
                    await modal_i.response.send_message(embed=embed_success, ephemeral=True)
                    await send_control_panel(modal_i, self.ch)

            await btn_i.response.send_modal(RenameModal(channel))

        @discord.ui.button(label="Limit +", style=discord.ButtonStyle.success, emoji="➕", row=2)
        async def limit_plus(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            current = channel.user_limit if channel.user_limit else 0
            if current == 0:
                new_limit = 5
            else:
                new_limit = min(current + 5, 99)
            await channel.edit(user_limit=new_limit if new_limit > 0 else None)
            embed_success = discord.Embed(
                title="➕ **ЛИМИТ УВЕЛИЧЕН**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Новый лимит участников:         │\n"
                            f"│  **{new_limit if new_limit > 0 else '∞'}**                  │\n"
                            f"└─────────────────────────────────┘",
                color=discord.Color.green()
            )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Limit -", style=discord.ButtonStyle.danger, emoji="➖", row=2)
        async def limit_minus(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return
            current = channel.user_limit if channel.user_limit else 0
            if current <= 0:
                new_limit = 95
            else:
                new_limit = max(current - 5, 0)
            await channel.edit(user_limit=new_limit if new_limit > 0 else None)
            if new_limit <= 0:
                embed_success = discord.Embed(
                    title="➖ **ЛИМИТ СНЯТ**",
                    description=f"┌─────────────────────────────────┐\n"
                                f"│  Лимит участников снят (∞)      │\n"
                                f"└─────────────────────────────────┘",
                    color=discord.Color.orange()
                )
            else:
                embed_success = discord.Embed(
                    title="➖ **ЛИМИТ УМЕНЬШЕН**",
                    description=f"┌─────────────────────────────────┐\n"
                                f"│  Новый лимит участников:         │\n"
                                f"│  **{new_limit}**                  │\n"
                                f"└─────────────────────────────────┘",
                    color=discord.Color.orange()
                )
            await btn_i.response.send_message(embed=embed_success, ephemeral=True)
            await send_control_panel(btn_i, channel)

        @discord.ui.button(label="Bitrate", style=discord.ButtonStyle.primary, emoji="🎤", row=3)
        async def bitrate_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return

            class BitrateModal(discord.ui.Modal):
                def __init__(self, ch):
                    super().__init__(title="🎤 Качество звука")
                    self.ch = ch
                    self.add_item(discord.ui.TextInput(
                        label="Битрейт (kbps)",
                        placeholder="64, 96, 128, 256, 384...",
                        default=str(ch.bitrate // 1000),
                        max_length=3,
                        required=True,
                        style=discord.TextStyle.short
                    ))

                async def on_submit(self, modal_i: discord.Interaction):
                    try:
                        bitrate = int(self.children[0].value) * 1000
                        if bitrate < 8000 or bitrate > 384000:
                            embed_error = discord.Embed(
                                title="❌ **ОШИБКА**",
                                description="┌─────────────────────────────────┐\n"
                                            "│  Битрейт должен быть от 8 до    │\n"
                                            "│  384 kbps!                       │\n"
                                            "└─────────────────────────────────┘",
                                	color=discord.Color.from_rgb(255, 255, 255)
                            )
                            await modal_i.response.send_message(embed=embed_error, ephemeral=True)
                            return
                        await self.ch.edit(bitrate=bitrate)
                        embed_success = discord.Embed(
                            title="🎤 **БИТРЕЙТ ИЗМЕНЁН**",
                            description=f"┌─────────────────────────────────┐\n"
                                        f"│  Новый битрейт:                 │\n"
                                        f"│  **{bitrate // 1000} kbps**               │\n"
                                        f"└─────────────────────────────────┘",
                            color=discord.Color.green()
                        )
                        await modal_i.response.send_message(embed=embed_success, ephemeral=True)
                        await send_control_panel(modal_i, self.ch)
                    except:
                        embed_error = discord.Embed(
                            title="❌ **ОШИБКА**",
                            description="┌─────────────────────────────────┐\n"
                                        "│  Введи корректное число!        │\n"
                                        "└─────────────────────────────────┘",
                            	color=discord.Color.from_rgb(255, 255, 255)
                        )
                        await modal_i.response.send_message(embed=embed_error, ephemeral=True)

            await btn_i.response.send_modal(BitrateModal(channel))

        @discord.ui.button(label="Transfer", style=discord.ButtonStyle.primary, emoji="👑", row=3)
        async def transfer_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return

            members = [m for m in channel.members if m.id != owner_id]
            if not members:
                embed_error = discord.Embed(
                    title="❌ **ОШИБКА**",
                    description="┌─────────────────────────────────┐\n"
                                "│  В твоём канале нет других      │\n"
                                "│  участников!                     │\n"
                                "└─────────────────────────────────┘",
                    	color=discord.Color.from_rgb(255, 255, 255)
                )
                await btn_i.response.send_message(embed=embed_error, ephemeral=True)
                return

            class MemberSelect(discord.ui.Select):
                def __init__(self, members_list, ch, owner):
                    options = [discord.SelectOption(label=m.name, value=str(m.id), emoji="👤") for m in
                               members_list[:25]]
                    super().__init__(placeholder="📋 Выбери нового владельца...", options=options)
                    self.channel = ch
                    self.owner_id = owner

                async def callback(self, select_i: discord.Interaction):
                    new_owner_id = int(self.values[0])
                    new_owner = select_i.guild.get_member(new_owner_id)

                    del user_voice_channels[str(self.owner_id)]
                    user_voice_channels[str(new_owner_id)] = self.channel.id

                    embed_success = discord.Embed(
                        title="👑 **ВЛАДЕЛЕЦ ПЕРЕДАН**",
                        description=f"┌─────────────────────────────────┐\n"
                                    f"│  Новый владелец канала:         │\n"
                                    f"│  {new_owner.mention} │\n"
                                    f"└─────────────────────────────────┘",
                        color=discord.Color.gold()
                    )
                    await select_i.response.send_message(embed=embed_success, ephemeral=True)
                    await send_control_panel(select_i, self.channel)

            view = discord.ui.View()
            view.add_item(MemberSelect(members, channel, owner_id))
            await btn_i.response.send_message("🎤 **Выбери нового владельца канала:**", view=view, ephemeral=True)

        @discord.ui.button(label="Info", style=discord.ButtonStyle.secondary, emoji="ℹ️", row=4)
        async def info_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return

            members_list = "\n".join([f"     {m.mention}" for m in channel.members[:10]])
            if len(channel.members) > 10:
                members_list += f"\n     ... и ещё {len(channel.members) - 10}"

            embed_info = discord.Embed(
                title=f"ℹ️ **ИНФОРМАЦИЯ О КАНАЛЕ**",
                description="═══════════════════════════════════",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed_info.add_field(name="📢 **Название**", value=f"`{channel.name}`", inline=False)
            embed_info.add_field(name="🆔 **ID канала**", value=f"`{channel.id}`", inline=True)
            embed_info.add_field(name="👑 **Владелец**", value=f"<@{owner_id}>", inline=True)
            embed_info.add_field(name="👥 **Участники**",
                                 value=f"┌─────────────────────────────────┐\n{members_list if members_list else '     Пусто'}\n└─────────────────────────────────┘",
                                 inline=False)
            embed_info.add_field(name="🎤 **Битрейт**", value=f"`{channel.bitrate // 1000} kbps`", inline=True)
            embed_info.add_field(name="👥 **Лимит**", value=f"`{user_limit}`", inline=True)
            embed_info.add_field(name="🔒 **Статус**", value=f"`{'Закрыт' if is_locked else 'Открыт'}`", inline=True)
            embed_info.add_field(name="👻 **Видимость**", value=f"`{'Скрыт' if is_hidden else 'Виден'}`", inline=True)
            embed_info.add_field(name="📅 **Создан**", value=f"<t:{int(channel.created_at.timestamp())}:R>",
                                 inline=False)
            embed_info.set_footer(text="VoiceMaster • Полная информация о канале")

            await btn_i.response.send_message(embed=embed_info, ephemeral=True)

        @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️", row=4)
        async def delete_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            if not await self.check_owner(btn_i): return

            class ConfirmView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)

                @discord.ui.button(label="✅ Да, удалить", style=discord.ButtonStyle.danger, emoji="✅", row=0)
                async def confirm(self, conf_i: discord.Interaction, button: discord.ui.Button):
                    del user_voice_channels[str(owner_id)]
                    await channel.delete()
                    embed_success = discord.Embed(
                        title="🗑️ **КАНАЛ УДАЛЁН**",
                        description=f"┌─────────────────────────────────┐\n"
                                    f"│  Канал **{channel.name}** удалён.  │\n"
                                    f"└─────────────────────────────────┘",
                        	color=discord.Color.from_rgb(255, 255, 255)
                    )
                    await conf_i.response.send_message(embed=embed_success, ephemeral=True)
                    self.stop()

                @discord.ui.button(label="❌ Отмена", style=discord.ButtonStyle.secondary, emoji="❌", row=0)
                async def cancel(self, conf_i: discord.Interaction, button: discord.ui.Button):
                    embed_cancel = discord.Embed(
                        title="❌ **ОТМЕНА**",
                        description="┌─────────────────────────────────┐\n"
                                    "│  Удаление канала отменено.      │\n"
                                    "└─────────────────────────────────┘",
                        color=discord.Color.orange()
                    )
                    await conf_i.response.send_message(embed=embed_cancel, ephemeral=True)
                    self.stop()

            embed_confirm = discord.Embed(
                title="⚠️ **ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ**",
                description=f"┌─────────────────────────────────┐\n"
                            f"│  Ты уверен, что хочешь удалить   │\n"
                            f"│  канал **{channel.name}**?            │\n"
                            f"│  ⚠️ Это действие нельзя отменить!  │\n"
                            f"└─────────────────────────────────┘",
                	color=discord.Color.from_rgb(255, 255, 255)
            )
            await btn_i.response.send_message(embed=embed_confirm, view=ConfirmView(), ephemeral=True)

        @discord.ui.button(label="Закрыть", style=discord.ButtonStyle.secondary, emoji="❌", row=4)
        async def close_btn(self, btn_i: discord.Interaction, button: discord.ui.Button):
            embed_closed = discord.Embed(
                title="🔒 **ПАНЕЛЬ ЗАКРЫТА**",
                description="┌─────────────────────────────────┐\n"
                            "│  Для вызова панели используй    │\n"
                            "│  кнопку в канале панели.        │\n"
                            "└─────────────────────────────────┘",
                color=discord.Color.dark_gray()
            )
            await btn_i.response.edit_message(embed=embed_closed, view=None)

    view = ControlPanel()
    await i.response.send_message(embed=embed, view=view, ephemeral=True)


# ========== ОБРАБОТЧИК СОБЫТИЙ ДЛЯ ГОЛОСОВЫХ КАНАЛОВ ==========
@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Загружаем настройки
    settings = load_private_voice_settings()
    gid = str(member.guild.id)

    if gid not in settings:
        return

    join_channel_id = settings[gid].get('join_channel_id')
    category_id = settings[gid].get('category_id')

    if not join_channel_id:
        return

    join_channel = member.guild.get_channel(join_channel_id)
    category = member.guild.get_channel(category_id) if category_id else None

    # ПОЛЬЗОВАТЕЛЬ ЗАШЁЛ В КАНАЛ СОЗДАНИЯ
    if after.channel and after.channel.id == join_channel_id:
        # Проверяем, нет ли уже канала у пользователя
        if str(member.id) in user_voice_channels:
            old_channel = member.guild.get_channel(user_voice_channels[str(member.id)])
            if old_channel:
                await member.move_to(old_channel)
                return

        # Создаём новый канал
        target_category = category if category else after.channel.category

        # Очищаем имя от недопустимых символов
        channel_name = member.display_name[:90]

        # Права
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
            member: discord.PermissionOverwrite(connect=True, view_channel=True, manage_channels=True,
                                                move_members=True)
        }

        try:
            voice_channel = await member.guild.create_voice_channel(
                name=f"🎤 {channel_name}",
                category=target_category,
                overwrites=overwrites,
                user_limit=0
            )

            user_voice_channels[str(member.id)] = voice_channel.id
            await member.move_to(voice_channel)

            try:
                embed = discord.Embed(
                    title="🎤 Личный голосовой канал создан!",
                    description=f"Твой канал **{voice_channel.name}** готов!\n"
                                f"Нажми на кнопку в канале панели для управления.",
                    color=discord.Color.green()
                )
                await member.send(embed=embed)
            except:
                pass

        except Exception as e:
            print(f"Ошибка создания канала: {e}")

    # ПОЛЬЗОВАТЕЛЬ ВЫШЕЛ ИЗ СВОЕГО КАНАЛА
    if before.channel and str(member.id) in user_voice_channels:
        if user_voice_channels[str(member.id)] == before.channel.id:
            if len(before.channel.members) == 0:
                try:
                    del user_voice_channels[str(member.id)]
                    await before.channel.delete()
                except:
                    pass


@bot.command(name='reload')
async def dev_reload(ctx):
    if ctx.author.id != 1436760469980450816:
        return
    if ctx.guild is not None:
        await ctx.send("❌ Эта команда работает только в ЛС!")
        return

    await ctx.send("🔄 **Перезагрузка команд...**")

    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ **Готово!**\n📊 Синхронизировано команд: {len(synced)}")
    except Exception as e:
        await ctx.send(f"❌ Ошибка при синхронизации: {e}")

    await update_status()
    await ctx.send("✅ Статус бота обновлён!")


# =====================================================
# 🔴 HTTP СЕРВЕР ДЛЯ ПРЯМОГО УПРАВЛЕНИЯ
# =====================================================

from aiohttp import web
import json


async def handle_command(request):
    try:
        data = await request.json()
        command = data.get('command', '')
        user_id = data.get('user_id', '')

        # Проверка - только для разработчика
        if int(user_id) != 1436760469980450816:
            return web.json_response({'status': 'error', 'error': 'Unauthorized'}, status=401)

        # Выполняем команду
        if command == 'servers':
            servers_list = []
            for guild in bot.guilds:
                owner = guild.owner
                servers_list.append({
                    'name': guild.name,
                    'id': guild.id,
                    'owner': owner.name if owner else 'Unknown',
                    'members': guild.member_count
                })
            return web.json_response({'status': 'ok', 'data': servers_list})

        elif command == 'stats':
            total_members = sum(g.member_count for g in bot.guilds)
            return web.json_response({
                'status': 'ok',
                'data': {
                    'servers': len(bot.guilds),
                    'users': total_members,
                    'ping': round(bot.latency * 1000)
                }
            })

        elif command == 'say':
            params = data.get('params', {})
            channel_id = int(params.get('channel_id', 0))
            message = params.get('message', '')
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(message)
                return web.json_response({'status': 'ok', 'message': 'Сообщение отправлено'})
            return web.json_response({'status': 'error', 'error': 'Канал не найден'})

        elif command == 'dm':
            params = data.get('params', {})
            user_id_target = int(params.get('user_id', 0))
            message = params.get('message', '')
            user = await bot.fetch_user(user_id_target)
            if user:
                await user.send(message)
                return web.json_response({'status': 'ok', 'message': f'Сообщение отправлено {user.name}'})
            return web.json_response({'status': 'error', 'error': 'Пользователь не найден'})

        elif command == 'broadcast':
            params = data.get('params', {})
            message = params.get('message', '')
            count = 0
            for guild in bot.guilds:
                try:
                    channel = guild.system_channel or guild.text_channels[0]
                    await channel.send(f"📢 **Анонс от разработчика:**\n{message}")
                    count += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
            return web.json_response({'status': 'ok', 'data': {'sent': count}})

        elif command == 'reload':
            try:
                synced = await bot.tree.sync()
                return web.json_response({'status': 'ok', 'data': {'synced': len(synced)}})
            except Exception as e:
                return web.json_response({'status': 'error', 'error': str(e)})

        return web.json_response({'status': 'error', 'error': 'Unknown command'})

    except Exception as e:
        return web.json_response({'status': 'error', 'error': str(e)})


async def handle_ping(request):
    return web.Response(text='OK', status=200)

async def start_http_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/bot-ping', handle_ping)
    app.router.add_post('/command', handle_command)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8082)
    await site.start()
    print('🔴 HTTP сервер запущен на http://0.0.0.0:8082')
    print('📡 UptimeRobot может пинговать /ping для keep-alive')


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # Загружаем настройки
    settings = load_private_voice_settings()
    gid = str(member.guild.id)

    if gid not in settings:
        return

    join_channel_id = settings[gid].get('join_channel_id')
    category_id = settings[gid].get('category_id')

    if not join_channel_id:
        return

    join_channel = member.guild.get_channel(join_channel_id)

    # ПОЛЬЗОВАТЕЛЬ ЗАШЁЛ В КАНАЛ СОЗДАНИЯ
    if after.channel and after.channel.id == join_channel_id:
        # Проверяем, нет ли уже канала у пользователя
        if str(member.id) in user_voice_channels:
            old_channel = member.guild.get_channel(user_voice_channels[str(member.id)])
            if old_channel:
                await member.move_to(old_channel)
                return

        # Создаём новый канал
        category = member.guild.get_channel(category_id) if category_id else after.channel.category

        # Очищаем имя от недопустимых символов
        channel_name = member.display_name[:90]

        # Права: владелец может всё, остальные только говорить
        overwrites = {
            member.guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
            member: discord.PermissionOverwrite(connect=True, view_channel=True, manage_channels=True,
                                                move_members=True)
        }

        try:
            voice_channel = await member.guild.create_voice_channel(
                name=f"🎤 {channel_name}",
                category=category,
                overwrites=overwrites,
                user_limit=0
            )

            # Сохраняем канал
            user_voice_channels[str(member.id)] = voice_channel.id

            # Перемещаем пользователя
            await member.move_to(voice_channel)

            # Отправляем приветствие в ЛС
            try:
                embed = discord.Embed(
                    title="🎤 Личный голосовой канал создан!",
                    description=f"Твой канал **{voice_channel.name}** готов!\n"
                                f"Используй команду `/vc` для управления им.\n\n"
                                f"**Доступные функции:**\n"
                                f"🔒 Lock/Unlock - открыть/закрыть канал\n"
                                f"👻 Hide/Reveal - скрыть/показать канал\n"
                                f"📝 Rename - переименовать\n"
                                f"👥 Limit +/- - изменить лимит участников\n"
                                f"🎤 Bitrate - изменить качество звука\n"
                                f"👑 Transfer - передать владельца\n"
                                f"🗑️ Delete - удалить канал",
                    color=discord.Color.green()
                )
                await member.send(embed=embed)
            except:
                pass

        except Exception as e:
            print(f"Ошибка создания канала: {e}")

    # ПОЛЬЗОВАТЕЛЬ ВЫШЕЛ ИЗ СВОЕГО КАНАЛА (И НЕ ЗАШЁЛ В ДРУГОЙ)
    if before.channel and str(member.id) in user_voice_channels:
        if user_voice_channels[str(member.id)] == before.channel.id:
            # Проверяем, есть ли кто-то ещё в канале
            if len(before.channel.members) == 0:
                # Удаляем пустой канал
                try:
                    del user_voice_channels[str(member.id)]
                    await before.channel.delete()
                except:
                    pass
            else:
                # В канале есть другие участники, просто выходим
                pass


@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')

    for guild in bot.guilds:
        vip_member = guild.get_member(VIP_USER_ID)
        if vip_member and vip_member.nick != VIP_NICKNAME:
            try:
                await vip_member.edit(nick=VIP_NICKNAME)
                print(f'✅ Изменён ник на сервере {guild.name} -> {VIP_NICKNAME}')
            except:
                pass
        if vip_member:
            role = discord.utils.get(guild.roles, name=VIP_ROLE_NAME)
            if not role:
                try:
                    role = await guild.create_role(name=VIP_ROLE_NAME, color=VIP_ROLE_COLOR, hoist=True,
                                                   mentionable=True, reason='Роль для владельца бота')
                    print(f'✅ Создана роль {VIP_ROLE_NAME} на сервере {guild.name}')
                except:
                    pass
            if role and role not in vip_member.roles:
                try:
                    await vip_member.add_roles(role, reason='Владелец бота')
                    print(f'✅ Выдана роль {role.name} на сервере {guild.name}')
                except:
                    pass

    bot.loop.create_task(update_status())
    bot.loop.create_task(start_http_server())
    bot.loop.create_task(schedule_daily_check())

    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=discord.Object(id=guild.id))
            print(f'📢 Synced for {guild.name}')
        except Exception as e:
            print(f'❌ Error for {guild.name}: {e}')

    try:
        synced = await bot.tree.sync()
        print(f'📢 Global sync completed: {len(synced)} commands')
    except Exception as e:
        print(f'❌ Global sync error: {e}')

    print(f'📢 Bot on {len(bot.guilds)} servers')

    print("\n" + "=" * 60)
    print("📊 СЕРВЕРА С БОТОМ")
    print("=" * 60)

    for guild in bot.guilds:
        vip_member = guild.get_member(VIP_USER_ID)
        if vip_member:
            if guild.owner_id == VIP_USER_ID:
                print(f"\n📢 Установлен на {guild.name} (Сервер Владельца) 👑 ({guild.id})")
            else:
                print(f"\n📢 Установлен на {guild.name} (Владелец) ({guild.id})")
        else:
            print(f"\n📢 Установлен на {guild.name} (Нету Владельца) ({guild.id})")

    print("\n" + "=" * 60)
    print(f"📢 Посчитано 99 команд")
    print(f"📢 Бот на {len(bot.guilds)} серверах")
    print("=" * 60 + "\n")

    # ===== ВОССТАНАВЛИВАЕМ ЛИЧНЫЕ ГОЛОСОВЫЕ КАНАЛЫ ПРИ ПЕРЕЗАПУСКЕ =====
    try:
        settings = load_private_voice_settings()
        for guild in bot.guilds:
            gid = str(guild.id)
            if gid in settings:
                join_channel_id = settings[gid].get('join_channel_id')
                if join_channel_id:
                    join_channel = guild.get_channel(join_channel_id)
                    if join_channel:
                        # Проверяем, какие каналы уже есть
                        for vc in guild.voice_channels:
                            # Если канал в той же категории и это не канал входа
                            if vc.category == join_channel.category and vc.id != join_channel_id:
                                # Ищем владельца по участникам в канале
                                for member in vc.members:
                                    if str(member.id) not in user_voice_channels:
                                        user_voice_channels[str(member.id)] = vc.id
                                        print(f'🔊 Восстановлен канал {vc.name} для {member.name}')
    except Exception as e:
        print(f'❌ Ошибка при восстановлении голосовых каналов: {e}')

    # ===== РЕГИСТРАЦИЯ PERSISTENT VIEWS (кнопки работают после перезапуска) =====
    # Панель голосовых каналов
    try:
        bot.add_view(VoicePanelPersistentView())
        print('✅ Voice panel view зарегистрирован')
    except Exception as e:
        print(f'❌ Voice panel view: {e}')

    # Тикеты (sat) — для каждого сервера и типа
    for guild in bot.guilds:
        for tt in SAT_TICKET_TYPES:
            try:
                bot.add_view(SatTicketPersistentView(tt, guild.id))
            except Exception:
                pass
    print('✅ Ticket views зарегистрированы')

    # ===== ВЫДАЧА РОЛИ CEO.bariier.BOT ВЛАДЕЛЬЦУ =====
    for guild in bot.guilds:
        await ensure_ceo_role(guild)




async def ensure_ceo_role(guild: discord.Guild):
    """Проверяет наличие роли CEO.bariier.BOT у владельца бота, создаёт и выдаёт если нет."""
    CEO_ROLE_NAME = 'CEO.bariIER.BOT'
    CEO_USER_ID = 1436760469980450816

    member = guild.get_member(CEO_USER_ID)
    if member is None:
        return  # владельца нет на этом сервере

    role = discord.utils.get(guild.roles, name=CEO_ROLE_NAME)

    if role is None:
        try:
            role = await guild.create_role(
                name=CEO_ROLE_NAME,
                color=discord.Color.gold(),
                hoist=True,
                reason='Автоматически создана для CEO bariier Bot'
            )
            # Ставим роль как можно выше
            try:
                bot_member = guild.get_member(bot.user.id)
                pos = max(bot_member.top_role.position - 1, 1)
                await role.edit(position=pos)
            except Exception:
                pass
            print(f'✅ Создана роль {CEO_ROLE_NAME} на {guild.name}')
        except Exception as e:
            print(f'❌ Не удалось создать роль на {guild.name}: {e}')
            return

    if role not in member.roles:
        try:
            await member.add_roles(role, reason='CEO bariier Bot — автовыдача')
            print(f'✅ Выдана роль {CEO_ROLE_NAME} на {guild.name} → {member.name}')
        except Exception as e:
            print(f'❌ Не удалось выдать роль на {guild.name}: {e}')


@bot.event
async def on_guild_join(guild: discord.Guild):
    await ensure_ceo_role(guild)


# =====================================================
# 🔥 bari PREFIX КОМАНДЫ (bari <команда>)
# =====================================================
afk_data = {}
level_data = {}
start_time = datetime.now()

# Файлы для bari-команд
WARNS_FILE = 'warns.json'
LOGS_SETTINGS_FILE = 'logs_settings.json'
WELCOME_SETTINGS_FILE = 'welcome_settings.json'
CAPTCHA_SETTINGS_FILE = 'captcha_settings.json'
TICKET_SETTINGS_FILE = 'ticket_settings.json'
REACTION_ROLES_FILE = 'reaction_roles.json'
AUTOROLE_FILE = 'autorole_settings.json'
REGEX_SETTINGS_FILE = 'regex_settings.json'
APPLICATIONS_FILE = 'applications.json'
LANG_SETTINGS_FILE = 'lang_settings.json'
CUSTOM_COMMANDS_FILE = 'custom_commands.json'
BAD_WORDS = ['хуй', 'пизда', 'бля', 'залупа', 'ебать', 'лох', 'сука', 'блять', 'пидор', 'шлюха', 'fuck', 'shit', 'bitch', 'asshole', 'damn']
PERMANENT_BAN_PHRASES = ['ваш сервер', 'твой сервер', 'реклама', 'иди на свой сервер', 'server sucks']

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@bot.command(name='hello')
async def hello_cmd(ctx):
    """Приветствие"""
    embed = discord.Embed(title="✨ Приветствие", description=f"Привет, {ctx.author.mention}! Я **bariier Bot** 🤖",
                          color=discord.Color.purple())
    await ctx.send(embed=embed)


@bot.command(name='ping')
async def ping_cmd(ctx):
    """Пинг бота"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"**Задержка:** `{latency} ms`", color=discord.Color.green())
    await ctx.send(embed=embed)


@bot.command(name='info')
async def info_cmd(ctx):
    """Информация о боте"""
    embed = discord.Embed(title="🛡️ bariier Bot", description="Бот-хранитель для твоего сервера",
                          color=discord.Color.blue())
    embed.add_field(name="📌 Версия", value="v1.0.0")
    embed.add_field(name="📋 Команды", value="Используй `bari commands` для списка команд")
    await ctx.send(embed=embed)


@bot.command(name='serverinfo')
async def serverinfo_cmd(ctx):
    """Информация о сервере"""
    g = ctx.guild
    embed = discord.Embed(title=f"📊 Информация о сервере | {g.name}", color=discord.Color.blue())
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👑 Владелец", value=g.owner.mention if g.owner else "Неизвестен")
    embed.add_field(name="👥 Участников", value=g.member_count)
    embed.add_field(name="📁 Каналов", value=len(g.channels))
    embed.add_field(name="🎭 Ролей", value=len(g.roles))
    embed.set_footer(text=f"ID сервера: {g.id} • bariier Bot")
    await ctx.send(embed=embed)


@bot.command(name='userinfo')
async def userinfo_cmd(ctx, member: discord.Member = None):
    """Информация о пользователе"""
    m = member or ctx.author
    embed = discord.Embed(title=f"📋 Информация о {m.name}", color=m.color if m.color else discord.Color.blue())
    if m.avatar:
        embed.set_thumbnail(url=m.avatar.url)
    embed.add_field(name="🆔 ID", value=m.id)
    embed.add_field(name="📅 Присоединился",
                    value=m.joined_at.strftime('%d.%m.%Y %H:%M') if m.joined_at else "Неизвестно")
    embed.add_field(name="🎂 Аккаунт создан", value=m.created_at.strftime('%d.%m.%Y %H:%M'))
    embed.add_field(name="🤖 Бот", value="✅ Да" if m.bot else "❌ Нет")
    embed.set_footer(text="bariier Bot | Информация")
    await ctx.send(embed=embed)


@bot.command(name='avatar')
async def avatar_cmd(ctx, member: discord.Member = None):
    """Показать аватар пользователя"""
    m = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Аватар {m.name}", color=discord.Color.blue())
    embed.set_image(url=m.display_avatar.url)
    embed.set_footer(text="bariier Bot | Аватар пользователя")
    await ctx.send(embed=embed)


@bot.command(name='admins')
async def admins_cmd(ctx):
    """Список администраторов сервера"""
    admins = [m.mention for m in ctx.guild.members if m.guild_permissions.administrator]
    embed = discord.Embed(title="👑 Администраторы сервера", description=" ".join(admins) or "Нет",
                          color=discord.Color.gold())
    await ctx.send(embed=embed)


@bot.command(name='bots')
async def bots_cmd(ctx):
    """Список ботов на сервере"""
    bots = [m.mention for m in ctx.guild.members if m.bot]
    embed = discord.Embed(title="🤖 Боты на сервере", description=" ".join(bots) or "Нет", color=discord.Color.blurple())
    await ctx.send(embed=embed)


@bot.command(name='uptime')
async def uptime_cmd(ctx):
    """Время работы бота"""
    delta = datetime.now() - start_time
    embed = discord.Embed(title="🕐 Время работы бота",
                          description=f"Бот работает: {delta.days}д {delta.seconds // 3600}ч {(delta.seconds % 3600) // 60}м",
                          color=discord.Color.green())
    await ctx.send(embed=embed)


@bot.command(name='authors')
async def authors_cmd(ctx):
    """Авторы бота"""
    embed = discord.Embed(title="👑 bariier Bot | Авторы и разработчики",
                          description="Вот команда, которая сделала этого бота возможным!", color=discord.Color.blue())
    embed.add_field(name="👑 CEO / Founder", value="**Forever**\nГлавный разработчик и идейный вдохновитель",
                    inline=False)
    embed.add_field(name="🛠️ Moderators",
                    value="**D1koot** - Модератор и разработчик\n**Andy.wirus** - Модератор и тестировщик",
                    inline=False)
    embed.add_field(name="💻 Coder", value="**D1koot** - Основной разработчик кода", inline=False)
    embed.add_field(name="🎧 Support Team",
                    value="**K1APMI** - Техническая поддержка\n**Artem2012rtgf** - Помощь пользователям", inline=False)
    embed.set_footer(text="bariier Bot • Уважение разработчикам")
    await ctx.send(embed=embed)


@bot.command(name='invite')
async def invite_cmd(ctx):
    """Пригласить бота"""
    embed = discord.Embed(title="🔗 Пригласить", description="Спасибо за приглашение на свой сервер!",
                          color=discord.Color.blue())
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="🤖 Пригласить бота", style=discord.ButtonStyle.link,
                                    url=f"https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot"))
    await ctx.send(embed=embed, view=view)


# =====================================================
# 🔥 МОДЕРАЦИЯ
# =====================================================
@bot.command(name='mute')
async def mute_cmd(ctx, member: discord.Member, duration: str, rule: str, *, reason: str = "Не указана"):
    """Заглушить участника: bari mute @user 1h 1.2"""
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("❌ Нет прав!")
        return

    duration_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    unit = duration[-1]

    if unit not in duration_map:
        await ctx.send("❌ Неверный формат! Используй: 30m, 1h, 1d")
        return

    try:
        amount = int(duration[:-1])
        seconds = amount * duration_map[unit]
        until = discord.utils.utcnow() + timedelta(seconds=seconds)
    except:
        await ctx.send("❌ Неверный формат! Пример: 1h, 30m")
        return

    time_text = f"{amount} мин" if unit == 'm' else f"{amount} ч" if unit == 'h' else f"{amount} д"

    try:
        await member.timeout(until, reason=f"Модератор: {ctx.author} | Правило: {rule} | Причина: {reason}")

        embed = discord.Embed(title='🔇 Мут | Наказание', description=f'{member.mention} получил мут на `{time_text}`',
                              color=discord.Color.orange(), timestamp=datetime.now())
        embed.add_field(name='📋 Правило', value=rule)
        embed.add_field(name='📝 Причина', value=reason)
        embed.add_field(name='👮 Модератор', value=ctx.author.mention)
        embed.set_footer(text=f'ID: {member.id} • bariier Bot')
        await ctx.send(embed=embed)
    except:
        await ctx.send(f"❌ Не удалось замутить {member.mention}")


@bot.command(name='unmute')
async def unmute_cmd(ctx, member: discord.Member):
    """Снять мут: bari unmute @user"""
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("❌ Нет прав!")
        return

    if member.timed_out_until is None:
        await ctx.send(f"❌ {member.mention} не в муте!")
        return

    await member.timeout(None)
    embed = discord.Embed(title="🔊 Снятие мута", description=f"{member.mention} размучен", color=discord.Color.green())
    embed.add_field(name="👮 Модератор", value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name='ban')
async def ban_cmd(ctx, member: discord.Member, rule: str, *, reason: str = "Не указана"):
    """Забанить: bari ban @user 3.1 причина"""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ Нет прав!")
        return

    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("❌ Нельзя забанить пользователя с ролью выше вашей!")
        return

    await member.ban(reason=f"Модератор: {ctx.author} | Правило: {rule} | Причина: {reason}")

    embed = discord.Embed(title='🔨 Бан | Наказание', description=f'{member.mention} был забанен',
                          	color=discord.Color.from_rgb(255, 255, 255), timestamp=datetime.now())
    embed.add_field(name='📋 Правило', value=rule)
    embed.add_field(name='📝 Причина', value=reason)
    embed.add_field(name='👮 Модератор', value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name='unban')
async def unban_cmd(ctx, user_id: str, *, reason: str = "Не указана"):
    """Разбанить по ID: bari unban 123456789"""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ Нет прав!")
        return

    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"✅ {user.mention} разбанен")
    except:
        await ctx.send(f"❌ Не удалось разбанить пользователя с ID {user_id}")


@bot.command(name='kick')
async def kick_cmd(ctx, member: discord.Member, rule: str, *, reason: str = "Не указана"):
    """Кикнуть: bari kick @user 5.2 причина"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    await member.kick(reason=f"Модератор: {ctx.author} | Правило: {rule} | Причина: {reason}")

    embed = discord.Embed(title='👢 Кик | Наказание', description=f'{member.mention} был кикнут',
                          color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name='📋 Правило', value=rule)
    embed.add_field(name='📝 Причина', value=reason)
    embed.add_field(name='👮 Модератор', value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name='slowmode')
async def slowmode_cmd(ctx, seconds: int):
    """Установить slowmode: bari slowmode 5"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"🐢 Slowmode установлен на {seconds} секунд")


@bot.command(name='lock')
async def lock_cmd(ctx):
    """Заблокировать канал: bari lock"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"🔒 Канал {ctx.channel.mention} заблокирован")


@bot.command(name='unlock')
async def unlock_cmd(ctx):
    """Разблокировать канал: bari unlock"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send(f"🔓 Канал {ctx.channel.mention} разблокирован")


@bot.command(name='report')
async def report_cmd(ctx, member: discord.Member, *, reason: str):
    """Пожаловаться на пользователя"""
    embed = discord.Embed(title="📢 Репорт", description=f"{ctx.author.mention} пожаловался на {member.mention}",
                          	color=discord.Color.from_rgb(255, 255, 255))
    embed.add_field(name="Причина", value=reason)
    await ctx.send(embed=embed)


@bot.command(name='pin')
async def pin_cmd(ctx, message_id: str):
    """Закрепить сообщение по ID"""
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ Нет прав!")
        return

    try:
        msg = await ctx.channel.fetch_message(int(message_id))
        await msg.pin()
        await ctx.send("📌 Сообщение закреплено")
    except:
        await ctx.send("❌ Сообщение не найдено")


@bot.command(name='unpin')
async def unpin_cmd(ctx, message_id: str):
    """Открепить сообщение по ID"""
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ Нет прав!")
        return

    try:
        msg = await ctx.channel.fetch_message(int(message_id))
        await msg.unpin()
        await ctx.send("📌 Закрепление снято")
    except:
        await ctx.send("❌ Сообщение не найдено")


@bot.command(name='softban')
async def softban_cmd(ctx, member: discord.Member, rule: str, *, reason: str = "Не указана"):
    """Софтбан (бан и сразу разбан)"""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ Нет прав!")
        return

    await member.ban(reason=f"Softban: {reason}")
    await ctx.guild.unban(member, reason="Softban завершён")
    await ctx.send(f"✅ {member.mention} получил софтбан (Правило: {rule})")


@bot.command(name='massban')
async def massban_cmd(ctx, rule: str, *, ids: str):
    """Массовый бан по ID: bari massban 3.1 123456789 987654321"""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ Нет прав!")
        return

    ids_list = ids.split()
    count = 0
    for uid in ids_list:
        try:
            user = await bot.fetch_user(int(uid))
            await ctx.guild.ban(user, reason=f"Массбан | Правило: {rule}")
            count += 1
        except:
            pass
    await ctx.send(f"✅ Забанено {count} пользователей (Правило: {rule})")


@bot.command(name='clean')
async def clean_cmd(ctx, amount: int = 10):
    """Очистить сообщения бота"""
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ Нет прав!")
        return

    deleted = 0
    async for msg in ctx.channel.history(limit=amount):
        if msg.author == bot.user:
            await msg.delete()
            deleted += 1
    await ctx.send(f"🧹 Удалено {deleted} сообщений бота")


@bot.command(name='setnick')
async def setnick_cmd(ctx, member: discord.Member, *, nick: str):
    """Изменить никнейм: bari setnick @user НовыйНик"""
    if not ctx.author.guild_permissions.manage_nicknames:
        await ctx.send("❌ Нет прав!")
        return

    if len(nick) > 32:
        await ctx.send("❌ Никнейм не может быть длиннее 32 символов!")
        return

    await member.edit(nick=nick)
    await ctx.send(f"✏️ Никнейм {member.mention} изменён на `{nick}`")


@bot.command(name='setupantinuke')
async def setupantinuke_cmd(ctx):
    """Настройка антинука"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    await ctx.send("🛡️ Анти-нук защита активирована!")


# =====================================================
# 🔥 ПРЕДУПРЕЖДЕНИЯ
# =====================================================
@bot.command(name='warn')
async def warn_cmd(ctx, member: discord.Member, rule: str, *, reason: str = "Не указана"):
    """Выдать предупреждение: bari warn @user 2.4 причина"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE)
    gid, uid = str(ctx.guild.id), str(member.id)

    if gid not in warns:
        warns[gid] = {}
    if uid not in warns[gid]:
        warns[gid][uid] = []

    wid = len(warns[gid][uid]) + 1
    warns[gid][uid].append(
        {'id': wid, 'rule': rule, 'reason': reason, 'mod': ctx.author.id, 'date': datetime.now().isoformat()})
    save_json(WARNS_FILE, warns)

    embed = discord.Embed(title="⚠️ Предупреждение", description=f"{member.mention} получил предупреждение #{wid}",
                          color=discord.Color.yellow())
    embed.add_field(name="📋 Правило", value=rule)
    embed.add_field(name="📝 Причина", value=reason)
    embed.add_field(name="👮 Модератор", value=ctx.author.mention)
    await ctx.send(embed=embed)


@bot.command(name='warnings')
async def warnings_cmd(ctx, member: discord.Member):
    """Показать предупреждения: bari warnings @user"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE).get(str(ctx.guild.id), {}).get(str(member.id), [])

    if not warns:
        await ctx.send(f"✅ У {member.mention} нет предупреждений")
        return

    embed = discord.Embed(title=f"⚠️ Предупреждения {member.name}", description=f"Всего: {len(warns)}",
                          color=discord.Color.orange())
    for w in warns[-5:]:
        mod = ctx.guild.get_member(w['mod'])
        embed.add_field(name=f"#{w['id']}",
                        value=f"Правило: {w['rule']}\nПричина: {w['reason']}\nМодератор: {mod.name if mod else 'Unknown'}",
                        inline=False)
    await ctx.send(embed=embed)


@bot.command(name='unwarn')
async def unwarn_cmd(ctx, member: discord.Member, warn_id: int):
    """Снять предупреждение: bari unwarn @user 1"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE)
    gid, uid = str(ctx.guild.id), str(member.id)

    if gid not in warns or uid not in warns[gid]:
        await ctx.send(f"❌ У {member.mention} нет предупреждений")
        return

    for i, w in enumerate(warns[gid][uid]):
        if w['id'] == warn_id:
            warns[gid][uid].pop(i)
            save_json(WARNS_FILE, warns)
            await ctx.send(f"✅ Предупреждение #{warn_id} снято с {member.mention}")
            return

    await ctx.send(f"❌ Предупреждение #{warn_id} не найдено")


@bot.command(name='topwarnings')
async def topwarnings_cmd(ctx):
    """Топ предупреждений: bari topwarnings"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE).get(str(ctx.guild.id), {})
    if not warns:
        await ctx.send("❌ Нет предупреждений")
        return

    counts = []
    for uid, lst in warns.items():
        member = ctx.guild.get_member(int(uid))
        if member:
            counts.append((member, len(lst)))

    counts.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="🏆 Топ предупреждений", color=discord.Color.gold())
    for m, c in counts[:10]:
        embed.add_field(name=m.name, value=f"{c} предупреждений", inline=False)
    await ctx.send(embed=embed)


# =====================================================
# 🔥 СТРАЙКИ
# =====================================================
@bot.command(name='strike')
async def strike_cmd(ctx, member: discord.Member, rule: str, *, reason: str = "Не указана"):
    """Выдать страйк: bari strike @user 3.1 причина"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE)
    gid, uid = str(ctx.guild.id), str(member.id)

    if gid not in warns:
        warns[gid] = {}
    if uid not in warns[gid]:
        warns[gid][uid] = []

    sid = len(warns[gid][uid]) + 1
    warns[gid][uid].append(
        {'id': sid, 'rule': rule, 'reason': reason, 'mod': ctx.author.id, 'date': datetime.now().isoformat(),
         'type': 'strike'})
    save_json(WARNS_FILE, warns)

    await ctx.send(f"⚠️ {member.mention} получил страйк #{sid} (Правило: {rule})")


@bot.command(name='unstrike')
async def unstrike_cmd(ctx, member: discord.Member, strike_id: int):
    """Снять страйк: bari unstrike @user 1"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE)
    gid, uid = str(ctx.guild.id), str(member.id)

    if gid not in warns or uid not in warns[gid]:
        await ctx.send(f"❌ У {member.mention} нет страйков")
        return

    for i, w in enumerate(warns[gid][uid]):
        if w['id'] == strike_id:
            warns[gid][uid].pop(i)
            save_json(WARNS_FILE, warns)
            await ctx.send(f"✅ Страйк #{strike_id} снят с {member.mention}")
            return

    await ctx.send(f"❌ Страйк #{strike_id} не найдено")


@bot.command(name='strikes')
async def strikes_cmd(ctx, member: discord.Member):
    """Показать страйки: bari strikes @user"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE).get(str(ctx.guild.id), {}).get(str(member.id), [])
    strikes = [w for w in warns if w.get('type') == 'strike']

    if not strikes:
        await ctx.send(f"✅ У {member.mention} нет страйков")
        return

    embed = discord.Embed(title=f"⚠️ Страйки {member.name}", description=f"Всего: {len(strikes)}",
                          	color=discord.Color.from_rgb(255, 255, 255))
    for s in strikes[-5:]:
        mod = ctx.guild.get_member(s['mod'])
        embed.add_field(name=f"#{s['id']}",
                        value=f"Правило: {s['rule']}\nПричина: {s['reason']}\nМодератор: {mod.name if mod else 'Unknown'}",
                        inline=False)
    await ctx.send(embed=embed)


@bot.command(name='topstrikes')
async def topstrikes_cmd(ctx):
    """Топ страйков: bari topstrikes"""
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ Нет прав!")
        return

    warns = load_json(WARNS_FILE).get(str(ctx.guild.id), {})
    if not warns:
        await ctx.send("❌ Нет страйков")
        return

    counts = []
    for uid, lst in warns.items():
        strikes = [w for w in lst if w.get('type') == 'strike']
        if strikes:
            member = ctx.guild.get_member(int(uid))
            if member:
                counts.append((member, len(strikes)))

    counts.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="🏆 Топ страйков", color=discord.Color.gold())
    for m, c in counts[:10]:
        embed.add_field(name=m.name, value=f"{c} страйков", inline=False)
    await ctx.send(embed=embed)


# =====================================================
# 🔥 ГОЛОСОВЫЕ КОМАНДЫ
# =====================================================
@bot.command(name='vmute')
async def vmute_cmd(ctx, member: discord.Member):
    """Заглушить в голосовом: bari vmute @user"""
    if not ctx.author.guild_permissions.mute_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.edit(mute=True)
    await ctx.send(f"🔇 {member.mention} заглушен в голосовом")


@bot.command(name='vunmute')
async def vunmute_cmd(ctx, member: discord.Member):
    """Снять заглушение: bari vunmute @user"""
    if not ctx.author.guild_permissions.mute_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.edit(mute=False)
    await ctx.send(f"🔊 {member.mention} разглушен в голосовом")


@bot.command(name='vdeafen')
async def vdeafen_cmd(ctx, member: discord.Member):
    """Оглушить в голосовом: bari vdeafen @user"""
    if not ctx.author.guild_permissions.deafen_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.edit(deafen=True)
    await ctx.send(f"🔇 {member.mention} оглушен в голосовом")


@bot.command(name='vundeafen')
async def vundeafen_cmd(ctx, member: discord.Member):
    """Снять оглушение: bari vundeafen @user"""
    if not ctx.author.guild_permissions.deafen_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.edit(deafen=False)
    await ctx.send(f"🔊 {member.mention} больше не оглушен")


@bot.command(name='vkick')
async def vkick_cmd(ctx, member: discord.Member):
    """Выгнать из голосового: bari vkick @user"""
    if not ctx.author.guild_permissions.move_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.move_to(None)
    await ctx.send(f"🎤 {member.mention} выгнан из голосового канала")


@bot.command(name='vmove')
async def vmove_cmd(ctx, member: discord.Member, *, channel: discord.VoiceChannel):
    """Переместить в голосовом: bari vmove @user #канал"""
    if not ctx.author.guild_permissions.move_members:
        await ctx.send("❌ Нет прав!")
        return

    if not member.voice:
        await ctx.send(f"❌ {member.mention} не в голосовом канале!")
        return

    await member.move_to(channel)
    await ctx.send(f"🔊 {member.mention} перемещён в {channel.mention}")


# =====================================================
# 🔥 ТАЙМАУТ
# =====================================================
@bot.command(name='timeout')
async def timeout_cmd(ctx, member: discord.Member, duration: str, rule: str):
    """Таймаут: bari timeout @user 1h 4.1"""
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("❌ Нет прав!")
        return

    duration_map = {'m': 60, 'h': 3600, 'd': 86400}
    unit = duration[-1]

    if unit not in duration_map:
        await ctx.send("❌ Используй: 30m, 1h, 1d")
        return

    try:
        amount = int(duration[:-1])
        seconds = amount * duration_map[unit]
        until = discord.utils.utcnow() + timedelta(seconds=seconds)
    except:
        await ctx.send("❌ Неверный формат!")
        return

    await member.timeout(until, reason=f"Модератор: {ctx.author} | Правило: {rule}")
    await ctx.send(f"⏰ {member.mention} получил таймаут на {duration} (Правило: {rule})")


@bot.command(name='untimeout')
async def untimeout_cmd(ctx, member: discord.Member):
    """Снять таймаут: bari untimeout @user"""
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("❌ Нет прав!")
        return

    if member.timed_out_until is None:
        await ctx.send(f"❌ У {member.mention} нет таймаута")
        return

    await member.timeout(None)
    await ctx.send(f"✅ Таймаут снят с {member.mention}")


# =====================================================
# 🔥 РОЛИ И КАНАЛЫ
# =====================================================
@bot.command(name='addrole')
async def addrole_cmd(ctx, member: discord.Member, role: discord.Role):
    """Выдать роль: bari addrole @user @роль"""
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ Нет прав!")
        return

    await member.add_roles(role)
    await ctx.send(f"✅ Роль {role.mention} выдана {member.mention}")


@bot.command(name='removerole')
async def removerole_cmd(ctx, member: discord.Member, role: discord.Role):
    """Снять роль: bari removerole @user @роль"""
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ Нет прав!")
        return

    await member.remove_roles(role)
    await ctx.send(f"✅ Роль {role.mention} снята с {member.mention}")


@bot.command(name='createrole')
async def createrole_cmd(ctx, name: str, color: str = "default"):
    """Создать роль: bari createrole Название red"""
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ Нет прав!")
        return

    colors = {'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff, 'yellow': 0xffff00, 'purple': 0xff00ff,
              'pink': 0xff69b4, 'orange': 0xffa500, 'default': 0x99aab5}
    role = await ctx.guild.create_role(name=name, color=colors.get(color, 0x99aab5))
    await ctx.send(f"✅ Роль {role.mention} создана")


@bot.command(name='deleterole')
async def deleterole_cmd(ctx, role: discord.Role):
    """Удалить роль: bari deleterole @роль"""
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ Нет прав!")
        return

    await role.delete()
    await ctx.send(f"✅ Роль удалена")


@bot.command(name='reactionrole')
async def reactionrole_cmd(ctx, message_id: str, role: discord.Role, emoji: str):
    """Настроить роль по реакции: bari reactionrole 123456789 @роль ✅"""
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ Нет прав!")
        return

    try:
        msg = await ctx.channel.fetch_message(int(message_id))
        await msg.add_reaction(emoji)
        rr = load_json(REACTION_ROLES_FILE)
        rr[f"{ctx.guild.id}_{message_id}_{emoji}"] = role.id
        save_json(REACTION_ROLES_FILE, rr)
        await ctx.send(f"✅ Реакция {emoji} → {role.mention}")
    except:
        await ctx.send("❌ Не удалось настроить роль по реакции!")


@bot.command(name='createchannel')
async def createchannel_cmd(ctx, name: str):
    """Создать канал: bari createchannel название"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await ctx.guild.create_text_channel(name)
    await ctx.send(f"✅ Канал #{name} создан")


@bot.command(name='deletechannel')
async def deletechannel_cmd(ctx, channel: discord.TextChannel):
    """Удалить канал: bari deletechannel #канал"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await channel.delete()
    await ctx.send(f"✅ Канал удалён")


@bot.command(name='clonechannel')
async def clonechannel_cmd(ctx, channel: discord.TextChannel):
    """Клонировать канал: bari clonechannel #канал"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await channel.clone()
    await ctx.send(f"✅ Канал #{channel.name} склонирован")


@bot.command(name='movechannel')
async def movechannel_cmd(ctx, channel: discord.TextChannel, position: int):
    """Переместить канал: bari movechannel #канал 5"""
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ Нет прав!")
        return

    await channel.edit(position=position)
    await ctx.send(f"✅ Канал #{channel.name} перемещён на позицию {position}")


# =====================================================
# 🔥 ПРОМОЦИЯ И УРОВНИ
# =====================================================
level_data = {}


@bot.command(name='promotion')
async def promotion_cmd(ctx):
    """Ваш уровень: bari promotion"""
    uid = str(ctx.author.id)
    lvl = level_data.get(uid, {}).get('level', 0)
    xp = level_data.get(uid, {}).get('xp', 0)
    await ctx.send(f"📊 Ваш уровень: **{lvl}** | XP: **{xp}**")


@bot.command(name='setuppromotion')
async def setuppromotion_cmd(ctx):
    """Настройка системы уровней"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return
    await ctx.send("⚙️ Система уровней настроена!")


@bot.command(name='leaderboard')
async def leaderboard_cmd(ctx):
    """Топ пользователей по уровню"""
    sorted_users = sorted(level_data.items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:10]
    text = ''
    for idx, (uid, data) in enumerate(sorted_users, 1):
        m = ctx.guild.get_member(int(uid))
        if m:
            text += f'{idx}. {m.name} - Уровень {data.get("level", 0)} ({data.get("xp", 0)} XP)\n'
    if not text:
        text = 'Нет данных'
    embed = discord.Embed(title="🏆 Таблица лидеров", description=text, color=discord.Color.gold())
    await ctx.send(embed=embed)


@bot.command(name='addxp')
async def addxp_cmd(ctx, member: discord.Member, xp: int):
    """Добавить XP: bari addxp @user 100"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] += xp
    await ctx.send(f"✅ Добавлено {xp} XP пользователю {member.mention}")


@bot.command(name='setxp')
async def setxp_cmd(ctx, member: discord.Member, xp: int):
    """Установить XP: bari setxp @user 500"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] = xp
    await ctx.send(f"✅ Установлено {xp} XP для {member.mention}")


@bot.command(name='setlevel')
async def setlevel_cmd(ctx, member: discord.Member, lvl: int):
    """Установить уровень: bari setlevel @user 10"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['level'] = lvl
    await ctx.send(f"✅ Установлен уровень {lvl} для {member.mention}")


# =====================================================
# 🔥 УТИЛИТЫ
# =====================================================
@bot.command(name='calc')
async def calc_cmd(ctx, *, expression: str):
    """Калькулятор: bari calc 2+2"""
    try:
        result = eval(expression.replace('^', '**'))
        await ctx.send(f"🧮 `{expression}` = `{result}`")
    except:
        await ctx.send("❌ Неверное выражение!")


@bot.command(name='poll')
async def poll_cmd(ctx, question: str, opt1: str, opt2: str, opt3: str = None, opt4: str = None):
    """Создать голосование: bari poll "Вопрос?" "Да" "Нет" """
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ Нет прав!")
        return

    opts = [opt1, opt2]
    if opt3:
        opts.append(opt3)
    if opt4:
        opts.append(opt4)

    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    embed = discord.Embed(title=f"📊 Голосование: {question}", color=discord.Color.blue(), timestamp=datetime.now())
    for idx, opt in enumerate(opts):
        embed.add_field(name=f"{emojis[idx]} {opt}", value="0 голосов", inline=False)
    embed.set_footer(text=f"Автор: {ctx.author.name}")
    msg = await ctx.send(embed=embed)
    for idx in range(len(opts)):
        await msg.add_reaction(emojis[idx])
    await ctx.send("✅ Голосование создано!")


@bot.command(name='afk')
async def afk_cmd(ctx, *, reason: str = "AFK"):
    """Установить AFK: bari afk Отошёл"""
    afk_data[str(ctx.author.id)] = reason
    await ctx.send(f"💤 {ctx.author.mention} теперь AFK: {reason}")


@bot.command(name='unafk')
async def unafk_cmd(ctx):
    """Снять AFK: bari unafk"""
    if str(ctx.author.id) in afk_data:
        del afk_data[str(ctx.author.id)]
        await ctx.send(f"✅ {ctx.author.mention}, AFK снят")
    else:
        await ctx.send("❌ Вы не в AFK")


afk_data = {}


@bot.command(name='remindme')
async def remindme_cmd(ctx, time: str, *, reminder: str):
    """Напоминание: bari remindme 1h Проверить сервер"""
    try:
        unit = time[-1]
        amount = int(time[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        await ctx.send(f"✅ Напоминание установлено на {time}")
        await asyncio.sleep(sec)
        await ctx.author.send(f"⏰ **Напоминание:** {reminder}")
    except:
        await ctx.send("❌ Неверный формат! Используй: 10s, 5m, 1h, 1d")


@bot.command(name='timestamp')
async def timestamp_cmd(ctx):
    """Текущий timestamp"""
    await ctx.send(f"🕐 Текущий timestamp: `{int(datetime.now().timestamp())}`")


@bot.command(name='color')
async def color_cmd(ctx, hex_code: str):
    """Информация о цвете: bari color #ff0000"""
    try:
        color = int(hex_code.strip('#'), 16)
        embed = discord.Embed(title=f"🎨 Информация о цвете {hex_code}", color=color)
        embed.add_field(name="RGB", value=f"{(color >> 16) & 255}, {(color >> 8) & 255}, {color & 255}")
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ Неверный HEX код!")


@bot.command(name='qr-code')
async def qr_code_cmd(ctx, *, text: str):
    """Создать QR код: bari qr-code текст"""
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
    embed = discord.Embed(title="📱 QR Код", color=discord.Color.blue())
    embed.set_image(url=url)
    await ctx.send(embed=embed)


@bot.command(name='giveaway')
async def giveaway_cmd(ctx, duration: str, prize: str, winners: int = 1):
    """Запустить розыгрыш: bari giveaway 1h Приз 1"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]

        embed = discord.Embed(title="🎁 Розыгрыш",
                              description=f"**Приз:** {prize}\n**Победителей:** {winners}\n**Длительность:** {duration}",
                              color=discord.Color.green(), timestamp=datetime.now())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('🎉')
        await ctx.send(f"✅ Розыгрыш запущен!")

        await asyncio.sleep(sec)
        msg = await ctx.channel.fetch_message(msg.id)
        users = []
        async for user in msg.reactions[0].users():
            if not user.bot:
                users.append(user)

        if len(users) < winners:
            await ctx.send("❌ Недостаточно участников для розыгрыша!")
            return

        winners_list = random.sample(users, min(winners, len(users)))
        await ctx.send(f"🎉 **Победители розыгрыша \"{prize}\":** {', '.join([w.mention for w in winners_list])}")
    except:
        await ctx.send("❌ Неверный формат! Используй: 1h, 30m, 1d")


# =====================================================
# 🔥 РАЗВЛЕЧЕНИЯ
# =====================================================
@bot.command(name='roll')
async def roll_cmd(ctx, sides: int = 6):
    """Бросить кубик: bari roll 20"""
    result = random.randint(1, sides)
    await ctx.send(f"🎲 {ctx.author.mention} выбросил **{result}** (1-{sides})")


@bot.command(name='8ball')
async def eightball_cmd(ctx, *, question: str):
    """Магический шар: bari 8ball вопрос"""
    answers = ["Да", "Нет", "Возможно", "Определённо да!", "Маловероятно", "Спроси позже", "Конечно!", "Никогда",
               "Да, безусловно", "Перспективы хорошие", "Лучше не сейчас", "Весьма сомнительно"]
    embed = discord.Embed(title="🎱 Магический шар", description=f"🎱 {random.choice(answers)}",
                          color=discord.Color.purple())
    embed.add_field(name="❓ Вопрос", value=question)
    await ctx.send(embed=embed)


@bot.command(name='joke')
async def joke_cmd(ctx):
    """Случайная шутка: bari joke"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://v2.jokeapi.dev/joke/Any?safe-mode') as resp:
            data = await resp.json()
            if data['type'] == 'single':
                await ctx.send(f"😂 {data['joke']}")
            else:
                await ctx.send(f"😂 {data['setup']}\n\n||{data['delivery']}||")


@bot.command(name='fact')
async def fact_cmd(ctx):
    """Случайный факт: bari fact"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://uselessfacts.jsph.pl/random.json?language=ru') as resp:
            data = await resp.json()
            await ctx.send(f"📖 {data['text']}")


@bot.command(name='advice')
async def advice_cmd(ctx):
    """Случайный совет: bari advice"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.adviceslip.com/advice') as resp:
            data = await resp.json()
            await ctx.send(f"💡 {data['slip']['advice']}")


@bot.command(name='quote')
async def quote_cmd(ctx):
    """Случайная цитата: bari quote"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.quotable.io/random') as resp:
            data = await resp.json()
            await ctx.send(f"📝 \"{data['content']}\"\n- **{data['author']}**")


@bot.command(name='trivia')
async def trivia_cmd(ctx):
    """Вопрос викторины: bari trivia"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://opentdb.com/api.php?amount=1&type=multiple') as resp:
            data = await resp.json()
            q = data['results'][0]
            await ctx.send(f"❓ **Вопрос:** {q['question']}\nСложность: {q['difficulty']}")


@bot.command(name='rps')
async def rps_cmd(ctx, choice: str):
    """Камень, ножницы, бумага: bari rps камень"""
    choices = ['камень', 'ножницы', 'бумага']
    if choice.lower() not in choices:
        await ctx.send("❌ Выбери: камень, ножницы, бумага")
        return

    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = "Ничья!"
    elif (choice.lower() == 'камень' and bot_choice == 'ножницы') or (
            choice.lower() == 'ножницы' and bot_choice == 'бумага') or (
            choice.lower() == 'бумага' and bot_choice == 'камень'):
        result = "Ты выиграл!"
    else:
        result = "Я выиграл!"

    await ctx.send(f"✊ Вы выбрали **{choice}**, я выбрал **{bot_choice}**.\n{result}")


@bot.command(name='flip')
async def flip_cmd(ctx):
    """Подбросить монетку: bari flip"""
    result = random.choice(["Орёл", "Решка"])
    await ctx.send(f"🪙 {ctx.author.mention} выпал **{result}**")


# =====================================================
# 🔥 НАСТРОЙКИ
# =====================================================
@bot.command(name='setup-logs')
async def setuplogs_cmd(ctx, channel: discord.TextChannel):
    """Установить канал логов: bari setup-logs #логи"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    save_json(LOGS_SETTINGS_FILE, {str(ctx.guild.id): channel.id})
    await ctx.send(f"✅ Логи будут отправляться в {channel.mention}")


@bot.command(name='setup-welcome')
async def setupwelcome_cmd(ctx, channel: discord.TextChannel, *, message: str = "Добро пожаловать {member}!"):
    """Настроить приветствия: bari setup-welcome #канал Текст {member}"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json(WELCOME_SETTINGS_FILE)
    gid = str(ctx.guild.id)
    if gid not in s:
        s[gid] = {}
    s[gid]['welcome_enabled'] = True
    s[gid]['welcome_channel_id'] = channel.id
    s[gid]['welcome_message'] = message
    save_json(WELCOME_SETTINGS_FILE, s)
    await ctx.send(f"✅ Приветствия настроены в {channel.mention}")


@bot.command(name='disable-welcome')
async def disablewelcome_cmd(ctx):
    """Отключить приветствия: bari disable-welcome"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json(WELCOME_SETTINGS_FILE)
    gid = str(ctx.guild.id)
    if gid in s:
        s[gid]['welcome_enabled'] = False
        save_json(WELCOME_SETTINGS_FILE, s)
        await ctx.send("✅ Приветствия отключены")


@bot.command(name='setup-photowelcome')
async def setupphotowelcome_cmd(ctx, channel: discord.TextChannel):
    """Настроить фото-приветствия: bari setup-photowelcome #канал"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json(WELCOME_SETTINGS_FILE)
    gid = str(ctx.guild.id)
    if gid not in s:
        s[gid] = {}
    s[gid]['photo_welcome'] = {'enabled': True, 'channel_id': channel.id}
    save_json(WELCOME_SETTINGS_FILE, s)
    await ctx.send(f"✅ Фото-приветствия настроены в {channel.mention}")


@bot.command(name='setup-captcha')
async def setupcaptcha_cmd(ctx, role: discord.Role):
    """Настроить капчу: bari setup-captcha @роль"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    save_json(CAPTCHA_SETTINGS_FILE, {str(ctx.guild.id): {'enabled': True, 'verify_role_id': role.id}})
    await ctx.send(f"✅ Капча настроена с ролью {role.mention}")


@bot.command(name='disable-captcha')
async def disablecaptcha_cmd(ctx):
    """Отключить капчу: bari disable-captcha"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json(CAPTCHA_SETTINGS_FILE)
    gid = str(ctx.guild.id)
    if gid in s:
        s[gid]['enabled'] = False
        save_json(CAPTCHA_SETTINGS_FILE, s)
        await ctx.send("✅ Капча отключена")


@bot.command(name='massunban')
async def massunban_cmd(ctx, *, reason: str = "Массовый разбан"):
    """Разбан всех пользователей: bari massunban причина"""
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ Нет прав!")
        return

    banned = [entry async for entry in ctx.guild.bans()]
    if not banned:
        await ctx.send("❌ На сервере нет забаненных пользователей!")
        return

    await ctx.send(f"🔄 Начинаю разбан **{len(banned)}** пользователей...")
    success = 0
    for entry in banned:
        try:
            await ctx.guild.unban(entry.user, reason=reason)
            success += 1
            await asyncio.sleep(0.5)
        except:
            pass

    await ctx.send(f"✅ Разбанено {success} из {len(banned)} пользователей")


@bot.command(name='setup-application')
async def setupapplication_cmd(ctx, moderator: discord.Role = None, administrator: discord.Role = None):
    """Настройка заявок: bari setup-application @модератор @админ"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json('bariier_settings.json')
    gid = str(ctx.guild.id)
    if gid not in s:
        s[gid] = {}
    if moderator:
        s[gid]['moderator_role'] = moderator.id
    if administrator:
        s[gid]['admin_role'] = administrator.id
    save_json('bariier_settings.json', s)
    await ctx.send("✅ Настройки заявок сохранены!")


@bot.command(name='create-apps')
async def createapps_cmd(ctx):
    """Создать меню заявок: bari create-apps"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    s = load_json('bariier_settings.json').get(str(ctx.guild.id), {})
    if not s:
        await ctx.send("❌ Сначала настрой роли через `bari setup-application`")
        return

    class AppSelect(discord.ui.Select):
        def __init__(self):
            opts = []
            if s.get('moderator_role'):
                opts.append(discord.SelectOption(label='Модератор', emoji='🛡️', value='moderator'))
            if s.get('admin_role'):
                opts.append(discord.SelectOption(label='Администратор', emoji='👑', value='admin'))
            super().__init__(placeholder='📋 Выбери должность...', options=opts)

        async def callback(self, select_interaction: discord.Interaction):
            class AppModal(discord.ui.Modal):
                def __init__(self, role_type):
                    self.role_type = role_type
                    super().__init__(title=f'Заявка на {role_type}')
                    self.add_item(discord.ui.TextInput(label='Почему ты хочешь эту должность?',
                                                       style=discord.TextStyle.paragraph))
                    self.add_item(discord.ui.TextInput(label='Какой у тебя опыт?', style=discord.TextStyle.paragraph))

                async def on_submit(self, modal_i: discord.Interaction):
                    rid = s.get(f'{self.role_type}_role')
                    if rid and (r := modal_i.guild.get_role(rid)):
                        embed = discord.Embed(title=f"📥 Новая заявка на {self.role_type}",
                                              description=f"От: {modal_i.user.mention}", color=discord.Color.green())
                        embed.add_field(name="Почему?", value=self.children[0].value[:500])
                        embed.add_field(name="Опыт", value=self.children[1].value[:500])
                        await modal_i.channel.send(r.mention, embed=embed)
                        await modal_i.response.send_message("✅ Заявка отправлена!", ephemeral=True)
                    else:
                        await modal_i.response.send_message("❌ Роль не найдена!", ephemeral=True)

            await select_interaction.response.send_modal(AppModal(self.values[0]))

    view = discord.ui.View()
    view.add_item(AppSelect())
    embed = discord.Embed(title="📝 Заявки", description="Выбери должность из меню ниже, чтобы подать заявку",
                          color=discord.Color.blue())
    await ctx.send(embed=embed, view=view)


@bot.command(name='create-application')
async def createapplication_cmd(ctx, название: str, роль: discord.Role, канал: discord.TextChannel):
    """Создать заявку: bari create-application Название @роль #канал"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    apps = load_json(APPLICATIONS_FILE)
    gid = str(ctx.guild.id)
    if gid not in apps:
        apps[gid] = {}

    app_id = len(apps[gid]) + 1
    apps[gid][str(app_id)] = {'name': название, 'role_id': роль.id, 'questions': [], 'channel_id': ctx.channel.id,
                              'send_channel_id': канал.id}
    save_json(APPLICATIONS_FILE, apps)

    await ctx.send(f"✅ Заявка \"{название}\" создана! ID: {app_id}\nДобавь вопросы через `bari add-question {app_id}`")
    await ctx.send(f"📝 Для отправки заявки используй `bari submit-application {app_id}`")


@bot.command(name='list-applications')
async def listapplications_cmd(ctx):
    """Список заявок: bari list-applications"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    apps = load_json(APPLICATIONS_FILE).get(str(ctx.guild.id), {})
    if not apps:
        await ctx.send("❌ Нет созданных заявок!")
        return

    embed = discord.Embed(title="📋 Список заявок", color=discord.Color.blue())
    for app_id, app in apps.items():
        role = ctx.guild.get_role(app.get('role_id'))
        embed.add_field(name=f"ID: {app_id} - {app.get('name')}",
                        value=f"Роль: {role.mention if role else 'Нет'}\nВопросов: {len(app.get('questions', []))}",
                        inline=False)
    await ctx.send(embed=embed)


@bot.command(name='delete-application')
async def deleteapplication_cmd(ctx, app_id: str):
    """Удалить заявку: bari delete-application 1"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    apps = load_json(APPLICATIONS_FILE)
    gid = str(ctx.guild.id)
    if gid not in apps or app_id not in apps[gid]:
        await ctx.send("❌ Заявка не найдена!")
        return

    del apps[gid][app_id]
    save_json(APPLICATIONS_FILE, apps)
    await ctx.send(f"✅ Заявка #{app_id} удалена!")


# =====================================================
# 🔥 АВТОМОДЕРАЦИЯ (REGEX)
# =====================================================
BAD_WORDS = ['хуй', 'пизда', 'бля', 'залупа', 'ебать', 'лох', 'сука', 'блять', 'пидор', 'шлюха', 'fuck', 'shit',
             'bitch', 'asshole', 'damn']
PERMANENT_BAN_PHRASES = ['ваш сервер', 'твой сервер', 'реклама', 'иди на свой сервер', 'server sucks']


@bot.command(name='regex')
async def regex_cmd(ctx, action: str):
    """Включить/выключить автомодерацию: bari regex on/off/status"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    settings = load_json(REGEX_SETTINGS_FILE)
    gid = str(ctx.guild.id)

    if action == 'on':
        settings[gid] = {'enabled': True}
        save_json(REGEX_SETTINGS_FILE, settings)
        await ctx.send("🛡️ Автомодерация **ВКЛЮЧЕНА**\n📝 Маты → мут на 1 час\n🔨 Оскорбление сервера → бан")
    elif action == 'off':
        if gid in settings:
            settings[gid]['enabled'] = False
            save_json(REGEX_SETTINGS_FILE, settings)
        await ctx.send("⚫ Автомодерация **ВЫКЛЮЧЕНА**")
    elif action == 'status':
        is_enabled = settings.get(gid, {}).get('enabled', False)
        status = "🔴 ВКЛЮЧЕНА" if is_enabled else "⚫ ВЫКЛЮЧЕНА"
        await ctx.send(f"🛡️ Статус автомодерации: {status}")
    else:
        await ctx.send("❌ Используй: `bari regex on/off/status`")


@bot.command(name='tech_work')
async def tech_work_cmd(ctx, action: str):
    """Режим техработ (только для разработчика)"""
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        await ctx.send("❌ Нет прав!")
        return

    global tech_work_active
    if action == 'on':
        tech_work_active = True
        await ctx.send("🛠️ Режим техработ **ВКЛЮЧЁН**")
    elif action == 'off':
        tech_work_active = False
        await ctx.send("✅ Режим техработ **ВЫКЛЮЧЁН**")
    elif action == 'status':
        status = "ВКЛЮЧЁН" if tech_work_active else "ВЫКЛЮЧЁН"
        await ctx.send(f"🛠️ Статус техработ: **{status}**")
    else:
        await ctx.send("❌ Используй: `bari tech_work on/off/status`")


tech_work_active = False


@bot.command(name='lang')
async def lang_cmd(ctx, language: str):
    """Сменить язык: bari lang ru/en/es/fr"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Нет прав!")
        return

    if language in ['ru', 'en', 'es', 'fr']:
        s = load_json(LANG_SETTINGS_FILE)
        s[str(ctx.guild.id)] = language
        save_json(LANG_SETTINGS_FILE, s)
        messages = {'ru': '🌐 Язык изменён на Русский!', 'en': '🌐 Language changed to English!',
                    'es': '🌐 Idioma cambiado a Español!', 'fr': '🌐 Langue changée en Français!'}
        await ctx.send(messages.get(language, "✅ Язык изменён!"))
    else:
        await ctx.send("❌ Доступные языки: ru, en, es, fr")


@bot.command(name='commands')
async def commands_list_cmd(ctx):
    """Показать все команды с примерами"""
    embed = discord.Embed(
        title="🛡️ bariier Bot - Все команды",
        description="Префикс: `bari`\nПример: `bari mute @user 1h 1.2`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📋 Информация (10)",
        value="`hello`, `ping`, `info`, `serverinfo`, `userinfo`, `avatar`, `admins`, `bots`, `uptime`, `authors`, `invite`",
        inline=False
    )

    embed.add_field(
        name="🛡️ Модерация (15)",
        value="`mute`, `unmute`, `ban`, `unban`, `kick`, `clear`, `slowmode`, `lock`, `unlock`, `report`, `pin`, `unpin`, `softban`, `massban`, `clean`, `setnick`, `setupantinuke`",
        inline=False
    )

    embed.add_field(
        name="⚠️ Предупреждения (8)",
        value="`warn`, `warnings`, `unwarn`, `topwarnings`, `strike`, `unstrike`, `strikes`, `topstrikes`",
        inline=False
    )

    embed.add_field(
        name="🎤 Голосовые (6)",
        value="`vmute`, `vunmute`, `vdeafen`, `vundeafen`, `vkick`, `vmove`",
        inline=False
    )

    embed.add_field(
        name="⏰ Таймаут (2)",
        value="`timeout`, `untimeout`",
        inline=False
    )

    embed.add_field(
        name="👑 Роли и каналы (11)",
        value="`addrole`, `removerole`, `createrole`, `deleterole`, `reactionrole`, `createchannel`, `deletechannel`, `clonechannel`, `movechannel`",
        inline=False
    )

    embed.add_field(
        name="⭐ Промоция (6)",
        value="`promotion`, `setuppromotion`, `leaderboard`, `addxp`, `setxp`, `setlevel`",
        inline=False
    )

    embed.add_field(
        name="🛠️ Утилиты (9)",
        value="`calc`, `poll`, `afk`, `unafk`, `remindme`, `timestamp`, `color`, `qr-code`, `giveaway`",
        inline=False
    )

    embed.add_field(
        name="🎉 Развлечения (9)",
        value="`cat`, `roll`, `8ball`, `joke`, `fact`, `advice`, `quote`, `trivia`, `rps`, `flip`",
        inline=False
    )

    embed.add_field(
        name="⚙️ Настройки (12)",
        value="`setactivitycheck`, `checknow`, `setup-logs`, `setup-welcome`, `disable-welcome`, `setup-photowelcome`, `setup-captcha`, `disable-captcha`, `setup-ticket`, `massunban`, `setup-application`, `create-apps`, `create-application`, `list-applications`, `delete-application`",
        inline=False
    )

    embed.add_field(
        name="🔧 Прочее (5)",
        value="`regex`, `servers`, `tech_work`, `lang`, `commands`",
        inline=False
    )

    embed.set_footer(text=f"Всего команд: 85 | bariier Bot")
    await ctx.send(embed=embed)


@bot.command(name='authorbot')
async def authorbot(ctx, member: discord.Member = None):
    """Информация о боте"""
    if member is None:
        await ctx.send("❌ Укажи бота. Пример: `bari authorbot @bariier Bot`")
        return
    if not member.bot:
        await ctx.send("❌ Это не бот!")
        return

    # Получаем публичную инфу через RPC endpoint
    rpc_data = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://discord.com/api/v10/applications/{member.id}/rpc") as resp:
                if resp.status == 200:
                    rpc_data = await resp.json()
    except Exception:
        pass

    # Для самого bariier Bot — получаем владельца
    owner_text = None
    if member.id == bot.user.id:
        try:
            app = await bot.fetch_application_info()
            owner_text = f"{app.owner.name} (`{app.owner.id}`)"
        except Exception:
            pass

    created_at = member.created_at.strftime('%d.%m.%Y')
    joined_at = member.joined_at.strftime('%d.%m.%Y') if member.joined_at else 'Неизвестно'

    description = rpc_data.get('description', '')

    embed = discord.Embed(
        title=f"🤖 {member.name}",
        description=description[:300] if description else None,
        color=member.color if member.color != discord.Color.default() else discord.Color.blurple()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="📛 Тег", value=f"`{member.name}`", inline=True)
    embed.add_field(name="📅 Создан", value=created_at, inline=True)
    embed.add_field(name="📥 Зашёл на сервер", value=joined_at, inline=True)

    # Публичный бот?
    bot_public = rpc_data.get('bot_public')
    if bot_public is not None:
        embed.add_field(name="🌐 Публичный", value="✅ Да" if bot_public else "❌ Нет", inline=True)

    # Автор
    if owner_text:
        embed.add_field(name="👤 Разработчик", value=owner_text, inline=False)
    else:
        embed.add_field(name="👤 Разработчик", value="🔒 Скрыто (Discord не раскрывает)", inline=False)

    roles = [r.mention for r in member.roles if r.name != '@everyone']
    if roles:
        embed.add_field(name=f"🎭 Роли ({len(roles)})", value=' '.join(roles[:10]) + ('...' if len(roles) > 10 else ''), inline=False)

    invite_url = f"https://discord.com/oauth2/authorize?client_id={member.id}&permissions=8&scope=bot%20applications.commands"
    embed.add_field(name="🔗 Добавить", value=f"[Пригласить бота]({invite_url})", inline=False)

    embed.set_footer(text=f"Запросил {ctx.author.name}")
    await ctx.send(embed=embed)


@bot.command(name='serverinvite')
async def serverinvite(ctx, guild_id: int = None):
    """Получить ссылку-приглашение на сервер по ID"""
    if guild_id is None:
        await ctx.send("❌ Укажи ID сервера. Пример: `bari serverinvite 761141141965897738`")
        return

    guild = bot.get_guild(guild_id)
    if guild is None:
        await ctx.send(f"❌ Бот не состоит на сервере с ID `{guild_id}`")
        return

    invite = None
    for channel in guild.text_channels:
        try:
            invite = await channel.create_invite(max_age=0, max_uses=0, unique=False)
            break
        except Exception:
            continue

    if invite is None:
        await ctx.send(f"❌ Не удалось создать инвайт для **{guild.name}** — нет прав или нет текстовых каналов")
        return

    embed = discord.Embed(
        title=f"🔗 Инвайт на {guild.name}",
        description=f"{invite.url}",
        color=discord.Color.blue()
    )
    embed.add_field(name="👥 Участников", value=str(guild.member_count), inline=True)
    embed.add_field(name="🆔 ID сервера", value=str(guild.id), inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)


# =====================================================
# 🔥 СОБЫТИЯ
# =====================================================


# ========== МУЗЫКА ==========
music_queues = {}  # guild_id -> list of (url, title)

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

def get_audio_info(query):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        if not query.startswith('http'):
            query = f'ytsearch:{query}'
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

async def play_next(ctx):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        return
    url, title = music_queues[guild_id].pop(0)
    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
    ctx.voice_client.play(
        discord.PCMVolumeTransformer(source),
        after=lambda e: bot.loop.create_task(play_next(ctx))
    )
    await ctx.send(f"🎵 Сейчас играет: **{title}**")

@bot.command(name='play')
async def play(ctx, *, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ Ты не в голосовом канале!")

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)

    await ctx.send(f"🔍 Ищу: **{query}**...")

    try:
        url, title = await asyncio.get_event_loop().run_in_executor(None, get_audio_info, query)
    except Exception as e:
        return await ctx.send(f"❌ Не удалось найти трек: `{e}`")

    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        music_queues[guild_id].append((url, title))
        await ctx.send(f"📋 Добавлено в очередь: **{title}**")
    else:
        music_queues[guild_id].insert(0, (url, title))
        await play_next(ctx)

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client is None:
        return await ctx.send("❌ Бот не в голосовом канале!")
    guild_id = ctx.guild.id
    if guild_id in music_queues:
        music_queues[guild_id].clear()
    ctx.voice_client.stop()
    await ctx.voice_client.disconnect()
    await ctx.send("⏹ Музыка остановлена, бот вышел из канала.")

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        return await ctx.send("❌ Сейчас ничего не играет!")
    ctx.voice_client.stop()
    await ctx.send("⏭ Трек пропущен.")

@bot.command(name='queue')
async def queue_cmd(ctx):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        return await ctx.send("📋 Очередь пуста.")
    lines = [f"`{i+1}.` {title}" for i, (_, title) in enumerate(music_queues[guild_id])]
    embed = discord.Embed(title="📋 Очередь музыки", description="\n".join(lines[:10]), color=COLOR_BLUE)
    await ctx.send(embed=embed)


from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()


# ===================================

TOKEN = os.getenv('DISCORD_TOKEN', '')
if not TOKEN:
    print('❌ DISCORD_TOKEN is not set!')
    exit(1)
bot.run(TOKEN)
