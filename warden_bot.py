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

BLACKLIST_USERS = [1290322870290878539]

async def check_blacklist(i: discord.Interaction):
    """Проверяет, находится ли пользователь в чёрном списке"""
    if i.user.id in BLACKLIST_USERS:
        embed = discord.Embed(
            title="⛔ ДОСТУП ЗАПРЕЩЁН",
            description="**Вы находитесь в чёрном списке бота.**\nОбратитесь к администратору для разблокировки.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Warden Bot • Блокировка")
        await i.response.send_message(embed=embed, ephemeral=True)
        return True
    return False

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
            'hello_title': '✨ Приветствие',
            'hello_footer': 'Warden Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Задержка:** `{} ms`\n**Статус:** {}',
            'ping_good': '🟢 Отлично',
            'ping_medium': '🟡 Средне',
            'ping_bad': '🔴 Плохо',
            'ping_footer': 'Warden Bot | 🌐 Статус сети',
            'lang_changed_title': '🌐 Язык изменён',
            'lang_changed_footer': 'Warden Bot | Настройки',
            'lang_ru_desc': 'Изменить язык на русский',
            'lang_en_desc': 'Change language to English',
            'lang_es_desc': 'Cambiar idioma a español',
            'lang_fr_desc': 'Changer la langue en français',
            'lang_footer': 'Warden Bot • 🔒 Требуются права администратора',
            'serverinfo_footer': 'ID сервера: {} • Warden Bot',
            'userinfo_footer': 'Warden Bot | Информация',
            'avatar_footer': 'Warden Bot | Аватар пользователя',
            'membercount_footer': 'Warden Bot | Статистика',
            'calc_title': '🧮 Калькулятор',
            'calc_footer': 'Warden Bot | Утилиты',
            'poll_title': '📊 Голосование: {}',
            'poll_footer': 'Warden Bot | Голосование активно',
            'poll_created': '✅ Голосование создано',
            'afk_title': '💤 AFK режим',
            'afk_footer': 'Warden Bot | AFK',
            'reminder_title': '⏰ Напоминание установлено',
            'reminder_footer': 'Warden Bot | Напоминание',
            'timestamp_title': '🕐 Текущий timestamp',
            'timestamp_footer': 'Warden Bot | Утилиты',
            'color_title': '🎨 Информация о цвете {}',
            'color_footer': 'Warden Bot | Информация о цвете',
            'qr_title': '📱 QR Код',
            'qr_footer': 'Warden Bot | QR Генератор',
            'uptime_title': '🕐 Время работы бота',
            'uptime_footer': 'Warden Bot | Статистика',
            'giveaway_title': '🎁 Розыгрыш',
            'giveaway_footer': 'Warden Bot | Удачи!',
            'giveaway_prize': '🏆 Приз: {}',
            'giveaway_winners': '👑 Победителей: {}',
            'giveaway_duration': '⏰ Длительность: {}',
            'cat_title': '🐱 Случайный котик',
            'cat_footer': 'Warden Bot | Котики',
            'roll_title': '🎲 Бросок кубика',
            'roll_footer': 'Warden Bot | Игры',
            'eightball_title': '🎱 Магический шар',
            'eightball_question': '❓ Вопрос',
            'eightball_footer': 'Warden Bot | Предсказания',
            'joke_title': '😂 Шутка',
            'joke_footer': 'Warden Bot | Юмор',
            'fact_title': '📖 Случайный факт',
            'fact_footer': 'Warden Bot | Интересно',
            'advice_title': '💡 Совет',
            'advice_footer': 'Warden Bot | Мудрость',
            'quote_title': '📝 Цитата',
            'quote_footer': 'Warden Bot | Вдохновение',
            'trivia_title': '❓ Викторина',
            'trivia_footer': 'Warden Bot | Викторины',
            'rps_title': '✊ Камень, ножницы, бумага',
            'rps_footer': 'Warden Bot | Игры',
            'rps_choice': 'Вы выбрали **{}**, я выбрал **{}**.',
            'flip_title': '🪙 Монетка',
            'flip_footer': 'Warden Bot | Игры',
            'flip_result': 'Выпал **{}**!',
            'setup_logs_title': '📋 Настройка логов',
            'setup_logs_footer': 'Warden Bot | Логирование',
            'setup_welcome_title': '👋 Настройка приветствий',
            'setup_welcome_footer': 'Warden Bot | Приветствия',
            'setup_photowelcome_title': '🖼️ Настройка фото-приветствий',
            'setup_photowelcome_footer': 'Warden Bot | Приветствия с фото',
            'disable_welcome_title': '⚠️ Отключение приветствий',
            'disable_welcome_footer': 'Warden Bot | Приветствия отключены',
            'setup_captcha_title': '🔐 Настройка капчи',
            'setup_captcha_footer': 'Warden Bot | Безопасность',
            'disable_captcha_title': '🔐 Отключение капчи',
            'disable_captcha_footer': 'Warden Bot | Капча отключена',
            'invite_title': '🔗 Пригласить',
            'invite_desc': 'Спасибо за приглашение на свой сервер!',
            'invite_footer': 'Warden Bot | Приглашения',
            'invite_button': '🤖 Пригласить бота',
            'server_button': '🌐 Сервер поддержки',
            'send_dm_title': '📨 Сообщение отправлено',
            'send_dm_success': '✅ Сообщение успешно отправлено пользователю {} (ID: {})',
            'send_dm_text': '📝 Текст сообщения',
            'send_dm_footer': 'Warden Bot | Разработка',
            'servers_title': '📊 Список серверов с ботом',
            'servers_footer': 'Всего серверов: {} • Warden Bot',
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
            'regex_footer': 'Warden Bot | Защита',
            'blacklist_title': '⛔ ДОСТУП ЗАПРЕЩЁН',
            'blacklist_desc': '**Вы находитесь в чёрном списке бота.**\nОбратитесь к администратору для разблокировки.',
            'blacklist_footer': 'Warden Bot • Блокировка',
            'massunban_title': '🔓 Массовый разбан',
            'massunban_success': '✅ Успешно разбанены',
            'massunban_list': '📋 Список разбаненных',
            'massunban_errors': '❌ Ошибки',
            'massunban_start': '🔄 Начинаю разбан **{}** пользователей...',
            'massunban_none': '❌ На сервере нет забаненных пользователей!',
            'massunban_footer': 'Запросил: {} • Warden Bot',
            'member_join_log': '🚪 Member joined',
            'member_remove_log': '🚪 Member left',
            'message_delete_log': '🗑️ Message deleted',
            'message_edit_log': '✏️ Message edited',
            'log_footer': 'Warden Bot | Логи',
            'hello': 'Привет, {}! Я **Warden Bot** 🤖',
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
            'info_title': '🛡️ Warden Bot',
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
            'hello': '¡Hola, {}! Soy **Warden Bot** 🤖',
            'ping': '🏓 Pong! Latencia: {} ms',
            'help_title': '📚 Ayuda - {}',
            'help_desc': 'Selecciona una categoría en el menú para ver la lista de comandos.\nO usa `/help all` para la lista completa.',
            'help_cmd_count': '{} comandos',
            'help_footer': '¿Sabías que solo hay 100 comandos? :3',
            'help_all_title': '📖 Todos los comandos',
            'help_all_desc': 'Lista completa de todos los comandos del bot:',
            'help_category_title': '{} - Lista de comandos',
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
            'info_title': '🛡️ Warden Bot',
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
            'invite_footer': 'Warden Bot | Invitaciones',
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
            'serverinfo_footer': 'ID del servidor: {} • Warden Bot',
            'userinfo_title': 'Información de {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'Se unió',
            'userinfo_created': 'Creado',
            'userinfo_bot': 'Bot',
            'userinfo_roles_header': 'Roles',
            'userinfo_footer': 'Warden Bot | Información',
            'avatar_title': 'Avatar de {}',
            'avatar_title_full': 'Avatar de {}',
            'avatar_footer': 'Warden Bot | Avatar de usuario',
            'membercount_total': 'Total',
            'membercount_humans': 'Humanos',
            'membercount_bots': 'Bots',
            'membercount_title': '📊 Estadísticas de miembros',
            'membercount_footer': 'Warden Bot | Estadísticas',
            'admins_list': '👑 Administradores',
            'admins_title': '👑 Administradores del servidor',
            'admins_footer': 'Warden Bot | Administración',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots en el servidor',
            'bots_footer': 'Warden Bot | Bots',
            'none': 'Ninguno',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Expresión inválida',
            'calc_title': '🧮 Calculadora',
            'calc_footer': 'Warden Bot | Utilidades',
            'reminder_set': '✅ Recordatorio en {}',
            'reminder_invalid': '❌ Usa: 10s, 5m, 1h, 1d',
            'reminder_title': '⏰ Recordatorio Establecido',
            'reminder_footer': 'Warden Bot | Recordatorio',
            'uptime_text': '🕐 Tiempo activo: {}d {}h {}m',
            'uptime_title': '🕐 Tiempo de Actividad',
            'uptime_footer': 'Warden Bot | Estadísticas',
            'poll_created': '✅ ¡Encuesta creada!',
            'poll_voted': '✅ ¡Votado!',
            'poll_total': 'Total de votos: {}',
            'poll_title': '📊 Encuesta: {}',
            'poll_option': '{} votos',
            'poll_footer': 'Warden Bot | Encuesta activa',
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
            'lang_changed_footer': 'Warden Bot | Ajustes',
            'lang_ru_desc': 'Cambiar idioma a ruso',
            'lang_en_desc': 'Cambiar idioma a inglés',
            'lang_es_desc': 'Cambiar idioma a español',
            'lang_fr_desc': 'Cambiar idioma a francés',
            'lang_select_placeholder': '🌐 Selecciona idioma',
            'lang_current': '**Idioma actual:** {}',
            'lang_admin_only': '**¡Solo para administradores!**',
            'lang_select_menu': 'Selecciona un idioma del menú.',
            'lang_footer': 'Warden Bot • 🔒 Solo administradores',
            'promotion_level': '📊 Tu nivel: {} | XP: {}',
            'leaderboard_title': '🏆 Tabla de clasificación',
            'xp_added': '✅ {} XP añadidos a {}',
            'xp_set': '✅ {} XP establecidos para {}',
            'level_set': '✅ Nivel {} establecido para {}',
            'afk_set': '✅ {} ahora está AFK: {}',
            'afk_removed': '✅ AFK eliminado',
            'not_afk': '❌ No estás AFK',
            'afk_title': '💤 Modo AFK',
            'afk_footer': 'Warden Bot | AFK',
            'timestamp_current': '🕐 Marca de tiempo actual: {}',
            'timestamp_title': '🕐 Marca de Tiempo Actual',
            'timestamp_footer': 'Warden Bot | Utilidades',
            'color_info': '🎨 Información del color {}',
            'color_title': '🎨 Información del color {}',
            'color_footer': 'Warden Bot | Información de color',
            'qr_code_title': '📱 Código QR',
            'qr_title': '📱 Código QR',
            'qr_footer': 'Warden Bot | Generador QR',
            'giveaway_started': '🎁 ¡Sorteo iniciado!',
            'giveaway_title': '🎁 Sorteo',
            'giveaway_prize': '🏆 Premio: {}',
            'giveaway_winners': '👑 Ganadores: {}',
            'giveaway_duration': '⏰ Duración: {}',
            'giveaway_footer': 'Warden Bot | ¡Buena suerte!',
            'cat_title': '🐱 Gato Aleatorio',
            'cat_title_full': '🐱 Gato aleatorio',
            'cat_footer': 'Warden Bot | Gatos',
            'roll_result': '🎲 Tiraste {} (1-{})',
            'roll_title': '🎲 Lanzamiento de Dado',
            'roll_footer': 'Warden Bot | Juegos',
            'eightball_result': '🎱 {}',
            'eightball_title': '🎱 Bola Mágica',
            'eightball_title_full': '🎱 Bola mágica',
            'eightball_question': '❓ Pregunta',
            'eightball_footer': 'Warden Bot | Predicciones',
            'joke_title': '😂 Chiste',
            'joke_title_full': '😂 Chiste',
            'joke_footer': 'Warden Bot | Humor',
            'fact_title': '📖 Dato Aleatorio',
            'fact_title_full': '📖 Dato aleatorio',
            'fact_footer': 'Warden Bot | Interesante',
            'advice_title': '💡 Consejo',
            'advice_title_full': '💡 Consejo',
            'advice_footer': 'Warden Bot | Sabiduría',
            'quote_title': '📝 Cita',
            'quote_title_full': '📝 Cita',
            'quote_footer': 'Warden Bot | Inspiración',
            'trivia_question': '❓ {} (Dificultad: {})',
            'trivia_title': '❓ Trivia',
            'trivia_footer': 'Warden Bot | Trivia',
            'rps_win': '¡Ganaste!',
            'rps_lose': '¡Gané!',
            'rps_tie': '¡Empate!',
            'rps_title': '✊ Piedra, Papel, Tijera',
            'rps_choice': 'Elegiste **{}**, yo elegí **{}**.',
            'rps_footer': 'Warden Bot | Juegos',
            'flip_heads': 'Cara',
            'flip_tails': 'Cruz',
            'flip_title': '🪙 Lanzamiento de Moneda',
            'flip_result': '¡Salió **{}**!',
            'flip_footer': 'Warden Bot | Juegos',
            'welcome_configured': '✅ Bienvenidas configuradas en {}',
            'welcome_disabled': '✅ Bienvenidas desactivadas',
            'photo_welcome_configured': '✅ ¡Bienvenida con foto configurada!',
            'setup_logs_title': '📋 Configuración de Registros',
            'setup_logs_footer': 'Warden Bot | Registros',
            'setup_welcome_title': '👋 Configuración de Bienvenidas',
            'setup_welcome_footer': 'Warden Bot | Bienvenidas',
            'setup_photowelcome_title': '🖼️ Configuración de Bienvenida con Foto',
            'setup_photowelcome_footer': 'Warden Bot | Bienvenidas con Foto',
            'disable_welcome_title': '⚠️ Desactivar Bienvenidas',
            'disable_welcome_footer': 'Warden Bot | Bienvenidas Desactivadas',
            'captcha_configured': '✅ Captcha configurado con rol {}',
            'captcha_disabled': '✅ Captcha desactivado',
            'setup_captcha_title': '🔐 Configuración de Captcha',
            'setup_captcha_footer': 'Warden Bot | Seguridad',
            'disable_captcha_title': '🔐 Desactivar Captcha',
            'disable_captcha_footer': 'Warden Bot | Captcha Desactivado',
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
            'authors_title': '👑 Warden Bot | Autores y Desarrolladores',
            'authors_desc': '¡Este es el equipo que hizo posible este bot!',
            'authors_ceo': '👑 CEO / Fundador',
            'authors_ceo_value': '**Forever**\nDesarrollador principal y visionario',
            'authors_moderators': '🛠️ Moderadores',
            'authors_moderators_value': '**D1koot** - Moderador y Desarrollador\n**Andy.wirus** - Moderador y Probador',
            'authors_coder': '💻 Programador',
            'authors_coder_value': '**D1koot**\nDesarrollador principal del código',
            'authors_support': '🎧 Equipo de Soporte',
            'authors_support_value': '**K1APMI** - Soporte Técnico\n**Artem2012rtgf** - Ayuda a usuarios',
            'authors_thanks': '📢 Agradecimientos',
            'authors_thanks_value': '¡Gracias a todos los que ayudaron a probar y desarrollar el bot!\nEl bot fue creado para tu comodidad y seguridad.',
            'authors_footer': 'Warden Bot • Respeto a los desarrolladores',
            'hello_title': '✨ Saludo',
            'hello_footer': 'Warden Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latencia:** `{} ms`\n**Estado:** {}',
            'ping_good': '🟢 Excelente',
            'ping_medium': '🟡 Media',
            'ping_bad': '🔴 Mala',
            'ping_footer': 'Warden Bot | 🌐 Estado de red',
            'blacklist_title': '⛔ ACCESO DENEGADO',
            'blacklist_desc': '**Estás en la lista negra del bot.**\nContacta al administrador para ser desbloqueado.',
            'blacklist_footer': 'Warden Bot • Bloqueado',
            'massunban_title': '🔓 Desbaneo Masivo',
            'massunban_success': '✅ Desbaneados exitosamente',
            'massunban_list': '📋 Lista de desbaneados',
            'massunban_errors': '❌ Errores',
            'massunban_start': '🔄 Comenzando desbaneo de **{}** usuarios...',
            'massunban_none': '❌ ¡No hay usuarios baneados en el servidor!',
            'massunban_footer': 'Solicitado por: {} • Warden Bot',
            'send_dm_title': '📨 Mensaje Enviado',
            'send_dm_success': '✅ Mensaje enviado exitosamente al usuario {} (ID: {})',
            'send_dm_text': '📝 Texto del mensaje',
            'send_dm_footer': 'Warden Bot | Desarrollo',
            'servers_title': '📊 Lista de Servidores con el Bot',
            'servers_footer': 'Total de servidores: {} • Warden Bot',
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
            'regex_footer': 'Warden Bot | Protección',
            'member_join_log': '🚪 Miembro unido',
            'member_remove_log': '🚪 Miembro salió',
            'message_delete_log': '🗑️ Mensaje eliminado',
            'message_edit_log': '✏️ Mensaje editado',
            'log_footer': 'Warden Bot | Registros',
        },
        'fr': {
            'hello': 'Bonjour, {}! Je suis **Warden Bot** 🤖',
            'ping': '🏓 Pong! Latence: {} ms',
            'help_title': '📚 Aide - {}',
            'help_desc': 'Sélectionne une catégorie dans le menu pour voir la liste des commandes.\nOu utilise `/help all` pour la liste complète.',
            'help_cmd_count': '{} commandes',
            'help_footer': 'Saviez-vous qu\'il n\'y a que 100 commandes? :3',
            'help_all_title': '📖 Toutes les commandes',
            'help_all_desc': 'Liste complète de toutes les commandes du bot:',
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
            'info_title': '🛡️ Warden Bot',
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
            'invite_footer': 'Warden Bot | Invitations',
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
            'serverinfo_footer': 'ID du serveur: {} • Warden Bot',
            'userinfo_title': 'Informations sur {}',
            'userinfo_id': 'ID',
            'userinfo_joined': 'A rejoint',
            'userinfo_created': 'Créé',
            'userinfo_bot': 'Bot',
            'userinfo_roles_header': 'Rôles',
            'userinfo_footer': 'Warden Bot | Informations',
            'avatar_title': 'Avatar de {}',
            'avatar_title_full': 'Avatar de {}',
            'avatar_footer': 'Warden Bot | Avatar de l\'utilisateur',
            'membercount_total': 'Total',
            'membercount_humans': 'Humains',
            'membercount_bots': 'Bots',
            'membercount_title': '📊 Statistiques des membres',
            'membercount_footer': 'Warden Bot | Statistiques',
            'admins_list': '👑 Administrateurs',
            'admins_title': '👑 Administrateurs du serveur',
            'admins_footer': 'Warden Bot | Administration',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots sur le serveur',
            'bots_footer': 'Warden Bot | Bots',
            'none': 'Aucun',
            'calc_result': '🧮 `{}` = `{}`',
            'calc_invalid': '❌ Expression invalide',
            'calc_title': '🧮 Calculatrice',
            'calc_footer': 'Warden Bot | Utilitaires',
            'reminder_set': '✅ Rappel dans {}',
            'reminder_invalid': '❌ Utilise: 10s, 5m, 1h, 1d',
            'reminder_title': '⏰ Rappel Défini',
            'reminder_footer': 'Warden Bot | Rappel',
            'uptime_text': '🕐 Temps de fonctionnement: {}j {}h {}m',
            'uptime_title': '🕐 Temps de Fonctionnement',
            'uptime_footer': 'Warden Bot | Statistiques',
            'poll_created': '✅ Sondage créé!',
            'poll_voted': '✅ Voté!',
            'poll_total': 'Total des votes: {}',
            'poll_title': '📊 Sondage: {}',
            'poll_option': '{} votes',
            'poll_footer': 'Warden Bot | Sondage actif',
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
            'lang_changed_footer': 'Warden Bot | Paramètres',
            'lang_ru_desc': 'Changer la langue en russe',
            'lang_en_desc': 'Changer la langue en anglais',
            'lang_es_desc': 'Changer la langue en espagnol',
            'lang_fr_desc': 'Changer la langue en français',
            'lang_select_placeholder': '🌐 Choisis la langue',
            'lang_current': '**Langue actuelle:** {}',
            'lang_admin_only': '**Réservé aux administrateurs!**',
            'lang_select_menu': 'Sélectionne une langue dans le menu.',
            'lang_footer': 'Warden Bot • 🔒 Administrateurs uniquement',
            'promotion_level': '📊 Ton niveau: {} | XP: {}',
            'leaderboard_title': '🏆 Classement',
            'xp_added': '✅ {} XP ajoutés à {}',
            'xp_set': '✅ {} XP définis pour {}',
            'level_set': '✅ Niveau {} défini pour {}',
            'afk_set': '✅ {} est maintenant AFK: {}',
            'afk_removed': '✅ AFK retiré',
            'not_afk': '❌ Tu n\'es pas AFK',
            'afk_title': '💤 Mode AFK',
            'afk_footer': 'Warden Bot | AFK',
            'timestamp_current': '🕐 Horodatage actuel: {}',
            'timestamp_title': '🕐 Horodatage Actuel',
            'timestamp_footer': 'Warden Bot | Utilitaires',
            'color_info': '🎨 Informations sur la couleur {}',
            'color_title': '🎨 Informations sur la couleur {}',
            'color_footer': 'Warden Bot | Informations couleur',
            'qr_code_title': '📱 Code QR',
            'qr_title': '📱 Code QR',
            'qr_footer': 'Warden Bot | Générateur QR',
            'giveaway_started': '🎁 Concours lancé!',
            'giveaway_title': '🎁 Concours',
            'giveaway_prize': '🏆 Prix: {}',
            'giveaway_winners': '👑 Gagnants: {}',
            'giveaway_duration': '⏰ Durée: {}',
            'giveaway_footer': 'Warden Bot | Bonne chance!',
            'cat_title': '🐱 Chat Aléatoire',
            'cat_title_full': '🐱 Chat aléatoire',
            'cat_footer': 'Warden Bot | Chats',
            'roll_result': '🎲 Tu as lancé {} (1-{})',
            'roll_title': '🎲 Lancer de Dés',
            'roll_footer': 'Warden Bot | Jeux',
            'eightball_result': '🎱 {}',
            'eightball_title': '🎱 Boule Magique',
            'eightball_title_full': '🎱 Boule magique',
            'eightball_question': '❓ Question',
            'eightball_footer': 'Warden Bot | Prédictions',
            'joke_title': '😂 Blague',
            'joke_title_full': '😂 Blague',
            'joke_footer': 'Warden Bot | Humour',
            'fact_title': '📖 Fait Aléatoire',
            'fact_title_full': '📖 Fait aléatoire',
            'fact_footer': 'Warden Bot | Intéressant',
            'advice_title': '💡 Conseil',
            'advice_title_full': '💡 Conseil',
            'advice_footer': 'Warden Bot | Sagesse',
            'quote_title': '📝 Citation',
            'quote_title_full': '📝 Citation',
            'quote_footer': 'Warden Bot | Inspiration',
            'trivia_question': '❓ {} (Difficulté: {})',
            'trivia_title': '❓ Quiz',
            'trivia_footer': 'Warden Bot | Quiz',
            'rps_win': 'Tu as gagné!',
            'rps_lose': 'J\'ai gagné!',
            'rps_tie': 'Égalité!',
            'rps_title': '✊ Pierre, Papier, Ciseaux',
            'rps_choice': 'Tu as choisi **{}**, j\'ai choisi **{}**.',
            'rps_footer': 'Warden Bot | Jeux',
            'flip_heads': 'Pile',
            'flip_tails': 'Face',
            'flip_title': '🪙 Lancer de Pièce',
            'flip_result': 'C\'est tombé sur **{}**!',
            'flip_footer': 'Warden Bot | Jeux',
            'welcome_configured': '✅ Bienvenue configurée dans {}',
            'welcome_disabled': '✅ Bienvenue désactivée',
            'photo_welcome_configured': '✅ Bienvenue avec photo configurée!',
            'setup_logs_title': '📋 Configuration des Logs',
            'setup_logs_footer': 'Warden Bot | Journaux',
            'setup_welcome_title': '👋 Configuration des Bienvenues',
            'setup_welcome_footer': 'Warden Bot | Bienvenues',
            'setup_photowelcome_title': '🖼️ Configuration de la Bienvenue avec Photo',
            'setup_photowelcome_footer': 'Warden Bot | Bienvenues avec Photo',
            'disable_welcome_title': '⚠️ Désactiver les Bienvenues',
            'disable_welcome_footer': 'Warden Bot | Bienvenues Désactivées',
            'captcha_configured': '✅ Captcha configuré avec le rôle {}',
            'captcha_disabled': '✅ Captcha désactivé',
            'setup_captcha_title': '🔐 Configuration du Captcha',
            'setup_captcha_footer': 'Warden Bot | Sécurité',
            'disable_captcha_title': '🔐 Désactiver le Captcha',
            'disable_captcha_footer': 'Warden Bot | Captcha Désactivé',
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
            'authors_title': '👑 Warden Bot | Auteurs et Développeurs',
            'authors_desc': 'Voici l\'équipe qui a rendu ce bot possible!',
            'authors_ceo': '👑 CEO / Fondateur',
            'authors_ceo_value': '**Forever**\nDéveloppeur principal et visionnaire',
            'authors_moderators': '🛠️ Modérateurs',
            'authors_moderators_value': '**D1koot** - Modérateur et Développeur\n**Andy.wirus** - Modérateur et Testeur',
            'authors_coder': '💻 Programmeur',
            'authors_coder_value': '**D1koot**\nDéveloppeur principal du code',
            'authors_support': '🎧 Équipe de Support',
            'authors_support_value': '**K1APMI** - Support Technique\n**Artem2012rtgf** - Aide aux utilisateurs',
            'authors_thanks': '📢 Remerciements',
            'authors_thanks_value': 'Merci à tous ceux qui ont aidé à tester et développer le bot!\nLe bot a été créé pour votre confort et votre sécurité.',
            'authors_footer': 'Warden Bot • Respect aux développeurs',
            'hello_title': '✨ Salutation',
            'hello_footer': 'Warden Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latence:** `{} ms`\n**Statut:** {}',
            'ping_good': '🟢 Excellent',
            'ping_medium': '🟡 Moyenne',
            'ping_bad': '🔴 Mauvaise',
            'ping_footer': 'Warden Bot | 🌐 État du réseau',
            'blacklist_title': '⛔ ACCÈS REFUSÉ',
            'blacklist_desc': '**Tu es sur la liste noire du bot.**\nContacte l\'administrateur pour être débloqué.',
            'blacklist_footer': 'Warden Bot • Bloqué',
            'massunban_title': '🔓 Débannissement Massif',
            'massunban_success': '✅ Débannis avec succès',
            'massunban_list': '📋 Liste des débannis',
            'massunban_errors': '❌ Erreurs',
            'massunban_start': '🔄 Débannissement de **{}** utilisateurs...',
            'massunban_none': '❌ Aucun utilisateur banni sur le serveur!',
            'massunban_footer': 'Demandé par: {} • Warden Bot',
            'send_dm_title': '📨 Message Envoyé',
            'send_dm_success': '✅ Message envoyé avec succès à l\'utilisateur {} (ID: {})',
            'send_dm_text': '📝 Texte du message',
            'send_dm_footer': 'Warden Bot | Développement',
            'servers_title': '📊 Liste des Serveurs avec le Bot',
            'servers_footer': 'Total des serveurs: {} • Warden Bot',
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
            'regex_footer': 'Warden Bot | Protection',
            'member_join_log': '🚪 Membre a rejoint',
            'member_remove_log': '🚪 Membre est parti',
            'message_delete_log': '🗑️ Message supprimé',
            'message_edit_log': '✏️ Message modifié',
            'log_footer': 'Warden Bot | Journaux',
        },
        'en': {
            'hello_title': '✨ Greeting',
            'hello_footer': 'Warden Bot',
            'ping_title': '🏓 Pong!',
            'ping_result': '**Latency:** `{} ms`\n**Status:** {}',
            'ping_good': '🟢 Excellent',
            'ping_medium': '🟡 Medium',
            'ping_bad': '🔴 Bad',
            'ping_footer': 'Warden Bot | 🌐 Network Status',
            'lang_changed_title': '🌐 Language Changed',
            'lang_changed_footer': 'Warden Bot | Settings',
            'lang_ru_desc': 'Change language to Russian',
            'lang_en_desc': 'Change language to English',
            'lang_es_desc': 'Change language to Spanish',
            'lang_fr_desc': 'Change language to French',
            'lang_footer': 'Warden Bot • 🔒 Administrator only',
            'serverinfo_footer': 'Server ID: {} • Warden Bot',
            'userinfo_footer': 'Warden Bot | Information',
            'avatar_footer': 'Warden Bot | User Avatar',
            'membercount_footer': 'Warden Bot | Statistics',
            'calc_footer': 'Warden Bot | Utilities',
            'poll_footer': 'Warden Bot | Poll Active',
            'afk_footer': 'Warden Bot | AFK',
            'reminder_footer': 'Warden Bot | Reminder',
            'timestamp_footer': 'Warden Bot | Utilities',
            'color_footer': 'Warden Bot | Color Info',
            'qr_footer': 'Warden Bot | QR Generator',
            'uptime_footer': 'Warden Bot | Statistics',
            'giveaway_footer': 'Warden Bot | Good luck!',
            'cat_footer': 'Warden Bot | Cats',
            'roll_footer': 'Warden Bot | Games',
            'joke_footer': 'Warden Bot | Humor',
            'fact_footer': 'Warden Bot | Interesting',
            'advice_footer': 'Warden Bot | Wisdom',
            'quote_footer': 'Warden Bot | Inspiration',
            'trivia_footer': 'Warden Bot | Trivia',
            'rps_footer': 'Warden Bot | Games',
            'setup_logs_footer': 'Warden Bot | Logging',
            'setup_welcome_footer': 'Warden Bot | Welcomes',
            'setup_photowelcome_footer': 'Warden Bot | Photo Welcomes',
            'disable_welcome_footer': 'Warden Bot | Welcomes Disabled',
            'setup_captcha_footer': 'Warden Bot | Security',
            'disable_captcha_footer': 'Warden Bot | Captcha Disabled',
            'invite_title': '🔗 Invite',
            'invite_desc': 'Thanks for inviting me to your server!',
            'invite_footer': 'Warden Bot | Invites',
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
            'regex_footer': 'Warden Bot | Protection',
            'massunban_footer': 'Requested by: {} • Warden Bot',
            'member_join_log': '🚪 Member joined',
            'member_remove_log': '🚪 Member left',
            'message_delete_log': '🗑️ Message deleted',
            'message_edit_log': '✏️ Message edited',
            'log_footer': 'Warden Bot | Logs',
            'hello': 'Hello, {}! I am **Warden Bot** 🤖',
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
            'info_title': '🛡️ Warden Bot',
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
            'admins_footer': 'Warden Bot | Administration',
            'bots_list': '🤖 Bots',
            'bots_title': '🤖 Bots on Server',
            'bots_footer': 'Warden Bot | Bots',
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
            'eightball_footer': 'Warden Bot | Predictions',
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
            'authors_title': '👑 Warden Bot | Authors & Developers',
            'authors_desc': 'Here is the team that made this bot possible!',
            'authors_ceo': '👑 CEO / Founder',
            'authors_ceo_value': '**Forever**\nLead developer and visionary',
            'authors_moderators': '🛠️ Moderators',
            'authors_moderators_value': '**D1koot** - Moderator & Developer\n**Andy.wirus** - Moderator & Tester',
            'authors_coder': '💻 Coder',
            'authors_coder_value': '**D1koot**\nMain code developer',
            'authors_support': '🎧 Support Team',
            'authors_support_value': '**K1APMI** - Technical Support\n**Artem2012rtgf** - User Support',
            'authors_thanks': '📢 Special Thanks',
            'authors_thanks_value': 'Thanks to everyone who helped test and develop the bot!\nThe bot was created for your convenience and safety.',
            'authors_footer': 'Warden Bot • Respect to the developers',
            'blacklist_title': '⛔ ACCESS DENIED',
            'blacklist_desc': '**You are in the bot\'s blacklist.**\nContact the administrator to be unblocked.',
            'blacklist_footer': 'Warden Bot • Blocked',
            'massunban_title': '🔓 Mass Unban',
            'massunban_success': '✅ Successfully unbanned',
            'massunban_list': '📋 Unbanned list',
            'massunban_errors': '❌ Errors',
            'massunban_start': '🔄 Starting unban of **{}** users...',
            'massunban_none': '❌ No banned users on the server!',
            'send_dm_title': '📨 Message sent',
            'send_dm_success': '✅ Message successfully sent to user {} (ID: {})',
            'send_dm_text': '📝 Message text',
            'send_dm_footer': 'Warden Bot | Development',
            'servers_title': '📊 List of servers with bot',
            'servers_id': '🆔 ID: `{}`',
            'servers_owner': '👑 Owner: {}',
            'servers_members': '👥 Members: {}',
            'servers_your': '🔴 **YOURS**',
            'servers_footer': 'Total servers: {} • Warden Bot',
        },
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


@bot.tree.command(name='tech_work', description='Manage maintenance mode')
async def tech_work_cmd(i: discord.Interaction, action: str):
    if await check_blacklist(i): return
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
    if await check_blacklist(i): return

    if not i.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="⛔ ДОСТУП ЗАПРЕЩЁН",
            description="**Только администраторы могут изменять язык бота!**\nОбратитесь к администратору сервера.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Warden Bot • Требуются права администратора")
        return await i.response.send_message(embed=embed, ephemeral=True)

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
                    color=discord.Color.red()
                )
                embed.set_footer(text="Warden Bot • Insufficient permissions")
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
            embed.set_footer(text="Warden Bot • Settings" if selected != 'ru' else "Warden Bot • Настройки")
            await select_interaction.response.send_message(embed=embed, ephemeral=True)

    class LangView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.add_item(LanguageSelect())

    current_lang = get_lang(str(i.guild_id))
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
    embed.set_footer(text="Warden Bot • 🔒 Требуются права администратора / Administrator only")
    await i.response.send_message(embed=embed, view=LangView())


@bot.tree.command(name='hello', description='Greet Warden bot')
async def hello(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'hello_title'),
        description=get_text(str(i.guild_id), 'hello', i.user.mention),
        color=discord.Color.purple()
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'hello_footer'), icon_url=bot.user.avatar.url)
    await i.response.send_message(embed=embed)


@bot.tree.command(name='ping', description='Check bot latency')
async def ping(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    latency = round(bot.latency * 1000)

    if latency < 100:
        status_color = COLOR_SUCCESS
        status_text = get_text(str(i.guild_id), 'ping_good')
    elif latency < 300:
        status_color = COLOR_RED
        status_text = get_text(str(i.guild_id), 'ping_medium')
    else:
        status_color = COLOR_ERROR
        status_text = get_text(str(i.guild_id), 'ping_bad')

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'ping_title'),
        description=get_text(str(i.guild_id), 'ping_result', latency, status_text),
        color=status_color
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'ping_footer'))
    await i.response.send_message(embed=embed)


@bot.tree.command(name='info', description='Bot information')
async def info(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    e = discord.Embed(title=get_text(str(i.guild_id), 'info_title'), description=get_text(str(i.guild_id), 'info_desc'),
                      color=discord.Color.blue())
    e.add_field(name=get_text(str(i.guild_id), 'info_version'), value='v1.0.0', inline=True)
    e.add_field(name=get_text(str(i.guild_id), 'info_cmds'), value='Use `/help` to see all commands', inline=False)
    e.set_footer(text=get_text(str(i.guild_id), 'info_footer'))
    await i.response.send_message(embed=e)


@bot.tree.command(name='help', description='Все команды бота с категориями')
async def help_command(i: discord.Interaction, category: str = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    lang = get_lang(str(i.guild_id))

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
            description=get_text(str(i.guild_id), 'help_category_desc', len(cmds)),
            color=discord.Color.blue()
        )

        for j in range(0, len(cmds), 10):
            embed.add_field(
                name='‎',
                value=' '.join(cmds[j:j + 10]),
                inline=False
            )

        await i.response.send_message(embed=embed, ephemeral=True)
        return

    if category == 'all':
        embed = discord.Embed(
            title=get_text(str(i.guild_id), 'help_all_title'),
            description=get_text(str(i.guild_id), 'help_all_desc'),
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

        await i.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'help_title', 'Warden Bot'),
        description=get_text(str(i.guild_id), 'help_desc'),
        color=discord.Color.blue()
    )

    for cat_id, cat in categories.items():
        if cat_id in ['overview', 'all']:
            continue
        name = cat['name_ru'] if lang == 'ru' else cat['name_en']
        cmd_count = len(commands_by_cat.get(cat_id, []))
        embed.add_field(
            name=f'{cat["emoji"]} **{name}**',
            value=get_text(str(i.guild_id), 'help_cmd_count', cmd_count),
            inline=True
        )

    embed.set_footer(text=get_text(str(i.guild_id), 'help_footer'))

    class HelpSelect(discord.ui.Select):
        def __init__(self):
            options = []
            for cat_id, cat in categories.items():
                name = cat['name_ru'] if lang == 'ru' else cat['name_en']
                if cat_id == 'overview':
                    desc = get_text(str(i.guild_id), 'help_select_overview_desc')
                elif cat_id == 'all':
                    desc = get_text(str(i.guild_id), 'help_select_all_desc')
                elif cat_id == 'mod':
                    desc = get_text(str(i.guild_id), 'help_select_mod_desc')
                elif cat_id == 'roles':
                    desc = get_text(str(i.guild_id), 'help_select_roles_desc')
                elif cat_id == 'voice':
                    desc = get_text(str(i.guild_id), 'help_select_voice_desc')
                elif cat_id == 'info':
                    desc = get_text(str(i.guild_id), 'help_select_info_desc')
                elif cat_id == 'level':
                    desc = get_text(str(i.guild_id), 'help_select_level_desc')
                elif cat_id == 'util':
                    desc = get_text(str(i.guild_id), 'help_select_util_desc')
                elif cat_id == 'fun':
                    desc = get_text(str(i.guild_id), 'help_select_fun_desc')
                elif cat_id == 'setup':
                    desc = get_text(str(i.guild_id), 'help_select_setup_desc')
                elif cat_id == 'misc':
                    desc = get_text(str(i.guild_id), 'help_select_misc_desc')
                else:
                    desc = ''

                options.append(discord.SelectOption(
                    label=name,
                    emoji=cat['emoji'],
                    value=cat_id,
                    description=desc
                ))

            super().__init__(
                placeholder=get_text(str(i.guild_id), 'help_select_placeholder'),
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, select_interaction: discord.Interaction):
            selected = self.values[0]

            if selected == 'overview':
                embed = discord.Embed(
                    title=get_text(str(select_interaction.guild_id), 'help_title', 'Warden Bot'),
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

    await i.response.send_message(embed=embed, view=view, ephemeral=True)
    from datetime import datetime, timedelta, timezone


@bot.tree.command(name='setup-ticket', description='🎫 Настроить систему тикетов')
async def setup_ticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    save(TICKET_SETTINGS_FILE, {str(i.guild_id): {'category': category.id, 'role': support_role.id}})

    class TicketView(discord.ui.View):
        @discord.ui.button(label='🎫 Создать тикет', style=discord.ButtonStyle.primary)
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            s = load(TICKET_SETTINGS_FILE).get(str(bi.guild_id), {})
            cat = bi.guild.get_channel(s.get('category'))
            role = bi.guild.get_role(s.get('role'))
            name = f'ticket-{bi.user.name.lower()}-{random.randint(100, 999)}'

            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

            ch = await bi.guild.create_text_channel(name, category=cat, overwrites=ow)

            embed = discord.Embed(
                title='🎫 Новый тикет',
                description=f'**От:** {bi.user.mention}\n**ID:** {bi.user.id}\n**Статус:** ⏳ Ожидает ответа',
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name='📝 Вопрос', value='Опишите вашу проблему...', inline=False)
            embed.set_footer(text=f'ID: {name} • Warden Bot')

            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                    if not btn_i.user.guild_permissions.administrator and btn_i.user.id != bi.user.id:
                        return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                    await btn_i.response.send_message('🔒 Закрытие тикета...', ephemeral=True)
                    try:
                        await bi.user.send(f'✅ Ваш тикет **{name}** был закрыт.')
                    except:
                        pass
                    await asyncio.sleep(2)
                    await ch.delete()

                @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅')
                async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                    if not btn_i.user.guild_permissions.administrator:
                        return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                    embed.color = discord.Color.green()
                    embed.description = f'**От:** {bi.user.mention}\n**Статус:** ✅ ПРИНЯТ В РАБОТУ'
                    embed.add_field(name='👨‍💻 Принял', value=btn_i.user.mention, inline=False)
                    await btn_i.message.edit(embed=embed, view=self)
                    await btn_i.response.send_message('✅ Тикет принят в работу!', ephemeral=True)
                    try:
                        await bi.user.send(f'✅ Ваш тикет **{name}** принят в работу сотрудником {btn_i.user.mention}')
                    except:
                        pass

                @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.secondary, emoji='❌')
                async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                    if not btn_i.user.guild_permissions.administrator:
                        return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                    embed.color = discord.Color.red()
                    embed.description = f'**От:** {bi.user.mention}\n**Статус:** ❌ ОТКЛОНЁН'
                    embed.add_field(name='👨‍💻 Отклонил', value=btn_i.user.mention, inline=False)
                    await btn_i.message.edit(embed=embed, view=self)
                    await btn_i.response.send_message('❌ Тикет отклонён!', ephemeral=True)
                    try:
                        await bi.user.send(f'❌ Ваш тикет **{name}** был отклонён.')
                    except:
                        pass

                @discord.ui.button(label='✏️ Ответить с сообщением', style=discord.ButtonStyle.primary, emoji='✏️')
                async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                    if not btn_i.user.guild_permissions.administrator:
                        return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                    class ReplyModal(discord.ui.Modal):
                        def __init__(self):
                            super().__init__(title='📝 Ответ пользователю')
                            self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                               placeholder='Ваш ответ...', required=True))

                        async def on_submit(self, modal_i: discord.Interaction):
                            msg = self.children[0].value
                            embed.color = discord.Color.green()
                            embed.description = f'**От:** {bi.user.mention}\n**Статус:** ✅ ОТВЕЧЕНО'
                            embed.add_field(name='📝 Ответ сотрудника', value=msg, inline=False)
                            embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                            try:
                                await bi.user.send(
                                    f'📩 Ответ на ваш тикет **{name}** от {modal_i.user.mention}:\n\n{msg}')
                            except:
                                pass

                    await btn_i.response.send_modal(ReplyModal())

            await ch.send(embed=embed, view=TicketButtons())
            await bi.response.send_message(f'✅ Тикет создан: {ch.mention}', ephemeral=True)

    embed = discord.Embed(
        title='🎫 Система тикетов',
        description='Нажми на кнопку ниже, чтобы создать тикет.\nСотрудники ответят в ближайшее время.',
        color=discord.Color.blue()
    )
    embed.set_footer(text="Warden Bot | Поддержка")
    await i.channel.send(embed=embed, view=TicketView())
    await i.response.send_message('✅ Система тикетов настроена!', ephemeral=True)



@bot.tree.command(name='mute', description='Заглушить участника')
async def mute(i: discord.Interaction, user: discord.Member, minutes: int, rule: str, reason: str = "Не указана"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    if not i.user.guild_permissions.moderate_members:
        embed = discord.Embed(title="❌ Ошибка", description="У вас нет прав на использование этой команды!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    bot_member = i.guild.get_member(bot.user.id)
    if not bot_member.guild_permissions.moderate_members:
        embed = discord.Embed(title="❌ Ошибка бота", description="У меня нет прав `Управление участниками`! Выдайте мне эту роль.", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if user.id == i.guild.owner_id:
        embed = discord.Embed(title="❌ Ошибка", description="Нельзя замутить владельца сервера!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if user.bot:
        embed = discord.Embed(title="❌ Ошибка", description="Нельзя замутить другого бота!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if user.top_role >= bot_member.top_role and user.id != i.guild.owner_id:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не могу замутить {user.mention}! Его роль выше или равна моей.\nПереместите мою роль выше в списке.", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if minutes <= 0:
        embed = discord.Embed(title="❌ Ошибка", description="Время должно быть больше 0 минут!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if minutes > 40320:
        embed = discord.Embed(title="❌ Ошибка", description="Максимум 28 дней (40320 минут)!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

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

    audit_reason = f"Модератор: {i.user} (ID: {i.user.id}) | Правило: {rule} | Причина: {reason}"

    try:
        await user.timeout(until, reason=audit_reason)
        embed = discord.Embed(title='🔇 Мут | Наказание', description=f'**{user.mention}** получил мут на `{time_text}`', color=discord.Color.orange(), timestamp=datetime.now())
        embed.add_field(name='📋 Правило', value=rule, inline=False)
        embed.add_field(name='📝 Причина', value=reason, inline=False)
        embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
        embed.set_footer(text=f'ID: {user.id} • Warden Bot')
        await i.response.send_message(embed=embed)
        await send_log(i.guild_id, embed)
    except discord.Forbidden:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не хватает прав для мута {user.mention}!\nПроверьте, что моя роль выше его роли.", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        await i.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не удалось замутить пользователя: {str(e)[:100]}", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unmute', description='Unmute a member')
async def unmute(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.timed_out_until is None:
        return await i.response.send_message(get_text(str(i.guild_id), 'not_muted'), ephemeral=True)
    await member.timeout(None)
    embed = discord.Embed(title="🔊 Снятие мута", description=get_text(str(i.guild_id), 'unmuted', member.mention), color=discord.Color.green(), timestamp=datetime.now())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='ban', description='Забанить участника')
async def ban(i: discord.Interaction, user: discord.Member, rule: str, reason: str = "Не указана"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    if user.top_role >= i.user.top_role and i.user.id != i.guild.owner_id:
        return await i.response.send_message('❌ Нельзя забанить пользователя с ролью выше или равной вашей!', ephemeral=True)

    audit_reason = f"Модератор: {i.user} (ID: {i.user.id}) | Правило: {rule} | Причина: {reason}"
    await user.ban(reason=audit_reason)

    embed = discord.Embed(title='🔨 Бан | Наказание', description=f'{user.mention} был забанен', color=discord.Color.red(), timestamp=datetime.now())
    embed.add_field(name='📋 Правило', value=rule, inline=False)
    embed.add_field(name='📝 Причина', value=reason, inline=False)
    embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id} • Warden Bot')
    await i.response.send_message(embed=embed)
    await send_log(i.guild_id, embed)

    try:
        await user.send(f'🔨 Вы были забанены на сервере **{i.guild.name}**\n📋 Правило: {rule}\n📝 Причина: {reason}')
    except:
        pass


@bot.tree.command(name='unban', description='Разбанить пользователя по ID')
async def unban(i: discord.Interaction, userid: str, reason: str = "Не указана"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    try:
        user_id = int(userid)
        user = await bot.fetch_user(user_id)

        banned = [entry async for entry in i.guild.bans()]
        if not any(str(entry.user.id) == userid for entry in banned):
            return await i.response.send_message(f'❌ Пользователь с ID `{userid}` не в бане!', ephemeral=True)

        await i.guild.unban(user, reason=reason)

        embed = discord.Embed(title='🔓 Разбан', description=f'{user.mention} был разбанен', color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name='📝 Причина', value=reason, inline=False)
        embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
        embed.set_footer(text=f'ID: {user.id} • Warden Bot')
        await i.response.send_message(embed=embed)
        await send_log(i.guild_id, embed)

    except ValueError:
        await i.response.send_message('❌ Неверный формат ID!', ephemeral=True)
    except discord.NotFound:
        await i.response.send_message(f'❌ Пользователь с ID `{userid}` не найден!', ephemeral=True)
    except Exception as e:
        await i.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


@bot.tree.command(name='kick', description='Kick a member')
async def kick(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.kick(reason=reason)
    embed = discord.Embed(title="👢 Кик", description=get_text(str(i.guild_id), 'kicked', member.mention), color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name="📝 Причина", value=reason)
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='warn', description='Warn a member')
async def warn(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_blacklist(i): return
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
    embed = discord.Embed(title="⚠️ Выдано предупреждение", description=get_text(str(i.guild_id), 'warned', member.mention, wid), color=discord.Color.yellow(), timestamp=datetime.now())
    embed.add_field(name="📝 Причина", value=reason)
    embed.set_footer(text=f"ID: {member.id} • Warden Bot")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='warnings', description='Show warnings')
async def warnings(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(member.id), [])
    if not w:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_warnings', member.mention), ephemeral=True)
    e = discord.Embed(title=get_text(str(i.guild_id), 'warnings_title', member.name), description=get_text(str(i.guild_id), 'warnings_total', len(w)), color=0xe67e22)
    for ww in w[-5:]:
        mod = i.guild.get_member(ww['mod'])
        e.add_field(name=f"Warning #{ww['id']}", value=f"**Reason:** {ww['reason']}\n**Mod:** {mod.name if mod else 'Unknown'}", inline=False)
    e.set_footer(text="Warden Bot | Система предупреждений")
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topwarnings', description='Top warnings')
async def topwarnings(i: discord.Interaction):
    if await check_blacklist(i): return
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
    e.set_footer(text="Warden Bot | Рейтинг")
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='unwarn', description='Remove warning')
async def unwarn(i: discord.Interaction, member: discord.Member, warn_id: int):
    if await check_blacklist(i): return
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
            embed = discord.Embed(title="✅ Предупреждение снято", description=get_text(str(i.guild_id), 'warn_removed', warn_id), color=discord.Color.green())
            embed.set_footer(text="Warden Bot | Модерация")
            return await i.response.send_message(embed=embed, ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'warn_not_found', warn_id), ephemeral=True)


@bot.tree.command(name='slowmode', description='Set slowmode')
async def slowmode(i: discord.Interaction, channel: discord.TextChannel, seconds: int):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(title="🐢 Режим slowmode", description=get_text(str(i.guild_id), 'slowmode', seconds, channel.mention), color=discord.Color.blue(), timestamp=datetime.now())
    embed.set_footer(text="Warden Bot | Управление каналом")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='lock', description='Lock channel')
async def lock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=False)
    embed = discord.Embed(title="🔒 Канал заблокирован", description=get_text(str(i.guild_id), 'locked', channel.mention), color=discord.Color.red(), timestamp=datetime.now())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unlock', description='Unlock channel')
async def unlock(i: discord.Interaction, channel: discord.TextChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await channel.set_permissions(i.guild.default_role, send_messages=None)
    embed = discord.Embed(title="🔓 Канал разблокирован", description=get_text(str(i.guild_id), 'unlocked', channel.mention), color=discord.Color.green(), timestamp=datetime.now())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='report', description='Report user')
async def report(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    e = discord.Embed(title='📢 Report', description=f'{i.user.mention} reported {user.mention}', color=discord.Color.red())
    e.add_field(name='Reason', value=reason)
    e.set_footer(text="Warden Bot | Жалоба")
    await send_log(i.guild_id, e)
    await i.response.send_message(get_text(str(i.guild_id), 'report_sent'), ephemeral=True)


@bot.tree.command(name='pin', description='Pin message')
async def pin(i: discord.Interaction, message_id: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.pin()
        embed = discord.Embed(title="📌 Сообщение закреплено", description=get_text(str(i.guild_id), 'pinned'), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='unpin', description='Unpin message')
async def unpin(i: discord.Interaction, message_id: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(message_id))
        await msg.unpin()
        embed = discord.Embed(title="📌 Закрепление снято", description=get_text(str(i.guild_id), 'unpinned'), color=discord.Color.orange())
        await i.response.send_message(embed=embed, ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'msg_not_found'), ephemeral=True)


@bot.tree.command(name='vmute', description='Заглушить в голосовом канале')
async def vmute(i: discord.Interaction, user: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    if not user.voice:
        return await i.response.send_message(f'❌ {user.mention} не в голосовом канале!', ephemeral=True)

    await user.edit(mute=True)

    embed = discord.Embed(title='🔇 Голосовой мут', description=f'{user.mention} заглушен в голосовом канале', color=discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id} • Warden Bot')
    await i.response.send_message(embed=embed)
    await send_log(i.guild_id, embed)


@bot.tree.command(name='vunmute', description='Unmute in voice')
async def vunmute(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(mute=False)
        embed = discord.Embed(title="🔊 Снятие голосового мута", description=get_text(str(i.guild_id), 'voice_unmuted', member.mention), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vdeafen', description='Deafen in voice')
async def vdeafen(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=True)
        embed = discord.Embed(title="🔇 Голосовая глухота", description=get_text(str(i.guild_id), 'voice_deafened', member.mention), color=discord.Color.orange())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vundeafen', description='Undeafen in voice')
async def vundeafen(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.deafen_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.edit(deafen=False)
        embed = discord.Embed(title="🔊 Снятие голосовой глухоты", description=get_text(str(i.guild_id), 'voice_undeafened', member.mention), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vkick', description='Kick from voice')
async def vkick(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(None)
        embed = discord.Embed(title="🎤 Выгон из голосового", description=get_text(str(i.guild_id), 'voice_kicked', member.mention), color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='vmove', description='Move in voice')
async def vmove(i: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.move_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.voice:
        await member.move_to(channel)
        embed = discord.Embed(title="🔊 Перемещение в голосовом", description=get_text(str(i.guild_id), 'voice_moved', member.mention, channel.name), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_in_voice'), ephemeral=True)


@bot.tree.command(name='serverinfo', description='Server info')
async def serverinfo(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    g = i.guild
    e = discord.Embed(
        title=get_text(str(i.guild_id), 'serverinfo_title', g.name),
        color=COLOR_BLUE,
        timestamp=datetime.now()
    )
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_owner'), value=g.owner.mention if g.owner else 'Unknown')
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_members'), value=g.member_count)
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_channels'), value=len(g.channels))
    e.add_field(name=get_text(str(i.guild_id), 'serverinfo_roles'), value=len(g.roles))
    e.set_footer(text=get_text(str(i.guild_id), 'serverinfo_footer', g.id))
    await i.response.send_message(embed=e)


@bot.tree.command(name='userinfo', description='User info')
async def userinfo(i: discord.Interaction, member: discord.Member = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    m = member or i.user
    e = discord.Embed(
        title=get_text(str(i.guild_id), 'userinfo_title', m.name),
        color=m.color if m.color else COLOR_BLUE,
        timestamp=datetime.now()
    )
    if m.avatar: e.set_thumbnail(url=m.avatar.url)
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_id'), value=m.id)
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_joined'),
                value=m.joined_at.strftime('%d.%m.%Y %H:%M') if m.joined_at else 'Unknown')
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_created'),
                value=m.created_at.strftime('%d.%m.%Y %H:%M'))
    e.add_field(name=get_text(str(i.guild_id), 'userinfo_bot'), value='✅ Да' if m.bot else '❌ Нет')
    e.set_footer(text=get_text(str(i.guild_id), 'userinfo_footer'))
    await i.response.send_message(embed=e)


@bot.tree.command(name='avatar', description='Show avatar')
async def avatar(i: discord.Interaction, member: discord.Member = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    m = member or i.user
    e = discord.Embed(
        title=get_text(str(i.guild_id), 'avatar_title', m.name),
        color=COLOR_BLUE
    )
    e.set_image(url=m.display_avatar.url)
    e.set_footer(text=get_text(str(i.guild_id), 'avatar_footer'))
    await i.response.send_message(embed=e)


@bot.tree.command(name='admins', description='Server admins')
async def admins(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    admins_list = [m.mention for m in i.guild.members if m.guild_permissions.administrator]
    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'admins_title'),
        description=' '.join(admins_list) or get_text(str(i.guild_id), 'none'),
        color=discord.Color.gold()
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'admins_footer'))
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='bots', description='Bots on server')
async def bots(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    bots_list = [m.mention for m in i.guild.members if m.bot]
    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'bots_title'),
        description=' '.join(bots_list) or get_text(str(i.guild_id), 'none'),
        color=discord.Color.blurple()
    )
    embed.set_footer(text=get_text(str(i.guild_id), 'bots_footer'))
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='timeout', description='Timeout member')
async def timeout(i: discord.Interaction, member: discord.Member, minutes: int, reason: str = "Not specified"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.timeout(datetime.now() + timedelta(minutes=minutes), reason=reason)
    embed = discord.Embed(title="⏰ Таймаут", description=get_text(str(i.guild_id), 'timeout_set', member.mention, minutes), color=discord.Color.orange(), timestamp=datetime.now())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='untimeout', description='Remove timeout')
async def untimeout(i: discord.Interaction, member: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.timeout(None)
    embed = discord.Embed(title="✅ Таймаут снят", description=get_text(str(i.guild_id), 'timeout_removed', member.mention), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='softban', description='Softban')
async def softban(i: discord.Interaction, member: discord.Member, reason: str = "Not specified"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.ban(reason=reason)
    await i.guild.unban(member, reason="Softban")
    embed = discord.Embed(title="🔄 Софтбан", description=get_text(str(i.guild_id), 'softbanned', member.mention), color=discord.Color.purple())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='authors', description='Показать список авторов и разработчиков бота')
async def authors(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'authors_title'),
        description=get_text(str(i.guild_id), 'authors_desc'),
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name=get_text(str(i.guild_id), 'authors_ceo'),
        value=get_text(str(i.guild_id), 'authors_ceo_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(i.guild_id), 'authors_moderators'),
        value=get_text(str(i.guild_id), 'authors_moderators_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(i.guild_id), 'authors_coder'),
        value=get_text(str(i.guild_id), 'authors_coder_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(i.guild_id), 'authors_support'),
        value=get_text(str(i.guild_id), 'authors_support_value'),
        inline=False
    )

    embed.add_field(
        name=get_text(str(i.guild_id), 'authors_thanks'),
        value=get_text(str(i.guild_id), 'authors_thanks_value'),
        inline=False
    )

    embed.set_footer(text=get_text(str(i.guild_id), 'authors_footer'))
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)

    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='massban', description='Mass ban')
async def massban(i: discord.Interaction, ids: str, reason: str = "Not specified"):
    if await check_blacklist(i): return
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
    embed = discord.Embed(title="🔨 Масс-бан", description=get_text(str(i.guild_id), 'massbanned', count), color=discord.Color.red())
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='clean', description='Clean bot messages')
async def clean(i: discord.Interaction, amount: int = 10):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    deleted = 0
    async for msg in i.channel.history(limit=amount):
        if msg.author == bot.user:
            await msg.delete()
            deleted += 1
    embed = discord.Embed(title="🧹 Очистка сообщений", description=get_text(str(i.guild_id), 'bot_messages_deleted', deleted), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Утилиты")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='strike', description='Give strike')
async def strike(i: discord.Interaction, user: discord.Member, reason: str):
    if await check_blacklist(i): return
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
    embed = discord.Embed(title="⚠️ Страйк выдан", description=get_text(str(i.guild_id), 'strike_given', user.mention, sid), color=discord.Color.orange())
    embed.add_field(name="📝 Причина", value=reason)
    embed.set_footer(text="Warden Bot | Модерация")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unstrike', description='Remove strike')
async def unstrike(i: discord.Interaction, user: discord.Member, sid: int):
    if await check_blacklist(i): return
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
            embed = discord.Embed(title="✅ Страйк снят", description=get_text(str(i.guild_id), 'strike_removed', sid, user.mention), color=discord.Color.green())
            embed.set_footer(text="Warden Bot | Модерация")
            return await i.response.send_message(embed=embed, ephemeral=True)
    await i.response.send_message(get_text(str(i.guild_id), 'strike_not_found', sid), ephemeral=True)


@bot.tree.command(name='strikes', description='Show strikes')
async def strikes(i: discord.Interaction, user: discord.Member):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {}).get(str(user.id), [])
    if not w:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_strikes', user.mention), ephemeral=True)
    e = discord.Embed(title=f'⚠️ Страйки пользователя {user.name}', description=f'Всего: {len(w)}', color=0xe67e22)
    for s in w[-5:]:
        mod = i.guild.get_member(s['mod'])
        e.add_field(name=f"Страйк #{s['id']}", value=f"Причина: {s['reason']}\nМодератор: {mod.name if mod else 'Unknown'}", inline=False)
    e.set_footer(text="Warden Bot | Система страйков")
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='topstrikes', description='Top strikes')
async def topstrikes(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.kick_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    w = load(WARNS_FILE).get(str(i.guild_id), {})
    if not w: return await i.response.send_message('Нет страйков', ephemeral=True)
    counts = []
    for uid, lst in w.items():
        if (m := i.guild.get_member(int(uid))):
            counts.append((m, len(lst)))
    counts.sort(key=lambda x: x[1], reverse=True)
    e = discord.Embed(title='🏆 Топ страйков', color=0x3498db)
    for m, c in counts[:10]:
        e.add_field(name=m.name, value=f'{c} страйков', inline=False)
    e.set_footer(text="Warden Bot | Рейтинг")
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='setnick', description='Set nickname')
async def setnick(i: discord.Interaction, member: discord.Member, nick: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_nicknames:
        embed = discord.Embed(title="❌ Ошибка", description=get_text(str(i.guild_id), 'no_permission'), color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if len(nick) > 32:
        embed = discord.Embed(title="❌ Ошибка", description=f"Никнейм не может быть длиннее **32 символов**!\nТвой никнейм: `{nick}` ({len(nick)} символов)", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    if not nick.strip():
        embed = discord.Embed(title="❌ Ошибка", description="Никнейм не может быть пустым!", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        return await i.response.send_message(embed=embed, ephemeral=True)

    try:
        await member.edit(nick=nick)
        embed = discord.Embed(title="✏️ Смена никнейма", description=get_text(str(i.guild_id), 'nickname_set', member.mention, nick), color=discord.Color.green(), timestamp=datetime.now())
        embed.add_field(name="👮 Модератор", value=i.user.mention, inline=False)
        embed.set_footer(text=f"ID: {member.id} • Warden Bot")
        await i.response.send_message(embed=embed, ephemeral=True)

        log_embed = discord.Embed(title="✏️ Смена никнейма", description=f"{member.mention} изменил никнейм", color=discord.Color.blue(), timestamp=datetime.now())
        log_embed.add_field(name="Новый никнейм", value=nick, inline=False)
        log_embed.add_field(name="👮 Модератор", value=i.user.mention, inline=False)
        log_embed.set_footer(text=f"ID: {member.id}")
        await send_log(i.guild_id, log_embed)

    except discord.Forbidden:
        embed = discord.Embed(title="❌ Ошибка", description="У меня нет прав менять никнейм этому пользователю!\n(Возможно, его роль выше моей)", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        await i.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title="❌ Ошибка", description=f"Не удалось изменить никнейм: {str(e)[:100]}", color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Модерация")
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setupantinuke', description='Setup antinuke')
async def setupantinuke(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    embed = discord.Embed(title="🛡️ Анти-нук", description=get_text(str(i.guild_id), 'antinuke_configured'), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Защита")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='addrole', description='Add role')
async def addrole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.add_roles(role)
    embed = discord.Embed(title="➕ Выдача роли", description=get_text(str(i.guild_id), 'role_added', role.mention, member.mention), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Управление ролями")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='removerole', description='Remove role')
async def removerole(i: discord.Interaction, member: discord.Member, role: discord.Role):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await member.remove_roles(role)
    embed = discord.Embed(title="➖ Снятие роли", description=get_text(str(i.guild_id), 'role_removed', role.mention, member.mention), color=discord.Color.orange())
    embed.set_footer(text="Warden Bot | Управление ролями")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='createrole', description='Create role')
async def createrole(i: discord.Interaction, name: str, color: str = "default"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    cols = {'red': 0xff0000, 'green': 0x00ff00, 'blue': 0x0000ff, 'yellow': 0xffff00, 'purple': 0xff00ff, 'default': 0x99aab5}
    r = await i.guild.create_role(name=name, color=cols.get(color, 0x99aab5))
    embed = discord.Embed(title="✨ Создание роли", description=get_text(str(i.guild_id), 'role_created', r.mention), color=discord.Color.green())
    embed.add_field(name="🎨 Цвет", value=color, inline=True)
    embed.set_footer(text="Warden Bot | Управление ролями")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='deleterole', description='Delete role')
async def deleterole(i: discord.Interaction, role: discord.Role):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await role.delete()
    embed = discord.Embed(title="🗑️ Удаление роли", description=get_text(str(i.guild_id), 'role_deleted'), color=discord.Color.red())
    embed.set_footer(text="Warden Bot | Управление ролями")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='reactionrole', description='Reaction role')
async def reactionrole(i: discord.Interaction, msg_id: str, role: discord.Role, emoji: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_roles:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        msg = await i.channel.fetch_message(int(msg_id))
        await msg.add_reaction(emoji)
        rr = load(REACTION_ROLES_FILE)
        rr[f"{i.guild_id}_{msg_id}_{emoji}"] = role.id
        save(REACTION_ROLES_FILE, rr)
        embed = discord.Embed(title="⚙️ Роль по реакции", description=get_text(str(i.guild_id), 'reaction_role_set', emoji, role.mention), color=discord.Color.blue())
        await i.response.send_message(embed=embed, ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'error', 'Message not found'), ephemeral=True)


@bot.tree.command(name='createchannel', description='Create channel')
async def createchannel(i: discord.Interaction, name: str, category: discord.CategoryChannel = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await i.guild.create_text_channel(name, category=category)
    embed = discord.Embed(title="#️⃣ Создание канала", description=get_text(str(i.guild_id), 'channel_created', name), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='deletechannel', description='Delete channel')
async def deletechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.delete()
    embed = discord.Embed(title="#️⃣ Удаление канала", description=get_text(str(i.guild_id), 'channel_deleted'), color=discord.Color.red())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='clonechannel', description='Clone channel')
async def clonechannel(i: discord.Interaction, ch: discord.TextChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.clone()
    embed = discord.Embed(title="#️⃣ Клонирование канала", description=get_text(str(i.guild_id), 'channel_cloned', ch.name), color=discord.Color.blue())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='movechannel', description='Move channel')
async def movechannel(i: discord.Interaction, ch: discord.TextChannel, pos: int):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_channels:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    await ch.edit(position=pos)
    embed = discord.Embed(title="#️⃣ Перемещение канала", description=get_text(str(i.guild_id), 'channel_moved', ch.name, pos), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


level_data = {}


@bot.tree.command(name='promotion', description='Your level')
async def promotion(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    uid = str(i.user.id)
    lvl = level_data.get(uid, {}).get('level', 0)
    xp = level_data.get(uid, {}).get('xp', 0)
    embed = discord.Embed(title="📊 Ваш прогресс", description=get_text(str(i.guild_id), 'promotion_level', lvl, xp), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Система уровней")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setuppromotion', description='Setup leveling')
async def setuppromotion(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    embed = discord.Embed(title="⚙️ Настройка уровней", description=get_text(str(i.guild_id), 'settings_saved'), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='leaderboard', description='Level leaderboard')
async def leaderboard(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    sorted_users = sorted(level_data.items(), key=lambda x: x[1].get('xp', 0), reverse=True)[:10]
    text = ''
    for idx, (uid, data) in enumerate(sorted_users, 1):
        m = i.guild.get_member(int(uid))
        if m:
            text += f'{idx}. {m.name} - Level {data.get("level", 0)} ({data.get("xp", 0)} XP)\n'
    if not text:
        text = 'Нет данных'
    e = discord.Embed(title=get_text(str(i.guild_id), 'leaderboard_title'), description=text, color=0x3498db)
    e.set_footer(text="Warden Bot | Рейтинг")
    await i.response.send_message(embed=e, ephemeral=True)


@bot.tree.command(name='addxp', description='Add XP')
async def addxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] += xp
    embed = discord.Embed(title="✨ Добавление XP", description=get_text(str(i.guild_id), 'xp_added', xp, member.mention), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setxp', description='Set XP')
async def setxp(i: discord.Interaction, member: discord.Member, xp: int):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['xp'] = xp
    embed = discord.Embed(title="🔧 Установка XP", description=get_text(str(i.guild_id), 'xp_set', xp, member.mention), color=discord.Color.blue())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setlevel', description='Set level')
async def setlevel(i: discord.Interaction, member: discord.Member, lvl: int):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    uid = str(member.id)
    if uid not in level_data:
        level_data[uid] = {'xp': 0, 'level': 0}
    level_data[uid]['level'] = lvl
    embed = discord.Embed(title="🔧 Установка уровня", description=get_text(str(i.guild_id), 'level_set', lvl, member.mention), color=discord.Color.blue())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='calc', description='Calculate')
async def calc(i: discord.Interaction, expression: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    try:
        res = eval(expression.replace('^', '**'))
        embed = discord.Embed(title="🧮 Калькулятор", description=get_text(str(i.guild_id), 'calc_result', expression, res), color=discord.Color.green())
        embed.set_footer(text="Warden Bot | Утилиты")
        await i.response.send_message(embed=embed, ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'calc_invalid'), ephemeral=True)


@bot.tree.command(name='poll', description='Create a poll')
async def poll(i: discord.Interaction, question: str, opt1: str, opt2: str, opt3: str = None, opt4: str = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    opts = [opt1, opt2]
    if opt3: opts.append(opt3)
    if opt4: opts.append(opt4)
    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']
    e = discord.Embed(title=f'📊 Голосование: {question}', color=0x3498db, timestamp=datetime.now())
    for idx, opt in enumerate(opts):
        e.add_field(name=f'{emojis[idx]} {opt}', value='0 голосов', inline=False)
    e.set_footer(text=f"Автор: {i.user.name} • Warden Bot")
    msg = await i.channel.send(embed=e)
    for idx in range(len(opts)):
        await msg.add_reaction(emojis[idx])
    embed = discord.Embed(title="✅ Голосование создано", description=get_text(str(i.guild_id), 'poll_created'), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


afk_data = {}


@bot.tree.command(name='afk', description='Set AFK')
async def afk(i: discord.Interaction, reason: str = "AFK"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    afk_data[str(i.user.id)] = reason
    embed = discord.Embed(title="💤 AFK режим", description=get_text(str(i.guild_id), 'afk_set', i.user.mention, reason), color=discord.Color.orange())
    embed.set_footer(text="Warden Bot | AFK")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='unafk', description='Remove AFK')
async def unafk(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if str(i.user.id) in afk_data:
        del afk_data[str(i.user.id)]
        embed = discord.Embed(title="✅ AFK снят", description=get_text(str(i.guild_id), 'afk_removed'), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    else:
        await i.response.send_message(get_text(str(i.guild_id), 'not_afk'), ephemeral=True)


@bot.tree.command(name='remindme', description='Set reminder')
async def remindme(i: discord.Interaction, time: str, reminder: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    try:
        unit = time[-1]
        amount = int(time[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        embed = discord.Embed(title="⏰ Напоминание установлено", description=get_text(str(i.guild_id), 'reminder_set', time), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
        await asyncio.sleep(sec)
        await i.user.send(f'⏰ **Напоминание:** {reminder}')
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'reminder_invalid'), ephemeral=True)


@bot.tree.command(name='timestamp', description='Current timestamp')
async def timestamp(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    embed = discord.Embed(title="🕐 Текущий timestamp", description=get_text(str(i.guild_id), 'timestamp_current', int(datetime.now().timestamp())), color=discord.Color.blue())
    embed.set_footer(text="Warden Bot | Утилиты")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='color', description='Color info')
async def color(i: discord.Interaction, hex_code: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    try:
        color = int(hex_code.strip('#'), 16)
        e = discord.Embed(title=get_text(str(i.guild_id), 'color_info', hex_code), color=color)
        e.add_field(name='RGB', value=f'{(color >> 16) & 255}, {(color >> 8) & 255}, {color & 255}')
        e.set_footer(text="Warden Bot | Информация о цвете")
        await i.response.send_message(embed=e)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'error', 'Invalid hex'), ephemeral=True)


@bot.tree.command(name='qr-code', description='Generate QR code')
async def qr_code(i: discord.Interaction, text: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={text}"
    e = discord.Embed(title=get_text(str(i.guild_id), 'qr_code_title'), color=0x3498db)
    e.set_image(url=url)
    e.set_footer(text="Warden Bot | QR Генератор")
    await i.response.send_message(embed=e)


start_time = datetime.now()


@bot.tree.command(name='uptime', description='Bot uptime')
async def uptime(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    delta = datetime.now() - start_time
    embed = discord.Embed(title="🕐 Время работы бота", description=get_text(str(i.guild_id), 'uptime_text', delta.days, delta.seconds // 3600, (delta.seconds % 3600) // 60), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Статистика")
    await i.response.send_message(embed=embed)


giveaways = {}


@bot.tree.command(name='giveaway', description='Start a giveaway')
async def giveaway(i: discord.Interaction, duration: str, prize: str, winners: int = 1):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        sec = amount * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[unit]
        e = discord.Embed(title='🎁 Розыгрыш', description=f'**Приз:** {prize}\n**Победителей:** {winners}\n**Длительность:** {duration}', color=0x00ff00, timestamp=datetime.now())
        e.set_footer(text="Warden Bot | Удачи!")
        msg = await i.channel.send(embed=e)
        await msg.add_reaction('🎉')
        giveaways[str(msg.id)] = {'channel': i.channel.id, 'prize': prize, 'winners': winners, 'end': datetime.now() + timedelta(seconds=sec)}
        embed = discord.Embed(title="✅ Розыгрыш запущен", description=get_text(str(i.guild_id), 'giveaway_started'), color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)
    except:
        await i.response.send_message(get_text(str(i.guild_id), 'invalid_time'), ephemeral=True)


@bot.tree.command(name='cat', description='Random cat')
async def cat(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.thecatapi.com/v1/images/search') as r:
            data = await r.json()
            e = discord.Embed(title=get_text(str(i.guild_id), 'cat_title'), color=0x3498db)
            e.set_image(url=data[0]['url'])
            e.set_footer(text="Warden Bot | Котики")
            await i.response.send_message(embed=e)


@bot.tree.command(name='roll', description='Roll dice')
async def roll(i: discord.Interaction, sides: int = 6):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    result = random.randint(1, sides)
    embed = discord.Embed(title="🎲 Бросок кубика", description=get_text(str(i.guild_id), 'roll_result', result, sides), color=discord.Color.blue())
    embed.set_footer(text="Warden Bot | Игры")
    await i.response.send_message(embed=embed)


@bot.tree.command(name='8ball', description='Magic 8ball')
async def eightball(i: discord.Interaction, question: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return

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

    lang = get_lang(str(i.guild_id))
    answers = answers_ru if lang == 'ru' else answers_en

    embed = discord.Embed(
        title=get_text(str(i.guild_id), 'eightball_title'),
        description=get_text(str(i.guild_id), 'eightball_result', random.choice(answers)),
        color=discord.Color.purple()
    )
    embed.add_field(name=get_text(str(i.guild_id), 'eightball_question'), value=question, inline=False)
    embed.set_footer(text=get_text(str(i.guild_id), 'eightball_footer'))
    await i.response.send_message(embed=embed)


@bot.tree.command(name='joke', description='Random joke')
async def joke(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://v2.jokeapi.dev/joke/Any?safe-mode') as r:
            data = await r.json()
            if data['type'] == 'single':
                embed = discord.Embed(title="😂 Шутка", description=data["joke"], color=discord.Color.green())
            else:
                embed = discord.Embed(title="😂 Шутка", description=f'{data["setup"]}\n\n||{data["delivery"]}||', color=discord.Color.green())
            embed.set_footer(text="Warden Bot | Юмор")
            await i.response.send_message(embed=embed)


@bot.tree.command(name='fact', description='Random fact')
async def fact(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://uselessfacts.jsph.pl/random.json?language=en') as r:
            data = await r.json()
            embed = discord.Embed(title="📖 Случайный факт", description=data["text"], color=discord.Color.blue())
            embed.set_footer(text="Warden Bot | Интересно")
            await i.response.send_message(embed=embed)


@bot.tree.command(name='advice', description='Random advice')
async def advice(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.adviceslip.com/advice') as r:
            data = await r.json()
            embed = discord.Embed(title="💡 Совет", description=data["slip"]["advice"], color=discord.Color.gold())
            embed.set_footer(text="Warden Bot | Мудрость")
            await i.response.send_message(embed=embed)


@bot.tree.command(name='quote', description='Random quote')
async def quote(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://api.quotable.io/random') as r:
            data = await r.json()
            embed = discord.Embed(title="📝 Цитата", description=f'"{data["content"]}"\n- **{data["author"]}**', color=discord.Color.purple())
            embed.set_footer(text="Warden Bot | Вдохновение")
            await i.response.send_message(embed=embed)


@bot.tree.command(name='trivia', description='Trivia question')
async def trivia(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    async with aiohttp.ClientSession() as s:
        async with s.get('https://opentdb.com/api.php?amount=1&type=multiple') as r:
            data = await r.json()
            q = data['results'][0]
            embed = discord.Embed(title="❓ Викторина", description=get_text(str(i.guild_id), 'trivia_question', q['question'], q['difficulty']), color=discord.Color.blue())
            embed.set_footer(text="Warden Bot | Викторины")
            await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='rps', description='Rock Paper Scissors')
async def rps(i: discord.Interaction, choice: str):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    choices = ['rock', 'paper', 'scissors']
    if choice.lower() not in choices:
        return await i.response.send_message(get_text(str(i.guild_id), 'error', 'Choose: rock, paper, scissors'), ephemeral=True)
    bot_choice = random.choice(choices)
    if choice.lower() == bot_choice:
        result = get_text(str(i.guild_id), 'rps_tie')
    elif (choice.lower() == 'rock' and bot_choice == 'scissors') or (choice.lower() == 'paper' and bot_choice == 'rock') or (choice.lower() == 'scissors' and bot_choice == 'paper'):
        result = get_text(str(i.guild_id), 'rps_win')
    else:
        result = get_text(str(i.guild_id), 'rps_lose')
    embed = discord.Embed(title="✊ Камень, ножницы, бумага", description=f'Вы выбрали **{choice}**, я выбрал **{bot_choice}**.\n{result}', color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Игры")
    await i.response.send_message(embed=embed)


@bot.tree.command(name='flip', description='Flip coin')
async def flip(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    result = random.choice([get_text(str(i.guild_id), 'flip_heads'), get_text(str(i.guild_id), 'flip_tails')])
    embed = discord.Embed(title="🪙 Монетка", description=f'Выпал **{result}**!', color=discord.Color.blue())
    embed.set_footer(text="Warden Bot | Игры")
    await i.response.send_message(embed=embed)


@bot.tree.command(name='setup-logs', description='Setup logging channel')
async def setup_logs(i: discord.Interaction, channel: discord.TextChannel):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    save(LOGS_SETTINGS_FILE, {str(i.guild_id): channel.id})

    embed = discord.Embed(title="📋 Настройка логов", description=get_text(str(i.guild_id), 'log_channel_set', channel.mention), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Логирование")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-welcome', description='Setup welcome message')
async def setup_welcome(i: discord.Interaction, channel: discord.TextChannel, message: str = "Welcome {member}!"):
    if await check_blacklist(i): return
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

    embed = discord.Embed(title="👋 Настройка приветствий", description=get_text(str(i.guild_id), 'welcome_configured', channel.mention), color=discord.Color.green())
    embed.add_field(name="📝 Сообщение", value=message, inline=False)
    embed.set_footer(text="Warden Bot | Приветствия")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='disable-welcome', description='Disable welcome')
async def disable_welcome(i: discord.Interaction):
    if await check_blacklist(i): return
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
        embed = discord.Embed(title="⚠️ Отключение приветствий", description=get_text(str(i.guild_id), 'welcome_disabled'), color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-captcha', description='Setup captcha')
async def setup_captcha(i: discord.Interaction, role: discord.Role):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)

    s = load(CAPTCHA_SETTINGS_FILE)
    s[str(i.guild_id)] = {'enabled': True, 'verify_role_id': role.id}
    save(CAPTCHA_SETTINGS_FILE, s)

    embed = discord.Embed(title="🔐 Настройка капчи", description=get_text(str(i.guild_id), 'captcha_configured', role.mention), color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Безопасность")
    await i.response.send_message(embed=embed, ephemeral=True)
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
async def create_application(i: discord.Interaction, название: str, роль: discord.Role, канал: discord.TextChannel):
    if await check_blacklist(i): return
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
        'send_channel_id': канал.id,
        'creator_id': i.user.id
    }
    save_applications(apps)

    class AddQuestionView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        @discord.ui.button(label='➕ Добавить вопрос', style=discord.ButtonStyle.primary)
        async def add_question(self, btn_i: discord.Interaction, button: discord.ui.Button):
            class AddQuestionModal(discord.ui.Modal):
                def __init__(self, app_id, app_name, role, gid, channel_id):
                    self.app_id = app_id
                    self.app_name = app_name
                    self.role = role
                    self.gid = gid
                    self.channel_id = channel_id
                    super().__init__(title='📝 Добавить вопрос')
                    self.add_item(discord.ui.TextInput(label='Вопрос', style=discord.TextStyle.paragraph, placeholder='Напиши вопрос для заявки...'))
                async def on_submit(self, modal_i: discord.Interaction):
                    question = self.children[0].value
                    apps = load_applications()
                    if self.gid not in apps: apps[self.gid] = {}
                    if str(self.app_id) not in apps[self.gid]: apps[self.gid][str(self.app_id)] = {'questions': []}
                    current_questions = apps[self.gid][str(self.app_id)].get('questions', [])
                    if len(current_questions) >= 8:
                        return await modal_i.response.send_message('❌ Максимум 8 вопросов!', ephemeral=True)
                    apps[self.gid][str(self.app_id)]['questions'].append(question)
                    save_applications(apps)
                    total = len(apps[self.gid][str(self.app_id)]['questions'])
                    embed = discord.Embed(title="✅ Вопрос добавлен", description=f'Вопрос добавлен! (Всего: {total}/8)', color=discord.Color.green())
                    await modal_i.response.send_message(embed=embed, ephemeral=True)
            await btn_i.response.send_modal(AddQuestionModal(app_id, название, роль, gid, i.channel.id))

        @discord.ui.button(label='✅ Завершить создание', style=discord.ButtonStyle.success)
        async def finish(self, btn_i: discord.Interaction, button: discord.ui.Button):
            apps_check = load_applications()
            questions = apps_check.get(gid, {}).get(str(app_id), {}).get('questions', [])
            if len(questions) < 1:
                return await btn_i.response.send_message('❌ Добавь хотя бы 1 вопрос!', ephemeral=True)
            if len(questions) > 8:
                return await btn_i.response.send_message('❌ Максимум 8 вопросов!', ephemeral=True)

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
                            embed.set_footer(text=f'ID заявки: {submission_id} • Warden Bot')
                            class ReviewView(discord.ui.View):
                                def __init__(self):
                                    super().__init__(timeout=86400)
                                @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅')
                                async def approve(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_i.user.guild_permissions.administrator: return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                                    all_apps = load_applications()
                                    if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                        all_apps['submissions'][submission_id]['status'] = 'approved'
                                        all_apps['submissions'][submission_id]['reviewed_by'] = btn_i.user.id
                                        all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                        save_applications(all_apps)
                                    if role:
                                        await interaction.user.add_roles(role)
                                        await btn_i.response.send_message(f'✅ Заявка одобрена! {interaction.user.mention} получил роль {role.mention}', ephemeral=True)
                                    else:
                                        await btn_i.response.send_message('✅ Заявка одобрена!', ephemeral=True)
                                    embed.color = discord.Color.green()
                                    embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ✅ ПРИНЯТА'
                                    embed.add_field(name='👮 Рассмотрел', value=btn_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed, view=None)
                                    try: await interaction.user.send(f'✅ Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}')
                                    except: pass
                                @discord.ui.button(label='❌ Отказать', style=discord.ButtonStyle.danger, emoji='❌')
                                async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_i.user.guild_permissions.administrator: return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                                    all_apps = load_applications()
                                    if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                        all_apps['submissions'][submission_id]['status'] = 'rejected'
                                        all_apps['submissions'][submission_id]['reviewed_by'] = btn_i.user.id
                                        all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                        save_applications(all_apps)
                                    await btn_i.response.send_message('❌ Заявка отклонена!', ephemeral=True)
                                    embed.color = discord.Color.red()
                                    embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ❌ ОТКЛОНЕНА'
                                    embed.add_field(name='👮 Рассмотрел', value=btn_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed, view=None)
                                    try: await interaction.user.send(f'❌ Ваша заявка **{app_name}** была ОТКЛОНЕНА.')
                                    except: pass
                                @discord.ui.button(label='✏️ Принять с сообщением', style=discord.ButtonStyle.primary, emoji='✏️')
                                async def approve_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_i.user.guild_permissions.administrator: return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                                    class ApproveMessageModal(discord.ui.Modal):
                                        def __init__(self):
                                            super().__init__(title='✅ Принять заявку')
                                            self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph, placeholder='Сообщение пользователю...', required=True))
                                        async def on_submit(self, modal_i: discord.Interaction):
                                            message_text = self.children[0].value
                                            all_apps = load_applications()
                                            if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                                all_apps['submissions'][submission_id]['status'] = 'approved_with_message'
                                                all_apps['submissions'][submission_id]['reviewed_by'] = modal_i.user.id
                                                all_apps['submissions'][submission_id]['review_message'] = message_text
                                                all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                                save_applications(all_apps)
                                            if role: await interaction.user.add_roles(role)
                                            embed.color = discord.Color.green()
                                            embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ✅ ПРИНЯТА (с сообщением)'
                                            embed.add_field(name='👮 Рассмотрел', value=modal_i.user.mention, inline=False)
                                            embed.add_field(name='📝 Сообщение', value=message_text[:500], inline=False)
                                            await btn_i.message.edit(embed=embed, view=None)
                                            await modal_i.response.send_message('✅ Заявка одобрена с сообщением!', ephemeral=True)
                                            try: await interaction.user.send(f'✅ Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}\n\n**Сообщение:**\n{message_text}')
                                            except: pass
                                    await btn_i.response.send_modal(ApproveMessageModal())
                                @discord.ui.button(label='📝 Отказать с сообщением', style=discord.ButtonStyle.secondary, emoji='📝')
                                async def reject_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                                    if not btn_i.user.guild_permissions.administrator: return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                                    class RejectMessageModal(discord.ui.Modal):
                                        def __init__(self):
                                            super().__init__(title='❌ Отказать заявке')
                                            self.add_item(discord.ui.TextInput(label='Причина', style=discord.TextStyle.paragraph, placeholder='Причина отказа...', required=True))
                                        async def on_submit(self, modal_i: discord.Interaction):
                                            message_text = self.children[0].value
                                            all_apps = load_applications()
                                            if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                                                all_apps['submissions'][submission_id]['status'] = 'rejected_with_message'
                                                all_apps['submissions'][submission_id]['reviewed_by'] = modal_i.user.id
                                                all_apps['submissions'][submission_id]['review_message'] = message_text
                                                all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                                                save_applications(all_apps)
                                            embed.color = discord.Color.red()
                                            embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ❌ ОТКАЗАНО (с сообщением)'
                                            embed.add_field(name='👮 Рассмотрел', value=modal_i.user.mention, inline=False)
                                            embed.add_field(name='📝 Причина', value=message_text[:500], inline=False)
                                            await btn_i.message.edit(embed=embed, view=None)
                                            await modal_i.response.send_message('❌ Заявка отклонена с сообщением!', ephemeral=True)
                                            try: await interaction.user.send(f'❌ Ваша заявка **{app_name}** была ОТКЛОНЕНА.\n\n**Причина:**\n{message_text}')
                                            except: pass
                                    await btn_i.response.send_modal(RejectMessageModal())
                            await send_channel.send(embed=embed, view=ReviewView())
                            await interaction.response.send_message('✅ Заявка отправлена! Ожидай решения.', ephemeral=True)
                    await apply_i.response.send_modal(ApplicationModal(app_id, gid, канал.id, page=0))
            embed = discord.Embed(title=f'📝 Заявка: {название}', description=f'Нажми на кнопку ниже, чтобы подать заявку.\nПосле проверки ты получишь роль {роль.mention}\n\nВсего вопросов: {len(questions)}', color=discord.Color.blue())
            embed.set_footer(text="Warden Bot | Заявки")
            await i.channel.send(embed=embed, view=ApplicationMenu())
            await btn_i.response.send_message('✅ Заявка создана! Кнопка отправлена в канал.', ephemeral=True)
            self.stop()

    embed = discord.Embed(title='📝 Создание заявки', description=f'**Название:** {название}\n**Роль:** {роль.mention}\n**Канал отправки:** {канал.mention}\n\nНажми на кнопки ниже, чтобы добавить вопросы.\n**Максимум 8 вопросов** (по 4 на страницу)', color=discord.Color.green())
    embed.set_footer(text="Warden Bot | Система заявок")
    await i.response.send_message(embed=embed, view=AddQuestionView(), ephemeral=True)


@bot.tree.command(name='list-applications', description='Показать список созданных заявок')
async def list_applications(i: discord.Interaction):
    if await check_blacklist(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)
    apps = load_applications().get(str(i.guild_id), {})
    if not apps:
        return await i.response.send_message('❌ Нет созданных заявок!', ephemeral=True)
    embed = discord.Embed(title='📋 Список заявок', color=discord.Color.blue())
    for app_id, app_data in apps.items():
        role = i.guild.get_role(app_data.get('role_id'))
        embed.add_field(name=f'ID: {app_id} - {app_data.get("name")}', value=f'Роль: {role.mention if role else "Не указана"}\nВопросов: {len(app_data.get("questions", []))}', inline=False)
    embed.set_footer(text="Warden Bot | Заявки")
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='delete-application', description='Удалить заявку по ID')
async def delete_application(i: discord.Interaction, id_заявки: str):
    if await check_blacklist(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)
    apps = load_applications()
    gid = str(i.guild_id)
    if gid not in apps or id_заявки not in apps[gid]:
        return await i.response.send_message('❌ Заявка не найдена!', ephemeral=True)
    del apps[gid][id_заявки]
    save_applications(apps)
    embed = discord.Embed(title="✅ Заявка удалена", description=f'Заявка #{id_заявки} удалена!', color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='massunban', description='Разбан всех пользователей на сервере')
async def massunban(i: discord.Interaction, reason: str = "Массовый разбан"):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    banned_users = [entry async for entry in i.guild.bans()]
    if len(banned_users) == 0:
        return await i.response.send_message('❌ На сервере нет забаненных пользователей!', ephemeral=True)
    await i.response.send_message(f'🔄 Начинаю разбан **{len(banned_users)}** пользователей...', ephemeral=True)
    success = []
    failed = []
    for entry in banned_users:
        user = entry.user
        try:
            await i.guild.unban(user, reason=reason)
            success.append(f'{user.name} ({user.id})')
        except Exception as e:
            failed.append(f'{user.name} ({user.id}) - {str(e)[:30]}')
    embed = discord.Embed(title='🔓 Массовый разбан', color=discord.Color.green() if not failed else discord.Color.orange(), timestamp=datetime.now())
    embed.add_field(name='✅ Успешно разбанены', value=f'**{len(success)}** из **{len(banned_users)}** пользователей', inline=False)
    if success: embed.add_field(name='📋 Список разбаненных', value='\n'.join(success[:15]) + ('\n...' if len(success) > 15 else ''), inline=False)
    if failed: embed.add_field(name='❌ Ошибки', value='\n'.join(failed[:10]), inline=False)
    embed.set_footer(text=f'Запросил: {i.user.name} • Warden Bot')
    await i.edit_original_response(content=None, embed=embed)


@bot.tree.command(name='disable-captcha', description='Disable captcha')
async def disable_captcha(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(CAPTCHA_SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid in s:
        s[gid]['enabled'] = False
        save(CAPTCHA_SETTINGS_FILE, s)
        embed = discord.Embed(title="🔐 Отключение капчи", description=get_text(str(i.guild_id), 'captcha_disabled'), color=discord.Color.red())
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='setup-application', description='Setup roles for applications')
async def setup_application(i: discord.Interaction, moderator: discord.Role = None, administrator: discord.Role = None):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE)
    gid = str(i.guild_id)
    if gid not in s: s[gid] = {}
    if moderator: s[gid]['moderator_role'] = moderator.id
    if administrator: s[gid]['admin_role'] = administrator.id
    save(SETTINGS_FILE, s)
    embed = discord.Embed(title="⚙️ Настройка заявок", description=get_text(str(i.guild_id), 'settings_saved'), color=discord.Color.green())
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='create-apps', description='Create application menu')
async def create_apps(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    s = load(SETTINGS_FILE).get(str(i.guild_id), {})
    if not s:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_roles'), ephemeral=True)
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
                async def on_submit(self, modal_i: discord.Interaction):
                    rid = self.s.get(f'{self.role_type}_role')
                    if rid and (r := modal_i.guild.get_role(rid)):
                        await modal_i.response.send_message(f'✅ Application sent to {r.mention}!', ephemeral=True)
                        e = discord.Embed(title=f'📥 New application for {self.role_type.title()}', description=f'From: {modal_i.user.mention}', color=0x00ff00)
                        e.add_field(name='Why?', value=self.children[0].value[:500])
                        e.add_field(name='Experience', value=self.children[1].value[:500])
                        e.set_footer(text="Warden Bot | Заявки")
                        await modal_i.channel.send(r.mention, embed=e)
                    else:
                        await modal_i.response.send_message(get_text(str(modal_i.guild_id), 'error', 'Role not found'), ephemeral=True)
            await select_interaction.response.send_modal(AppModal(self.values[0], s))
    view = discord.ui.View()
    view.add_item(AppSelect())
    e = discord.Embed(title='📝 Applications', description='Select a position from the menu below to apply.', color=0x2b2d31)
    await i.response.send_message(embed=e, view=view)


@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')

    bot.add_view(TicketView())

@bot.tree.command(name='invite', description='Invite bot')
async def invite(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    e = discord.Embed(title=get_text(str(i.guild_id), 'invite_title'), description=get_text(str(i.guild_id), 'invite_desc'), color=discord.Color.blue())
    if i.guild.icon: e.set_thumbnail(url=i.guild.icon.url)
    e.set_footer(text="Warden Bot | Приглашения")
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='🤖 Invite Bot', style=discord.ButtonStyle.link, url=f'https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands'))
    view.add_item(discord.ui.Button(label='🌐 Community Server', style=discord.ButtonStyle.link, url='https://discord.gg/invite'))
    await i.response.send_message(embed=e, view=view)


@bot.tree.command(name='send', description='Отправить ЛС пользователю по ID (только для разработчика)')
async def send_dm(i: discord.Interaction, user_id: str, message: str):
    if await check_blacklist(i): return
    ALLOWED_DEV_IDS = [1436760469980450816]
    if i.user.id not in ALLOWED_DEV_IDS:
        return await i.response.send_message('❌ Эта команда только для разработчиков!', ephemeral=True)
    if await check_tech_work(i): return
    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)
        await user.send(message)
        embed = discord.Embed(title='📨 Сообщение отправлено', description=f'✅ Сообщение успешно отправлено пользователю {user.name} (ID: {user_id})', color=discord.Color.green())
        embed.add_field(name='📝 Текст сообщения', value=message[:500], inline=False)
        embed.set_footer(text="Warden Bot | Разработка")
        await i.response.send_message(embed=embed, ephemeral=True)
    except ValueError:
        await i.response.send_message(f'❌ Неверный формат ID!', ephemeral=True)
    except discord.NotFound:
        await i.response.send_message(f'❌ Пользователь с ID `{user_id}` не найден!', ephemeral=True)
    except discord.Forbidden:
        await i.response.send_message(f'❌ Не могу отправить сообщение пользователю с ID `{user_id}` (закрыты ЛС)', ephemeral=True)
    except Exception as e:
        await i.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


VIP_USER_ID = 1436760469980450816
VIP_NICKNAME = "Ceo.wander Forever.morgan"
VIP_ROLE_NAME = "CEO.WANDER.BOT👑"
VIP_ROLE_COLOR = 0xffffff

WHITELIST_USERS = [1436760469980450816]

@bot.tree.command(name='regex', description='Включить/выключить авто-мут/бан за нарушения')
@app_commands.choices(attribute=[
    app_commands.Choice(name='🔴 Включить', value='on'),
    app_commands.Choice(name='⚫ Выключить', value='off'),
    app_commands.Choice(name='📊 Статус', value='status')
])
async def regex_cmd(i: discord.Interaction, attribute: app_commands.Choice[str]):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)
    settings = load_regex_settings()
    gid = str(i.guild_id)
    if attribute.value == 'on':
        settings[gid] = {'enabled': True, 'action': 'mute', 'duration': 60}
        save_regex_settings(settings)
        embed = discord.Embed(title='🛡️ Автомодерация', description='✅ Система **ВКЛЮЧЕНА**\n\n**📝 За маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n**🔨 За рекламу/оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)', color=discord.Color.green())
        embed.set_footer(text="Warden Bot | Защита")
        await i.response.send_message(embed=embed, ephemeral=True)
    elif attribute.value == 'off':
        if gid in settings: settings[gid]['enabled'] = False
        save_regex_settings(settings)
        embed = discord.Embed(title='🛡️ Автомодерация', description='⚫ Система **ВЫКЛЮЧЕНА**', color=discord.Color.red())
        embed.set_footer(text="Warden Bot | Защита")
        await i.response.send_message(embed=embed, ephemeral=True)
    elif attribute.value == 'status':
        is_enabled = settings.get(gid, {}).get('enabled', False)
        status_text = '🔴 **ВКЛЮЧЕНА**' if is_enabled else '⚫ **ВЫКЛЮЧЕНА**'
        embed = discord.Embed(title='🛡️ Статус автомодерации', description=f'{status_text}\n\n**📝 Маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n**🔨 Оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)', color=discord.Color.green() if is_enabled else discord.Color.red())
        embed.set_footer(text="Warden Bot | Защита")
        await i.response.send_message(embed=embed, ephemeral=True)


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
                    audit_reason = f"Автомодерация Warden Bot | Нарушение: '{phrase}' | Автор: {message.author}"
                    await message.author.ban(reason=audit_reason)
                    embed = discord.Embed(title='🔨 ПЕРМАНЕНТНЫЙ БАН', description=f'{message.author.mention} был **НАВСЕГДА ЗАБАНЕН** за сообщение:\n```{message.content[:100]}```\n**Причина:** Оскорбление/реклама сервера', color=discord.Color.red())
                    embed.set_footer(text="Warden Bot • Автомодерация")
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
                    audit_reason = f"Автомодерация Warden Bot | Мат: '{bad_word}' | Автор: {message.author}"
                    await message.author.timeout(until, reason=audit_reason)
                    embed = discord.Embed(title='🛡️ Авто-мут', description=f'{message.author.mention} получил **МУТ на 1 час** за использование мата: `{bad_word}`', color=discord.Color.orange())
                    embed.set_footer(text="Warden Bot • Автомодерация")
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
                if bi.user.id != member.id: return await bi.response.send_message("❌ Not for you!", ephemeral=True)
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
                        if not d: return await mi.response.send_message("❌ Expired!", ephemeral=True)
                        if self.children[0].value == d['code']:
                            g = bot.get_guild(self.gid)
                            if g and (r := g.get_role(self.rid)) and (mo := g.get_member(self.uid)):
                                await mo.add_roles(r)
                                await mi.response.send_message("✅ Verified! Welcome!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                        else:
                            d['attempts'] += 1
                            if d['attempts'] >= 3:
                                if (g := bot.get_guild(self.gid)) and (mo := g.get_member(self.uid)): await mo.kick(reason="Failed captcha")
                                await mi.response.send_message("❌ Kicked for 3 failed attempts!", ephemeral=True)
                                del active_captchas[str(self.uid)]
                            else: await mi.response.send_message(f"❌ Invalid! {3 - d['attempts']} attempts left", ephemeral=True)
                await bi.response.send_modal(Modal(code, member.id, member.guild.id, rid))
        e = discord.Embed(title='🔐 Verification Required', description=f'Welcome to {member.guild.name}!', color=0x3498db)
        e.add_field(name='Code', value=f'||{code}||')
        e.set_footer(text='5 minutes | 3 attempts • Warden Bot')
        try: await member.send(embed=e, view=View())
        except: pass
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
    e = discord.Embed(title='🚪 Member left', description=f'{member.mention} left', color=0xe74c3c, timestamp=datetime.now())
    e.set_footer(text="Warden Bot | Логи")
    await send_log(member.guild.id, e)


@bot.event
async def on_message_delete(msg):
    if msg.author.bot: return
    e = discord.Embed(title='🗑️ Message deleted', description=f'{msg.author.mention} in {msg.channel.mention}', color=0xe74c3c, timestamp=datetime.now())
    e.add_field(name='Content', value=msg.content[:500] if msg.content else '*No text*')
    e.set_footer(text="Warden Bot | Логи")
    await send_log(msg.guild.id, e)


@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    e = discord.Embed(title='✏️ Message edited', description=f'{before.author.mention}', color=0xe67e22, timestamp=datetime.now())
    e.add_field(name='Before', value=before.content[:500] if before.content else '*No text*')
    e.add_field(name='After', value=after.content[:500] if after.content else '*No text*')
    e.set_footer(text="Warden Bot | Логи")
    await send_log(before.guild.id, e)


@bot.tree.command(name='servers', description='Показать список серверов и их владельцев')
async def servers_cmd(i: discord.Interaction):
    if await check_blacklist(i): return
    if await check_tech_work(i): return
    if i.user.id != VIP_USER_ID:
        return await i.response.send_message('❌ Эта команда только для разработчика!', ephemeral=True)
    embed = discord.Embed(title='📊 Список серверов с ботом', color=discord.Color.blue(), timestamp=datetime.now())
    for guild in bot.guilds:
        owner = guild.owner
        is_my = "🔴 **ВАШ**" if owner.id == VIP_USER_ID else ""
        embed.add_field(name=f"{guild.name}", value=f"🆔 ID: `{guild.id}`\n👑 Владелец: {owner.mention if owner else 'Неизвестен'}\n👥 Участников: {guild.member_count}\n{is_my}", inline=False)
    embed.set_footer(text=f'Всего серверов: {len(bot.guilds)} • Warden Bot')
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.command(name='sat')
async def setup_all_ticket(ctx):
    ALLOWED_IDS = [1436760469980450816]
    if ctx.author.id not in ALLOWED_IDS:
        return

    CATEGORY_ID = 1511417385595306024
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
                embed.set_footer(text=f'ID: {name} • Warden Bot')

                class TicketButtons(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=None)

                    @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒',
                                       custom_id=f'ticket_close_{name}')
                    async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not btn_i.user.guild_permissions.administrator and btn_i.user.id != button_interaction.user.id:
                            return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                        await btn_i.response.send_message('🔒 Закрытие тикета...', ephemeral=True)
                        try:
                            await button_interaction.user.send(f'✅ Ваш тикет **{name}** был закрыт.')
                        except:
                            pass
                        await asyncio.sleep(2)
                        await ch.delete()

                    @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅',
                                       custom_id=f'ticket_accept_{name}')
                    async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not btn_i.user.guild_permissions.administrator:
                            return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                        embed.color = discord.Color.green()
                        embed.description = f'**От:** {button_interaction.user.mention}\n**Статус:** ✅ ПРИНЯТ В РАБОТУ'
                        embed.add_field(name='👨‍💻 Принял', value=btn_i.user.mention, inline=False)
                        await btn_i.message.edit(embed=embed, view=self)
                        await btn_i.response.send_message('✅ Тикет принят в работу!', ephemeral=True)
                        try:
                            await button_interaction.user.send(
                                f'✅ Ваш тикет **{name}** принят в работу сотрудником {btn_i.user.mention}')
                        except:
                            pass

                    @discord.ui.button(label='❌ Отклонить', style=discord.ButtonStyle.secondary, emoji='❌',
                                       custom_id=f'ticket_reject_{name}')
                    async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not btn_i.user.guild_permissions.administrator:
                            return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                        embed.color = discord.Color.red()
                        embed.description = f'**От:** {button_interaction.user.mention}\n**Статус:** ❌ ОТКЛОНЁН'
                        embed.add_field(name='👨‍💻 Отклонил', value=btn_i.user.mention, inline=False)
                        await btn_i.message.edit(embed=embed, view=self)
                        await btn_i.response.send_message('❌ Тикет отклонён!', ephemeral=True)
                        try:
                            await button_interaction.user.send(f'❌ Ваш тикет **{name}** был отклонён.')
                        except:
                            pass

                    @discord.ui.button(label='✏️ Ответить', style=discord.ButtonStyle.primary, emoji='✏️',
                                       custom_id=f'ticket_reply_{name}')
                    async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                        if not btn_i.user.guild_permissions.administrator:
                            return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

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
                                embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                                await btn_i.message.edit(embed=embed)
                                await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                                try:
                                    await button_interaction.user.send(
                                        f'📩 Ответ на ваш тикет **{name}** от {modal_i.user.mention}:\n\n{msg}')
                                except:
                                    pass

                        await btn_i.response.send_modal(ReplyModal())

                await ch.send(f'{role.mention if role else ""}', embed=embed, view=TicketButtons())
                await button_interaction.response.send_message(f'✅ Тикет создан: {ch.mention}', ephemeral=True)

        embed_msg = discord.Embed(
            title=titles[ticket_type],
            description=descriptions[ticket_type],
            color=colors[ticket_type]
        )
        embed_msg.set_footer(text="Warden Bot • Тикет-система")
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
    bot.loop.create_task(tech_work_checker())
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
                print(f"\n📢 Установлен на {guild.name} (Сервер Владельца) 👑")
            else:
                print(f"\n📢 Установлен на {guild.name} (Владелец)")
        else:
            print(f"\n📢 Установлен на {guild.name} (Нету Владельца)")
    print("\n" + "=" * 60)
    print(f"📢 Посчитано 99 команд")
    print(f"📢 Бот на {len(bot.guilds)} серверах")
    print("=" * 60 + "\n")


TOKEN = ''
bot.run(TOKEN)
