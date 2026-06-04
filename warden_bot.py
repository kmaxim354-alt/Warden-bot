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
            'help_title': '📚 Помощь - {}',
            'help_desc': 'Выбери категорию в меню ниже, чтобы увидеть список команд.\nИли используй `/help all` для полного списка.',
            'help_cmd_count': '{} команд',
            'help_footer': 'Всего 88 команд | Используй /help <категория>',
            'help_all_title': '📖 Все команды',
            'help_all_desc': 'Полный список всех команд бота:',
            'help_category_title': '{} - Список команд',
            'help_category_desc': 'Всего команд в категории: {}',
            'help_select_placeholder': '📋 Выбери категорию...',
            'help_select_overview': '📚 Обзор',
            'help_select_overview_desc': 'Вернуться к началу',
            'help_select_all': '📖 Все команды',
            'help_select_all_desc': 'Показать все 88 команд',
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
            'settings_saved': '✅ Настройки сохранены',
            'log_channel_set': '✅ Канал логов: {}',
            'report_staff_ticket_setup': '✅ Система жалоб на персонал настроена!',
            'report_staff_title': '⚠️ Жалобы на персонал',
            'report_staff_desc': 'Если вы столкнулись с неправомерными действиями сотрудника сервера, нажмите на кнопку ниже, чтобы подать жалобу.\n\n**Внимание:** Ложные жалобы могут привести к наказанию!',
            'report_staff_button': '📝 Пожаловаться на персонал',
            'report_staff_modal_title': '📝 Жалоба на персонал',
            'report_staff_against': 'На кого жалуетесь?',
            'report_staff_reason': 'Причина жалобы',
            'ticket_no_permission': '❌ Нет прав!',
            'ticket_closing': 'Закрытие тикета...',
            'ticket_closed_dm': '✅ Ваш тикет **{}** был закрыт.',
            'ticket_accepted_dm': '✅ Ваш тикет **{}** принят в работу сотрудником {}',
            'ticket_rejected_dm': '❌ Ваш тикет **{}** был отклонён.',
            'ticket_reply_dm': '📩 Ответ на ваш тикет **{}** от {}:\n\n{}',
            'ticket_close_button': '🔒 Закрыть',
            'ticket_accept_button': '✅ Принять',
            'ticket_reject_button': '❌ Отклонить',
            'ticket_reply_button': '📝 Ответить',
            'ticket_accept_work_button': '✅ Принято в работу',
            'ticket_approve_button': '✅ Одобрено',
            'ticket_approved_dm': '✅ Ваша жалоба была **ПРИНЯТА**. Сотрудник получит наказание.',
            'ticket_rejected_dm_report': '❌ Ваша жалоба была **ОТКЛОНЕНА**. Недостаточно доказательств.',
            'ticket_partnership_accepted_dm': '✅ Ваше предложение сотрудничества было **ПРИНЯТО**! Свяжемся с вами.',
            'ticket_partnership_rejected_dm': '❌ Ваше предложение сотрудничества было **ОТКЛОНЕНО**.',
            'ticket_bug_accepted': '✅ Баг принят в работу!',
            'ticket_idea_approved': '✅ Идея одобрена!',
            'ticket_status_pending': '⏳ Ожидает ответа',
            'ticket_status_accepted': '✅ ПРИНЯТ В РАБОТУ',
            'ticket_status_rejected': '❌ ОТКЛОНЁН',
            'ticket_status_approved': '✅ ОДОБРЕНО',
            'ticket_status_rejected_report': '❌ ОТКЛОНЕНА',
            'ticket_status_bug_accepted': 'Баг подтверждён, в работе',
            'ticket_status_bug_rejected': 'Баг не подтверждён',
            'ticket_status_idea_approved': 'Идея одобрена, добавим в планы',
            'ticket_status_idea_rejected': 'Идея отклонена',
            'report_staff_proof': 'Доказательства',
            'report_staff_submitted': '✅ Жалоба отправлена!',
            'report_staff_embed_title': '⚠️ ЖАЛОБА НА ПЕРСОНАЛ',
            'report_staff_accept': '✅ Принять жалобу',
            'report_staff_reject': '❌ Отклонить жалобу',
            'report_staff_reply': '📝 Ответить с пояснением',
            'report_staff_accept_desc': 'Жалоба принята, сотрудник будет наказан',
            'report_staff_reject_desc': 'Жалоба отклонена (недостаточно доказательств)',
            'partnership_ticket_setup': '✅ Система партнёрства настроена!',
            'partnership_title': '🤝 Сотрудничество',
            'partnership_desc': 'Нажмите на кнопку ниже, чтобы предложить сотрудничество, рекламу или совместные ивенты.',
            'partnership_button': '🤝 Предложить сотрудничество',
            'partnership_modal_title': '🤝 Предложение сотрудничества',
            'partnership_name': 'Название проекта',
            'partnership_type': 'Тип сотрудничества',
            'partnership_description': 'Описание',
            'partnership_contacts': 'Контакты',
            'partnership_submitted': '✅ Предложение отправлено!',
            'partnership_embed_title': '🤝 ПРЕДЛОЖЕНИЕ СОТРУДНИЧЕСТВА',
            'partnership_accept': '✅ Принять',
            'partnership_reject': '❌ Отказать',
            'partnership_reply': '📝 Ответить с пояснением',
            'partnership_accept_desc': 'Предложение ПРИНЯТО',
            'partnership_reject_desc': 'Предложение ОТКЛОНЕНО',
            'bug_accept': '✅ Принято',
            'bug_reject': '❌ Отклонено',
            'bug_reply': '📝 Ответить',
            'bug_accept_desc': 'Баг подтверждён, в работе',
            'bug_reject_desc': 'Баг не подтверждён',
            'idea_approve': '✅ Одобрено',
            'idea_reject': '❌ Отклонено',
            'idea_reply': '📝 Ответить',
            'idea_approve_desc': 'Идея одобрена, добавим в планы',
            'idea_reject_desc': 'Идея отклонена',
            'welcome_configured': '✅ Приветствия настроены в {}',
            'photo_welcome_configured': '✅ Фото-приветствие настроено!',
            'welcome_disabled': '✅ Приветствия отключены',
            'captcha_configured': '✅ Капча настроена с ролью {}',
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
            'ticket_system_setup': '✅ Система тикетов настроена!',
            'ticket_system_title': '🎫 Система тикетов',
            'ticket_system_desc': 'Нажми на кнопку ниже, чтобы создать тикет.\nНаши сотрудники свяжутся с тобой в ближайшее время.',
            'ticket_create_button': '🎫 Создать тикет',
            'ticket_creating': 'Создание тикета...',
            'ticket_created_channel': '✅ Тикет создан: {}',
            'ticket_closed': '✅ Тикет закрыт',
            'ticket_embed_title': '🎫 Тикет создан',
            'ticket_embed_desc': '{}, опишите вашу проблему.\nСотрудники скоро ответят вам.',
            'ticket_dm_closed': '✅ Ваш тикет **{}** был закрыт сотрудником {}.',
            'application_created': '✅ Заявка создана! Кнопка отправлена в канал.',
            'application_no_questions': '❌ Добавь хотя бы 1 вопрос!',
            'application_question_added': '✅ Вопрос добавлен! (Всего: {})',
            'application_button_label': '📝 Подать заявку: {}',
            'application_embed_title': '📝 {}',
            'application_embed_desc': 'Нажми на кнопку ниже, чтобы подать заявку.\nПосле проверки ты получишь роль {}',
            'application_creation_title': '📝 Создание заявки',
            'application_creation_desc': '**Название:** {}\n**Роль:** {}\n**Канал отправки:** {}\n\nНажми на кнопки ниже, чтобы добавить вопросы.',
            'application_add_question_button': '➕ Добавить вопрос',
            'application_finish_button': '✅ Завершить создание',
            'application_submit_button': '📝 Подать заявку: {}',
            'application_modal_title': '📝 {}',
            'application_submitted': '✅ Заявка отправлена! Ожидай решения.',
            'application_new_title': '📥 Новая заявка: {}',
            'application_new_desc': '**От:** {}\n**ID:** {}\n**Статус:** ⏳ Ожидает рассмотрения',
            'application_question_field': '❓ Вопрос {}',
            'application_footer': 'ID заявки: {}',
            'application_approve_button': '✅ Принять',
            'application_reject_button': '❌ Отказать',
            'application_approve_msg_button': '✏️ Принять с сообщением',
            'application_reject_msg_button': '📝 Отказать с сообщением',
            'application_approved': '✅ Заявка одобрена! {} получил роль {}',
            'application_approved_simple': '✅ Заявка одобрена!',
            'application_rejected': '❌ Заявка отклонена!',
            'application_approved_with_msg': '✅ Заявка одобрена с сообщением!',
            'application_rejected_with_msg': '❌ Заявка отклонена с сообщением!',
            'application_status_approved': '✅ ПРИНЯТА',
            'application_status_rejected': '❌ ОТКЛОНЕНА',
            'application_status_approved_msg': '✅ ПРИНЯТА (с сообщением)',
            'application_status_rejected_msg': '❌ ОТКАЗАНО (с сообщением)',
            'application_reviewed_by': '✅ Рассмотрел',
            'application_reviewed_by_reject': '❌ Рассмотрел',
            'application_review_message': '📝 Сообщение',
            'application_reject_reason': '📝 Причина отказа',
            'application_dm_approved': '✅ Ваша заявка **{}** была **ОДОБРЕНА**! Вы получили роль {}',
            'application_dm_rejected': '❌ Ваша заявка **{}** была **ОТКЛОНЕНА**.',
            'application_dm_approved_msg': '✅ Ваша заявка **{}** была **ОДОБРЕНА**! Вы получили роль {}\n\n**Сообщение от администрации:**\n{}',
            'application_dm_rejected_msg': '❌ Ваша заявка **{}** была **ОТКЛОНЕНА**.\n\n**Причина:**\n{}',
            'application_no_permission': '❌ Нет прав!',
            'application_approve_modal_title': '✅ Принять заявку с сообщением',
            'application_approve_modal_label': 'Сообщение пользователю',
            'application_approve_modal_placeholder': 'Напишите сообщение для пользователя...',
            'application_reject_modal_title': '❌ Отказать заявке с сообщением',
            'application_reject_modal_label': 'Причина отказа',
            'bug_ticket_setup': '✅ Система баг-репортов настроена!',
            'bug_title': '🐛 Сообщить об ошибке',
            'bug_desc': 'Нашли ошибку или баг? Нажмите на кнопку ниже, чтобы сообщить разработчикам.\n\n**Спасибо за помощь в улучшении бота!**',
            'bug_button': '🐛 Сообщить об ошибке',
            'bug_modal_title': '🐛 Сообщение об ошибке',
            'bug_summary': 'Краткое описание',
            'bug_description': 'Подробное описание',
            'bug_steps': 'Шаги воспроизведения',
            'bug_expected': 'Ожидаемое поведение',
            'bug_submitted': '✅ Спасибо за сообщение! Баг будет рассмотрен в ближайшее время.',
            'bug_embed_title': '🐛 НОВЫЙ БАГ-РЕПОРТ',
            'bug_embed_footer': 'Пожалуйста, проверьте и исправьте',
            'idea_ticket_setup': '✅ Система предложений идей настроена!',
            'idea_title': '💡 Предложить идею',
            'idea_desc': 'Есть идея по улучшению бота? Нажмите на кнопку ниже и поделитесь своим предложением!\n\n**Лучшие идеи будут реализованы!**',
            'idea_button': '💡 Предложить идею',
            'idea_modal_title': '💡 Предложение идеи',
            'idea_title_field': 'Название идеи',
            'idea_description': 'Описание идеи',
            'idea_benefits': 'Какую пользу принесёт',
            'idea_examples': 'Примеры реализации',
            'idea_submitted': '✅ Спасибо за идею! Мы рассмотрим ваше предложение.',
            'idea_embed_title': '💡 НОВОЕ ПРЕДЛОЖЕНИЕ',
            'idea_embed_footer': 'Рассмотрите и оцените идею',
            'application_reject_modal_placeholder': 'Напишите причину отказа...',
        },
        'en': {
            'hello': 'Hello, {}! I am **Warden Bot** 🤖',
            'ping': '🏓 Pong! Latency: {} ms',
            'info_title': '🛡️ Warden Bot',
            'info_desc': 'The guardian bot for your server',
            'info_version': 'Version',
            'info_cmds': 'Commands',
            'bug_ticket_setup': '✅ Bug report system setup!',
            'bug_title': '🐛 Report a Bug',
            'bug_desc': 'Found a bug? Click the button below to report it to the developers.\n\n**Thank you for helping improve the bot!**',
            'bug_button': '🐛 Report Bug',
            'bug_modal_title': '🐛 Bug Report',
            'bug_summary': 'Summary',
            'bug_description': 'Detailed description',
            'bug_steps': 'Steps to reproduce',
            'bug_expected': 'Expected behavior',
            'bug_submitted': '✅ Thank you for your report! The bug will be reviewed shortly.',
            'bug_embed_title': '🐛 NEW BUG REPORT',
            'bug_embed_footer': 'Please review and fix',
            'idea_ticket_setup': '✅ Idea suggestion system setup!',
            'idea_title': '💡 Suggest an Idea',
            'ticket_no_permission': '❌ No permission!',
            'ticket_closing': 'Closing ticket...',
            'ticket_closed_dm': '✅ Your ticket **{}** has been closed.',
            'ticket_accepted_dm': '✅ Your ticket **{}** has been accepted by {}',
            'ticket_rejected_dm': '❌ Your ticket **{}** has been rejected.',
            'ticket_reply_dm': '📩 Reply to your ticket **{}** from {}:\n\n{}',
            'ticket_close_button': '🔒 Close',
            'ticket_accept_button': '✅ Accept',
            'ticket_reject_button': '❌ Reject',
            'ticket_reply_button': '📝 Reply',
            'ticket_accept_work_button': '✅ Accepted',
            'ticket_approve_button': '✅ Approve',
            'ticket_approved_dm': '✅ Your report has been **ACCEPTED**. The staff member will be punished.',
            'ticket_rejected_dm_report': '❌ Your report has been **REJECTED**. Insufficient evidence.',
            'ticket_partnership_accepted_dm': '✅ Your partnership proposal has been **ACCEPTED**! We will contact you.',
            'ticket_partnership_rejected_dm': '❌ Your partnership proposal has been **REJECTED**.',
            'ticket_bug_accepted': '✅ Bug accepted for work!',
            'ticket_idea_approved': '✅ Idea approved!',
            'ticket_status_pending': '⏳ Pending',
            'ticket_status_accepted': '✅ ACCEPTED',
            'ticket_status_rejected': '❌ REJECTED',
            'ticket_status_approved': '✅ APPROVED',
            'ticket_status_rejected_report': '❌ REJECTED',
            'ticket_status_bug_accepted': 'Bug confirmed, in progress',
            'ticket_status_bug_rejected': 'Bug not confirmed',
            'ticket_status_idea_approved': 'Idea approved, will be added to plans',
            'ticket_status_idea_rejected': 'Idea rejected',
            'report_staff_ticket_setup': '✅ Staff report system setup!',
            'report_staff_title': '⚠️ Report Staff',
            'report_staff_desc': 'Click the button below to report a staff member.\n\n**False reports will be punished!**',
            'report_staff_button': '⚠️ Report Staff',
            'report_staff_modal_title': '⚠️ Staff Report',
            'report_staff_against': 'Who are you reporting?',
            'report_staff_reason': 'Reason',
            'report_staff_proof': 'Evidence',
            'report_staff_submitted': '✅ Report submitted!',
            'report_staff_embed_title': '⚠️ STAFF REPORT',
            'report_staff_accept': '✅ Accept report',
            'report_staff_reject': '❌ Reject report',
            'report_staff_reply': '📝 Reply with explanation',
            'report_staff_accept_desc': 'Report accepted, staff will be punished',
            'report_staff_reject_desc': 'Report rejected (insufficient evidence)',
            'partnership_ticket_setup': '✅ Partnership system setup!',
            'partnership_title': '🤝 Partnership',
            'partnership_desc': 'Click the button below to propose partnership, advertising, or joint events.',
            'partnership_button': '🤝 Propose Partnership',
            'partnership_modal_title': '🤝 Partnership Proposal',
            'partnership_name': 'Project Name',
            'partnership_type': 'Partnership Type',
            'partnership_description': 'Description',
            'partnership_contacts': 'Contacts',
            'partnership_submitted': '✅ Proposal submitted!',
            'partnership_embed_title': '🤝 PARTNERSHIP PROPOSAL',
            'partnership_accept': '✅ Accept',
            'partnership_reject': '❌ Reject',
            'partnership_reply': '📝 Reply with explanation',
            'partnership_accept_desc': 'Proposal ACCEPTED',
            'partnership_reject_desc': 'Proposal REJECTED',
            'bug_accept': '✅ Accepted',
            'bug_reject': '❌ Rejected',
            'bug_reply': '📝 Reply',
            'bug_accept_desc': 'Bug confirmed, in progress',
            'bug_reject_desc': 'Bug not confirmed',
            'idea_desc': 'Have an idea to improve the bot? Click the button below and share!',
            'idea_button': '💡 Suggest Idea',
            'idea_modal_title': '💡 Idea for Bot',
            'idea_name': 'Idea title',
            'idea_description': 'Description',
            'idea_benefits': 'Why is this useful?',
            'idea_submitted': '✅ Idea submitted! Thanks for your suggestion!',
            'idea_embed_title': '💡 NEW IDEA',
            'idea_approve': '✅ Approve',
            'idea_reject': '❌ Reject',
            'idea_reply': '📝 Reply',
            'idea_approve_desc': 'Idea approved, will be added to plans',
            'idea_reject_desc': 'Idea rejected',
            'idea_embed_footer': 'Review and evaluate the idea',
            'info_footer': 'Always keeping order 🔒',
            'no_permission': '❌ No permission!',
            'need_admin': '❌ Need admin permissions!',
            'error': '❌ Error: {}',
            'sent': '✅ Sent to {}',
            'no_roles': '❌ No roles specified!',
            'settings_saved': '✅ Settings saved',
            'help_title': '📚 Help - {}',
            'help_desc': 'Select a category from the menu below to see the command list.\nOr use `/help all` for full list.',
            'help_cmd_count': '{} commands',
            'help_footer': 'Total 88 commands | Use /help <category>',
            'help_all_title': '📖 All Commands',
            'help_all_desc': 'Full list of all bot commands:',
            'help_category_title': '{} - Command List',
            'help_category_desc': 'Total commands in category: {}',
            'help_select_placeholder': '📋 Choose a category...',
            'help_select_overview': '📚 Overview',
            'help_select_overview_desc': 'Back to start',
            'help_select_all': '📖 All Commands',
            'help_select_all_desc': 'Show all 88 commands',
            'help_select_mod_desc': '28 commands',
            'help_select_roles_desc': '8 commands',
            'help_select_voice_desc': '5 commands',
            'help_select_info_desc': '9 commands',
            'help_select_level_desc': '6 commands',
            'help_select_util_desc': '10 commands',
            'help_select_fun_desc': '10 commands',
            'help_select_setup_desc': '13 commands',
            'help_select_misc_desc': '2 commands',
            'report_staff_embed_footer': 'Please review this report',
            'ticket_system_setup': '✅ Ticket system setup!',
            'ticket_system_title': '🎫 Ticket System',
            'ticket_system_desc': 'Click the button below to create a ticket.\nOur staff will contact you shortly.',
            'ticket_create_button': '🎫 Create Ticket',
            'ticket_creating': 'Creating ticket...',
            'ticket_created_channel': '✅ Ticket created: {}',
            'ticket_closed': '✅ Ticket closed',
            'ticket_embed_title': '🎫 Ticket Created',
            'ticket_embed_desc': '{}, describe your issue.\nStaff will respond shortly.',
            'ticket_dm_closed': '✅ Your ticket **{}** was closed by staff member {}.',
            'partnership_server_name': 'Server/Project Name',
            'partnership_links': 'Links (server, social media)',
            'log_channel_set': '✅ Log channel: {}',
            'welcome_configured': '✅ Welcome configured in {}',
            'photo_welcome_configured': '✅ Photo welcome configured!',
            'welcome_disabled': '✅ Welcome disabled',
            'captcha_configured': '✅ Captcha configured with role {}',
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


@bot.tree.command(name='help', description='Все команды бота с категориями')
async def help_command(i: discord.Interaction, category: str = None):
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


@bot.tree.command(name='mute', description='Заглушить участника')
async def mute(i: discord.Interaction, user: discord.Member, minutes: int, rule: str, reason: str = "Не указана"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    if minutes <= 0:
        return await i.response.send_message('❌ Время должно быть больше 0!', ephemeral=True)

    if minutes > 40320:
        return await i.response.send_message('❌ Максимум 28 дней (40320 минут)!', ephemeral=True)

    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await user.timeout(until, reason=f'Правило: {rule} | Причина: {reason}')

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

    embed = discord.Embed(
        title='🔇 Мут',
        description=f'{user.mention} получил мут на **{time_text}**',
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name='📋 Правило', value=rule, inline=False)
    embed.add_field(name='📝 Причина', value=reason, inline=False)
    embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id}')

    await i.response.send_message(embed=embed, ephemeral=False)

    await send_log(i.guild_id, embed)


@bot.tree.command(name='unmute', description='Unmute a member')
async def unmute(i: discord.Interaction, member: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.moderate_members:
        return await i.response.send_message(get_text(str(i.guild_id), 'no_permission'), ephemeral=True)
    if member.timed_out_until is None:
        return await i.response.send_message(get_text(str(i.guild_id), 'not_muted'), ephemeral=True)
    await member.timeout(None)
    await i.response.send_message(get_text(str(i.guild_id), 'unmuted', member.mention), ephemeral=True)


@bot.tree.command(name='setup-bugsticket', description='🐛 Настроить систему баг-репортов')
async def setup_bugsticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    class BugView(discord.ui.View):
        @discord.ui.button(label='🐛 Сообщить об ошибке', style=discord.ButtonStyle.danger, emoji='🐛')
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            name = f'bug-{bi.user.name.lower()}-{random.randint(100, 999)}'
            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            ch = await bi.guild.create_text_channel(name, category=category, overwrites=ow)

            class BugModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title='🐛 Сообщение об ошибке')
                    self.add_item(discord.ui.TextInput(label='Краткое описание', required=True))
                    self.add_item(discord.ui.TextInput(label='Подробное описание', style=discord.TextStyle.paragraph,
                                                       required=True))
                    self.add_item(discord.ui.TextInput(label='Шаги воспроизведения', style=discord.TextStyle.paragraph,
                                                       required=True))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title='🐛 БАГ-РЕПОРТ',
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='📌 Кратко', value=self.children[0].value, inline=False)
                    embed.add_field(name='📝 Подробно', value=self.children[1].value, inline=False)
                    embed.add_field(name='🔁 Шаги', value=self.children[2].value, inline=False)

                    class BugButtons(discord.ui.View):
                        @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            await btn_i.response.send_message('Закрытие...', ephemeral=True)
                            await asyncio.sleep(2)
                            await ch.delete()

                        @discord.ui.button(label='✅ Принято', style=discord.ButtonStyle.success, emoji='✅')
                        async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.green()
                            embed.add_field(name='✅ Статус', value='Баг подтверждён, в работе', inline=False)
                            embed.add_field(name='👨‍💻 Принял', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('✅ Баг принят в работу!', ephemeral=True)

                        @discord.ui.button(label='❌ Отклонено', style=discord.ButtonStyle.secondary, emoji='❌')
                        async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.red()
                            embed.add_field(name='❌ Статус', value='Баг не подтверждён', inline=False)
                            embed.add_field(name='👨‍💻 Отклонил', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('❌ Баг отклонён!', ephemeral=True)

                        @discord.ui.button(label='📝 Ответить', style=discord.ButtonStyle.primary, emoji='📝')
                        async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                            class ReplyModal(discord.ui.Modal):
                                def __init__(self):
                                    super().__init__(title='Ответ пользователю')
                                    self.add_item(
                                        discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                             required=True))

                                async def on_submit(self, modal_i: discord.Interaction):
                                    msg = self.children[0].value
                                    embed.add_field(name='📝 Ответ разработчика', value=msg, inline=False)
                                    embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed)
                                    await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)

                            await btn_i.response.send_modal(ReplyModal())

                    await ch.send(f'{support_role.mention}', embed=embed, view=BugButtons())
                    await modal_i.response.send_message('✅ Баг-репорт отправлен!', ephemeral=True)

            await bi.response.send_modal(BugModal())

    embed = discord.Embed(
        title='🐛 Сообщить об ошибке',
        description='Нашли баг? Нажмите на кнопку ниже и сообщите разработчикам.',
        color=discord.Color.red()
    )
    await i.channel.send(embed=embed, view=BugView())
    await i.response.send_message('✅ Система баг-репортов настроена!', ephemeral=True)


@bot.tree.command(name='setup-ideaticket', description='💡 Настроить систему предложений идей')
async def setup_ideaticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    class IdeaView(discord.ui.View):
        @discord.ui.button(label='💡 Предложить идею', style=discord.ButtonStyle.success, emoji='💡')
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            name = f'idea-{bi.user.name.lower()}-{random.randint(100, 999)}'
            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            ch = await bi.guild.create_text_channel(name, category=category, overwrites=ow)

            class IdeaModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title='💡 Идея для бота')
                    self.add_item(discord.ui.TextInput(label='Название идеи', required=True))
                    self.add_item(
                        discord.ui.TextInput(label='Описание', style=discord.TextStyle.paragraph, required=True))
                    self.add_item(discord.ui.TextInput(label='Почему это полезно?', style=discord.TextStyle.paragraph,
                                                       required=False))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title='💡 НОВАЯ ИДЕЯ',
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='💡 Название', value=self.children[0].value, inline=False)
                    embed.add_field(name='📝 Описание', value=self.children[1].value, inline=False)
                    if self.children[2].value:
                        embed.add_field(name='⭐ Польза', value=self.children[2].value, inline=False)

                    class IdeaButtons(discord.ui.View):
                        @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            await btn_i.response.send_message('Закрытие...', ephemeral=True)
                            await asyncio.sleep(2)
                            await ch.delete()

                        @discord.ui.button(label='✅ Одобрено', style=discord.ButtonStyle.success, emoji='✅')
                        async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.green()
                            embed.add_field(name='✅ Статус', value='Идея одобрена, добавим в планы', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('✅ Идея одобрена!', ephemeral=True)

                        @discord.ui.button(label='❌ Отклонено', style=discord.ButtonStyle.secondary, emoji='❌')
                        async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.red()
                            embed.add_field(name='❌ Статус', value='Идея отклонена', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('❌ Идея отклонена!', ephemeral=True)

                        @discord.ui.button(label='📝 Ответить', style=discord.ButtonStyle.primary, emoji='📝')
                        async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                            class ReplyModal(discord.ui.Modal):
                                def __init__(self):
                                    super().__init__(title='Ответ пользователю')
                                    self.add_item(
                                        discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                             required=True))

                                async def on_submit(self, modal_i: discord.Interaction):
                                    msg = self.children[0].value
                                    embed.add_field(name='📝 Ответ', value=msg, inline=False)
                                    embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed)
                                    await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)

                            await btn_i.response.send_modal(ReplyModal())

                    await ch.send(f'{support_role.mention}', embed=embed, view=IdeaButtons())
                    await modal_i.response.send_message('✅ Идея отправлена! Спасибо за предложение!', ephemeral=True)

            await bi.response.send_modal(IdeaModal())

    embed = discord.Embed(
        title='💡 Предложить идею',
        description='Есть идея по улучшению бота? Нажмите на кнопку ниже и поделитесь!',
        color=discord.Color.green()
    )
    await i.channel.send(embed=embed, view=IdeaView())
    await i.response.send_message('✅ Система предложений идей настроена!', ephemeral=True)


@bot.tree.command(name='ban', description='Забанить участника')
async def ban(i: discord.Interaction, user: discord.Member, rule: str, reason: str = "Не указана"):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.ban_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    if user.top_role >= i.user.top_role and i.user.id != i.guild.owner_id:
        return await i.response.send_message('❌ Нельзя забанить пользователя с ролью выше или равной вашей!',
                                             ephemeral=True)

    await user.ban(reason=f'Правило: {rule} | Причина: {reason}')

    embed = discord.Embed(
        title='🔨 Бан',
        description=f'{user.mention} был забанен',
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    embed.add_field(name='📋 Правило', value=rule, inline=False)
    embed.add_field(name='📝 Причина', value=reason, inline=False)
    embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id}')

    await i.response.send_message(embed=embed, ephemeral=False)
    await send_log(i.guild_id, embed)

    try:
        await user.send(f'🔨 Вы были забанены на сервере **{i.guild.name}**\n📋 Правило: {rule}\n📝 Причина: {reason}')
    except:
        pass


@bot.tree.command(name='unban', description='Разбанить пользователя по ID')
async def unban(i: discord.Interaction, userid: str, reason: str = "Не указана"):
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

        embed = discord.Embed(
            title='🔓 Разбан',
            description=f'{user.mention} был разбанен',
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name='📝 Причина', value=reason, inline=False)
        embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
        embed.set_footer(text=f'ID: {user.id}')

        await i.response.send_message(embed=embed, ephemeral=False)
        await send_log(i.guild_id, embed)

    except ValueError:
        await i.response.send_message('❌ Неверный формат ID!', ephemeral=True)
    except discord.NotFound:
        await i.response.send_message(f'❌ Пользователь с ID `{userid}` не найден!', ephemeral=True)
    except Exception as e:
        await i.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


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


@bot.tree.command(name='vmute', description='Заглушить в голосовом канале')
async def vmute(i: discord.Interaction, user: discord.Member):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.mute_members:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    if not user.voice:
        return await i.response.send_message(f'❌ {user.mention} не в голосовом канале!', ephemeral=True)

    await user.edit(mute=True)

    embed = discord.Embed(
        title='🔇 Голосовой мут',
        description=f'{user.mention} заглушен в голосовом канале',
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name='👮 Модератор', value=i.user.mention, inline=False)
    embed.set_footer(text=f'ID: {user.id}')

    await i.response.send_message(embed=embed, ephemeral=False)
    await send_log(i.guild_id, embed)


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

    await i.response.send_message(get_text(str(i.guild_id), 'log_channel_set', channel.mention), ephemeral=True)


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

    await i.response.send_message(get_text(str(i.guild_id), 'captcha_configured', role.mention), ephemeral=True)


APPLICATIONS_FILE = 'applications.json'


def load_applications():
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_applications(apps):
    with open(APPLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(apps, f, indent=4, ensure_ascii=False)


REGEX_SETTINGS_FILE = 'regex_settings.json'


def load_regex_settings():
    if os.path.exists(REGEX_SETTINGS_FILE):
        with open(REGEX_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_regex_settings(settings):
    with open(REGEX_SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)


BAD_WORDS_RU = [
    'хуй', 'пизда', 'бля', 'залупа', 'ебать', 'ебаный', 'нахуй', 'охуел',
    'хуесос', 'гандон', 'мудак', 'ублюдок', 'сука', 'блять', 'пиздец',
    'хер', 'долбоеб', 'пидор', 'пидарас', 'шлюха', 'курва', 'блядина',
    'ебучий', 'заебать', 'отъебись', 'подъеб', 'срака', 'жопа', 'пердеж'
]

BAD_WORDS_EN = [
    'fuck', 'shit', 'bitch', 'asshole', 'bastard', 'dick', 'pussy', 'cunt',
    'motherfucker', 'faggot', 'whore', 'slut', 'damn', 'hell', 'cock',
    'suck', 'ass', 'dumbass', 'douche', 'prick', 'crap', 'bullshit'
]

PERMANENT_BAN_PHRASES = [
    'ваш сервер', 'твой сервер', 'свой сервер', 'его сервер', 'их сервер',
    'ваша гильдия', 'твоя гильдия', 'своя гильдия',
    'ваш дискорд', 'твой дискорд', 'свой дискорд',
    'реклама сервера', 'чужой сервер', 'другой сервер',
    'забери свой сервер', 'иди на свой сервер', 'вали на свой сервер',
    'создай свой сервер', 'сделай свой сервер', 'открой свой сервер',
    'свой дискорд сервер', 'свой дс сервер', 'свой дс',
    'ебаный сервер', 'хуевый сервер', 'гнилой сервер',
    'ты сам создай сервер', 'ты сам сделай сервер',
    'ваш сервер говно', 'твой сервер говно', 'это сервер говно',
    'server sucks', 'your server sucks', 'his server sucks',
    'bad server', 'shitty server', 'garbage server'
]

ALL_BAD_WORDS = BAD_WORDS_RU + BAD_WORDS_EN


@bot.tree.command(name='regex', description='Включить/выключить авто-мут/бан за нарушения')
@app_commands.choices(attribute=[
    app_commands.Choice(name='🔴 Включить', value='on'),
    app_commands.Choice(name='⚫ Выключить', value='off'),
    app_commands.Choice(name='📊 Статус', value='status')
])
async def regex_cmd(i: discord.Interaction, attribute: app_commands.Choice[str]):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    settings = load_regex_settings()
    gid = str(i.guild_id)

    if attribute.value == 'on':
        settings[gid] = {'enabled': True, 'action': 'mute', 'duration': 60}
        save_regex_settings(settings)
        embed = discord.Embed(
            title='🛡️ Автомодерация',
            description='✅ Система **ВКЛЮЧЕНА**\n\n'
                        f'**📝 За маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n'
                        f'**🔨 За рекламу/оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)',
            color=discord.Color.green()
        )
        await i.response.send_message(embed=embed, ephemeral=True)

    elif attribute.value == 'off':
        if gid in settings:
            settings[gid]['enabled'] = False
            save_regex_settings(settings)
        embed = discord.Embed(
            title='🛡️ Автомодерация',
            description='⚫ Система **ВЫКЛЮЧЕНА**',
            color=discord.Color.red()
        )
        await i.response.send_message(embed=embed, ephemeral=True)

    elif attribute.value == 'status':
        is_enabled = settings.get(gid, {}).get('enabled', False)
        status_text = '🔴 **ВКЛЮЧЕНА**' if is_enabled else '⚫ **ВЫКЛЮЧЕНА**'
        embed = discord.Embed(
            title='🛡️ Статус автомодерации',
            description=f'{status_text}\n\n'
                        f'**📝 Маты:** Мут на 1 час ({len(ALL_BAD_WORDS)} слов)\n'
                        f'**🔨 Оскорбление сервера:** Перманентный бан ({len(PERMANENT_BAN_PHRASES)} фраз)',
            color=discord.Color.green() if is_enabled else discord.Color.red()
        )
        await i.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_message(message):
    if message.author.bot:
        return await bot.process_commands(message)

    if not message.guild:
        return await bot.process_commands(message)

    settings = load_regex_settings()
    gid = str(message.guild.id)

    if settings.get(gid, {}).get('enabled', False):
        content_lower = message.content.lower()

        for phrase in PERMANENT_BAN_PHRASES:
            if phrase in content_lower:
                try:
                    await message.delete()

                    await message.author.ban(reason=f'Авто-бан: оскорбление/реклама сервера (фраза: "{phrase}")')

                    embed = discord.Embed(
                        title='🔨 ПЕРМАНЕНТНЫЙ БАН',
                        description=f'{message.author.mention} был **НАВСЕГДА ЗАБАНЕН** за сообщение:\n```{message.content[:100]}```\n**Причина:** Оскорбление/реклама сервера',
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)

                    try:
                        await message.author.send(
                            f'🔨 Вы получили **ПЕРМАНЕНТНЫЙ БАН** на сервере **{message.guild.name}** за сообщение: "{message.content[:100]}"')
                    except:
                        pass

                except Exception as e:
                    print(f'Ошибка при бане: {e}')

                return await bot.process_commands(message)

        for bad_word in ALL_BAD_WORDS:
            if bad_word in content_lower:
                try:
                    await message.delete()

                    until = discord.utils.utcnow() + timedelta(hours=1)
                    await message.author.timeout(until, reason=f'Авто-мут: использование мата "{bad_word}"')

                    embed = discord.Embed(
                        title='🛡️ Авто-мут',
                        description=f'{message.author.mention} получил **МУТ на 1 час** за использование мата: `{bad_word}`',
                        color=discord.Color.orange()
                    )
                    await message.channel.send(embed=embed, delete_after=10)

                    try:
                        await message.author.send(
                            f'⏰ Вы получили мут на 1 час на сервере **{message.guild.name}** за использование мата: `{bad_word}`')
                    except:
                        pass

                except Exception as e:
                    print(f'Ошибка при выдаче мута: {e}')

                break

    await bot.process_commands(message)


@bot.tree.command(name='create-application', description='Создать заявку с вопросами до 8 вопросов')
async def create_application(i: discord.Interaction, название: str, роль: discord.Role, канал: discord.TextChannel):
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

        @discord.ui.button(label='Добавить вопрос', style=discord.ButtonStyle.primary)
        async def add_question(self, btn_i: discord.Interaction, button: discord.ui.Button):
            modal = AddQuestionModal(app_id, название, роль, gid, i.channel.id)
            await btn_i.response.send_modal(modal)

        @discord.ui.button(label='Завершить создание', style=discord.ButtonStyle.success)
        async def finish(self, btn_i: discord.Interaction, button: discord.ui.Button):
            apps_check = load_applications()
            questions = apps_check.get(gid, {}).get(str(app_id), {}).get('questions', [])
            if len(questions) < 1:
                return await btn_i.response.send_message('Добавь хотя бы 1 вопрос!', ephemeral=True)
            if len(questions) > 8:
                return await btn_i.response.send_message('Максимум 8 вопросов!', ephemeral=True)

            class ApplicationMenu(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label=f'Подать заявку: {название[:35]}', style=discord.ButtonStyle.primary)
                async def apply(self, apply_i: discord.Interaction, button: discord.ui.Button):
                    await apply_i.response.send_modal(ApplicationModal(app_id, gid, канал.id, page=0))

            embed = discord.Embed(
                title=f'Заявка: {название}',
                description=f'Нажми на кнопку ниже, чтобы подать заявку.\nПосле проверки ты получишь роль {роль.mention}\n\nВсего вопросов: {len(questions)}',
                color=discord.Color.blue()
            )
            await i.channel.send(embed=embed, view=ApplicationMenu())
            await btn_i.response.send_message('Заявка создана! Кнопка отправлена в канал.', ephemeral=True)
            self.stop()

    class AddQuestionModal(discord.ui.Modal):
        def __init__(self, app_id, app_name, role, gid, channel_id):
            self.app_id = app_id
            self.app_name = app_name
            self.role = role
            self.gid = gid
            self.channel_id = channel_id
            super().__init__(title='Добавить вопрос')
            self.add_item(discord.ui.TextInput(label='Вопрос', style=discord.TextStyle.paragraph,
                                               placeholder='Напиши вопрос для заявки...'))

        async def on_submit(self, modal_i: discord.Interaction):
            question = self.children[0].value
            apps = load_applications()

            if self.gid not in apps:
                apps[self.gid] = {}
            if str(self.app_id) not in apps[self.gid]:
                apps[self.gid][str(self.app_id)] = {'questions': []}

            current_questions = apps[self.gid][str(self.app_id)].get('questions', [])
            if len(current_questions) >= 8:
                return await modal_i.response.send_message('Максимум 8 вопросов!', ephemeral=True)

            apps[self.gid][str(self.app_id)]['questions'].append(question)
            save_applications(apps)

            total = len(apps[self.gid][str(self.app_id)]['questions'])
            await modal_i.response.send_message(f'Вопрос добавлен! (Всего: {total}/8)', ephemeral=True)

    embed = discord.Embed(
        title='Создание заявки',
        description=f'**Название:** {название}\n**Роль:** {роль.mention}\n**Канал отправки:** {канал.mention}\n\nНажми на кнопки ниже, чтобы добавить вопросы.\n**Максимум 8 вопросов** (по 4 на страницу)',
        color=discord.Color.green()
    )
    await i.response.send_message(embed=embed, view=AddQuestionView(), ephemeral=True)


class ApplicationModal(discord.ui.Modal):
    def __init__(self, app_id, guild_id, send_channel_id, page=0):
        title = f'Заявка - Страница {page + 1}'
        if len(title) > 45:
            title = f'Стр.{page + 1}'
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
            self.add_item(discord.ui.TextInput(
                label=label,
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=1000
            ))

    async def on_submit(self, interaction: discord.Interaction):
        if not hasattr(interaction.client, 'application_answers'):
            interaction.client.application_answers = {}

        user_key = f"{self.guild_id}_{self.app_id}_{interaction.user.id}"
        if user_key not in interaction.client.application_answers:
            interaction.client.application_answers[user_key] = {}

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
        if not send_channel:
            send_channel = interaction.channel

        answers_list = []
        for i, q in enumerate(self.questions):
            answers_list.append({'question': q, 'answer': answers.get(i, '')})

        all_apps = load_applications()
        if 'submissions' not in all_apps:
            all_apps['submissions'] = {}

        submission_id = f"{self.guild_id}_{self.app_id}_{interaction.user.id}_{int(datetime.now().timestamp())}"
        all_apps['submissions'][submission_id] = {
            'guild_id': self.guild_id,
            'app_id': self.app_id,
            'user_id': interaction.user.id,
            'user_name': str(interaction.user),
            'answers': answers_list,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        save_applications(all_apps)

        embed = discord.Embed(
            title=f'Новая заявка: {app_name}',
            description=f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** Ожидает рассмотрения',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for i, ans in enumerate(answers_list, 1):
            embed.add_field(name=f'Вопрос {i}', value=f'**{ans["question"][:50]}**\n{ans["answer"][:500]}',
                            inline=False)

        embed.set_footer(text=f'ID заявки: {submission_id}')

        class ReviewView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=86400)

            @discord.ui.button(label='Принять', style=discord.ButtonStyle.success, emoji='✅')
            async def approve(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('Нет прав!', ephemeral=True)

                all_apps = load_applications()
                if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                    all_apps['submissions'][submission_id]['status'] = 'approved'
                    all_apps['submissions'][submission_id]['reviewed_by'] = btn_i.user.id
                    all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                    save_applications(all_apps)

                if role:
                    await interaction.user.add_roles(role)
                    await btn_i.response.send_message(
                        f'Заявка одобрена! {interaction.user.mention} получил роль {role.mention}', ephemeral=True)
                else:
                    await btn_i.response.send_message('Заявка одобрена!', ephemeral=True)

                embed.color = discord.Color.green()
                embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ПРИНЯТА'
                embed.add_field(name='Рассмотрел', value=btn_i.user.mention, inline=False)
                await btn_i.message.edit(embed=embed, view=None)

                try:
                    await interaction.user.send(
                        f'Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}')
                except:
                    pass

            @discord.ui.button(label='Отказать', style=discord.ButtonStyle.danger, emoji='❌')
            async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('Нет прав!', ephemeral=True)

                all_apps = load_applications()
                if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                    all_apps['submissions'][submission_id]['status'] = 'rejected'
                    all_apps['submissions'][submission_id]['reviewed_by'] = btn_i.user.id
                    all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                    save_applications(all_apps)

                await btn_i.response.send_message('Заявка отклонена!', ephemeral=True)

                embed.color = discord.Color.red()
                embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ОТКЛОНЕНА'
                embed.add_field(name='Рассмотрел', value=btn_i.user.mention, inline=False)
                await btn_i.message.edit(embed=embed, view=None)

                try:
                    await interaction.user.send(f'Ваша заявка **{app_name}** была ОТКЛОНЕНА.')
                except:
                    pass

            @discord.ui.button(label='Принять с сообщением', style=discord.ButtonStyle.primary, emoji='✏️')
            async def approve_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('Нет прав!', ephemeral=True)

                class ApproveMessageModal(discord.ui.Modal):
                    def __init__(self):
                        super().__init__(title='Принять заявку')
                        self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                           placeholder='Сообщение пользователю...', required=True))

                    async def on_submit(self, modal_i: discord.Interaction):
                        message_text = self.children[0].value

                        all_apps = load_applications()
                        if 'submissions' in all_apps and submission_id in all_apps['submissions']:
                            all_apps['submissions'][submission_id]['status'] = 'approved_with_message'
                            all_apps['submissions'][submission_id]['reviewed_by'] = modal_i.user.id
                            all_apps['submissions'][submission_id]['review_message'] = message_text
                            all_apps['submissions'][submission_id]['reviewed_at'] = datetime.now().isoformat()
                            save_applications(all_apps)

                        if role:
                            await interaction.user.add_roles(role)

                        embed.color = discord.Color.green()
                        embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ПРИНЯТА (с сообщением)'
                        embed.add_field(name='Рассмотрел', value=modal_i.user.mention, inline=False)
                        embed.add_field(name='Сообщение', value=message_text[:500], inline=False)
                        await btn_i.message.edit(embed=embed, view=None)

                        await modal_i.response.send_message('Заявка одобрена с сообщением!', ephemeral=True)

                        try:
                            await interaction.user.send(
                                f'Ваша заявка **{app_name}** была ОДОБРЕНА! Вы получили роль {role.mention if role else ""}\n\n**Сообщение:**\n{message_text}')
                        except:
                            pass

                await btn_i.response.send_modal(ApproveMessageModal())

            @discord.ui.button(label='Отказать с сообщением', style=discord.ButtonStyle.secondary, emoji='📝')
            async def reject_with_message(self, btn_i: discord.Interaction, button: discord.ui.Button):
                if not btn_i.user.guild_permissions.administrator:
                    return await btn_i.response.send_message('Нет прав!', ephemeral=True)

                class RejectMessageModal(discord.ui.Modal):
                    def __init__(self):
                        super().__init__(title='Отказать заявке')
                        self.add_item(discord.ui.TextInput(label='Причина', style=discord.TextStyle.paragraph,
                                                           placeholder='Причина отказа...', required=True))

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
                        embed.description = f'**От:** {interaction.user.mention}\n**ID:** {interaction.user.id}\n**Статус:** ОТКАЗАНО (с сообщением)'
                        embed.add_field(name='Рассмотрел', value=modal_i.user.mention, inline=False)
                        embed.add_field(name='Причина', value=message_text[:500], inline=False)
                        await btn_i.message.edit(embed=embed, view=None)

                        await modal_i.response.send_message('Заявка отклонена с сообщением!', ephemeral=True)

                        try:
                            await interaction.user.send(
                                f'Ваша заявка **{app_name}** была ОТКЛОНЕНА.\n\n**Причина:**\n{message_text}')
                        except:
                            pass

                await btn_i.response.send_modal(RejectMessageModal())

        await send_channel.send(embed=embed, view=ReviewView())
        await interaction.response.send_message('Заявка отправлена! Ожидай решения.', ephemeral=True)


@bot.tree.command(name='massunban', description='Разбан всех пользователей на сервере')
async def massunban(i: discord.Interaction, reason: str = "Массовый разбан"):
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

    embed = discord.Embed(
        title='🔓 Массовый разбан',
        color=discord.Color.green() if not failed else discord.Color.orange(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name='✅ Успешно разбанены',
        value=f'**{len(success)}** из **{len(banned_users)}** пользователей',
        inline=False
    )

    if success:
        embed.add_field(
            name='📋 Список разбаненных',
            value='\n'.join(success[:15]) + ('\n...' if len(success) > 15 else ''),
            inline=False
        )

    if failed:
        embed.add_field(
            name='❌ Ошибки',
            value='\n'.join(failed[:10]),
            inline=False
        )

    embed.set_footer(text=f'Запросил: {i.user.name}')

    await i.edit_original_response(content=None, embed=embed)


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
            embed.set_footer(text=f'ID: {name}')

            class TicketButtons(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=None)

                @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                    if not btn_i.user.guild_permissions.administrator and btn_i.user.id != bi.user.id:
                        return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                    await btn_i.response.send_message('Закрытие тикета...', ephemeral=True)
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
                            super().__init__(title='Ответ пользователю')
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
    await i.channel.send(embed=embed, view=TicketView())
    await i.response.send_message('✅ Система тикетов настроена!', ephemeral=True)


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


@bot.tree.command(name='setup-reportstaffticket', description='⚠️ Настроить систему жалоб на персонал')
async def setup_reportstaffticket(i: discord.Interaction, category: discord.CategoryChannel, support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    class ReportStaffView(discord.ui.View):
        @discord.ui.button(label='⚠️ Пожаловаться на персонал', style=discord.ButtonStyle.danger, emoji='⚠️')
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            name = f'report-{bi.user.name.lower()}-{random.randint(100, 999)}'
            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            ch = await bi.guild.create_text_channel(name, category=category, overwrites=ow)

            class ReportModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title='⚠️ Жалоба на персонал')
                    self.add_item(discord.ui.TextInput(label='На кого жалуетесь?', placeholder='Ник или ID', required=True))
                    self.add_item(discord.ui.TextInput(label='Причина', placeholder='Опишите ситуацию', required=True, style=discord.TextStyle.paragraph))
                    self.add_item(discord.ui.TextInput(label='Доказательства', placeholder='Ссылки на скриншоты', required=False))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title='⚠️ ЖАЛОБА НА ПЕРСОНАЛ',
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.red(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='👤 На кого', value=self.children[0].value, inline=False)
                    embed.add_field(name='📋 Причина', value=self.children[1].value, inline=False)
                    if self.children[2].value:
                        embed.add_field(name='🔗 Доказательства', value=self.children[2].value, inline=False)

                    class ReportButtons(discord.ui.View):
                        @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            await btn_i.response.send_message('Закрытие...', ephemeral=True)
                            await asyncio.sleep(2)
                            await ch.delete()

                        @discord.ui.button(label='✅ Принять жалобу', style=discord.ButtonStyle.success, emoji='✅')
                        async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.green()
                            embed.add_field(name='✅ Решение', value='Жалоба принята, сотрудник будет наказан', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('✅ Жалоба принята!', ephemeral=True)
                            try:
                                await modal_i.user.send('✅ Ваша жалоба была **ПРИНЯТА**. Сотрудник получит наказание.')
                            except:
                                pass

                        @discord.ui.button(label='❌ Отклонить жалобу', style=discord.ButtonStyle.secondary, emoji='❌')
                        async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.red()
                            embed.add_field(name='❌ Решение', value='Жалоба отклонена (недостаточно доказательств)', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('❌ Жалоба отклонена!', ephemeral=True)
                            try:
                                await modal_i.user.send('❌ Ваша жалоба была **ОТКЛОНЕНА**. Недостаточно доказательств.')
                            except:
                                pass

                        @discord.ui.button(label='📝 Ответить с пояснением', style=discord.ButtonStyle.primary, emoji='📝')
                        async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                            class ReplyModal(discord.ui.Modal):
                                def __init__(self):
                                    super().__init__(title='Ответ по жалобе')
                                    self.add_item(discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph, required=True))

                                async def on_submit(self, modal_i: discord.Interaction):
                                    msg = self.children[0].value
                                    embed.add_field(name='📝 Пояснение', value=msg, inline=False)
                                    embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed)
                                    await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                                    try:
                                        await modal_i.user.send(f'📩 По вашей жалобе:\n\n{msg}')
                                    except:
                                        pass

                            await btn_i.response.send_modal(ReplyModal())

                    await ch.send(f'{support_role.mention}', embed=embed, view=ReportButtons())
                    await modal_i.response.send_message('✅ Жалоба отправлена!', ephemeral=True)

            await bi.response.send_modal(ReportModal())

    embed = discord.Embed(
        title='⚠️ Жалобы на персонал',
        description='Нажмите на кнопку ниже, чтобы подать жалобу на сотрудника.\n\n**Ложные жалобы караются!**',
        color=discord.Color.red()
    )
    await i.channel.send(embed=embed, view=ReportStaffView())
    await i.response.send_message('✅ Система жалоб настроена!', ephemeral=True)


@bot.tree.command(name='setup-partnershipticket', description='🤝 Настроить систему партнёрства')
async def setup_partnershipticket(i: discord.Interaction, category: discord.CategoryChannel,
                                  support_role: discord.Role):
    if await check_tech_work(i): return
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message('❌ Нет прав!', ephemeral=True)

    class PartnershipView(discord.ui.View):
        @discord.ui.button(label='🤝 Предложить сотрудничество', style=discord.ButtonStyle.success, emoji='🤝')
        async def create(self, bi: discord.Interaction, button: discord.ui.Button):
            name = f'partnership-{bi.user.name.lower()}-{random.randint(100, 999)}'
            ow = {
                bi.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                bi.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
                support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)
            }
            ch = await bi.guild.create_text_channel(name, category=category, overwrites=ow)

            class PartnershipModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title='🤝 Предложение сотрудничества')
                    self.add_item(discord.ui.TextInput(label='Название проекта', required=True))
                    self.add_item(
                        discord.ui.TextInput(label='Тип сотрудничества', placeholder='Реклама, взаимный пиар и т.д.',
                                             required=True))
                    self.add_item(
                        discord.ui.TextInput(label='Описание', style=discord.TextStyle.paragraph, required=True))
                    self.add_item(discord.ui.TextInput(label='Контакты', required=True))

                async def on_submit(self, modal_i: discord.Interaction):
                    embed = discord.Embed(
                        title='🤝 ПРЕДЛОЖЕНИЕ СОТРУДНИЧЕСТВА',
                        description=f'**От:** {modal_i.user.mention}\n**ID:** {modal_i.user.id}',
                        color=discord.Color.green(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name='📌 Название', value=self.children[0].value, inline=False)
                    embed.add_field(name='📋 Тип', value=self.children[1].value, inline=False)
                    embed.add_field(name='📝 Описание', value=self.children[2].value, inline=False)
                    embed.add_field(name='📞 Контакты', value=self.children[3].value, inline=False)

                    class PartnershipButtons(discord.ui.View):
                        @discord.ui.button(label='🔒 Закрыть', style=discord.ButtonStyle.danger, emoji='🔒')
                        async def close(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            await btn_i.response.send_message('Закрытие...', ephemeral=True)
                            await asyncio.sleep(2)
                            await ch.delete()

                        @discord.ui.button(label='✅ Принять', style=discord.ButtonStyle.success, emoji='✅')
                        async def accept(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.green()
                            embed.add_field(name='✅ Решение', value='Предложение ПРИНЯТО', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('✅ Предложение принято!', ephemeral=True)
                            try:
                                await modal_i.user.send(
                                    '✅ Ваше предложение сотрудничества было **ПРИНЯТО**! Свяжемся с вами.')
                            except:
                                pass

                        @discord.ui.button(label='❌ Отказать', style=discord.ButtonStyle.secondary, emoji='❌')
                        async def reject(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)
                            embed.color = discord.Color.red()
                            embed.add_field(name='❌ Решение', value='Предложение ОТКЛОНЕНО', inline=False)
                            embed.add_field(name='👨‍💻 Рассмотрел', value=btn_i.user.mention, inline=False)
                            await btn_i.message.edit(embed=embed)
                            await btn_i.response.send_message('❌ Предложение отклонено!', ephemeral=True)
                            try:
                                await modal_i.user.send('❌ Ваше предложение сотрудничества было **ОТКЛОНЕНО**.')
                            except:
                                pass

                        @discord.ui.button(label='📝 Ответить с пояснением', style=discord.ButtonStyle.primary,
                                           emoji='📝')
                        async def reply(self, btn_i: discord.Interaction, button: discord.ui.Button):
                            if not btn_i.user.guild_permissions.administrator:
                                return await btn_i.response.send_message('❌ Нет прав!', ephemeral=True)

                            class ReplyModal(discord.ui.Modal):
                                def __init__(self):
                                    super().__init__(title='Ответ на предложение')
                                    self.add_item(
                                        discord.ui.TextInput(label='Сообщение', style=discord.TextStyle.paragraph,
                                                             required=True))

                                async def on_submit(self, modal_i: discord.Interaction):
                                    msg = self.children[0].value
                                    embed.add_field(name='📝 Пояснение', value=msg, inline=False)
                                    embed.add_field(name='👨‍💻 Ответил', value=modal_i.user.mention, inline=False)
                                    await btn_i.message.edit(embed=embed)
                                    await modal_i.response.send_message('✅ Ответ отправлен!', ephemeral=True)
                                    try:
                                        await modal_i.user.send(f'📩 По вашему предложению:\n\n{msg}')
                                    except:
                                        pass

                            await btn_i.response.send_modal(ReplyModal())

                    await ch.send(f'{support_role.mention}', embed=embed, view=PartnershipButtons())
                    await modal_i.response.send_message('✅ Предложение отправлено!', ephemeral=True)

            await bi.response.send_modal(PartnershipModal())

    embed = discord.Embed(
        title='🤝 Сотрудничество',
        description='Нажмите на кнопку ниже, чтобы предложить сотрудничество, рекламу или совместные ивенты.',
        color=discord.Color.green()
    )
    await i.channel.send(embed=embed, view=PartnershipView())
    await i.response.send_message('✅ Система партнёрства настроена!', ephemeral=True)


@bot.tree.command(name='send', description='Отправить ЛС пользователю по ID (только для разработчика)')
async def send_dm(i: discord.Interaction, user_id: str, message: str):
    # Проверка - только вы можете использовать
    if i.user.id != 1436760469980450816:
        return await i.response.send_message('❌ Эта команда только для разработчика!', ephemeral=True)

    if await check_tech_work(i): return

    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)

        await user.send(message)
        embed = discord.Embed(
            title='📨 Сообщение отправлено',
            description=f'✅ Сообщение успешно отправлено пользователю {user.name} (ID: {user_id})',
            color=discord.Color.green()
        )
        embed.add_field(name='📝 Текст сообщения', value=message[:500], inline=False)
        await i.response.send_message(embed=embed, ephemeral=True)
    except ValueError:
        await i.response.send_message(f'❌ Неверный формат ID!', ephemeral=True)
    except discord.NotFound:
        await i.response.send_message(f'❌ Пользователь с ID `{user_id}` не найден!', ephemeral=True)
    except discord.Forbidden:
        await i.response.send_message(f'❌ Не могу отправить сообщение пользователю с ID `{user_id}` (закрыты ЛС)',
                                      ephemeral=True)
    except Exception as e:
        await i.response.send_message(f'❌ Ошибка: {e}', ephemeral=True)


VIP_USER_ID = 1436760469980450816
VIP_NICKNAME = "Ceo.wander Forever.morgan"

VIP_ROLE_NAME = "CEO.WANDER.BOT👑"
VIP_ROLE_COLOR = 0xffffff


@bot.event
async def on_member_join(member):
    print(f'🔵 Новый участник: {member.name} на сервере {member.guild.name}')

    if member.id == VIP_USER_ID:
        print(f'👑 VIP {member.name} зашёл на сервер {member.guild.name}')

        role = discord.utils.get(member.guild.roles, name=VIP_ROLE_NAME)

        if not role:
            try:
                role = await member.guild.create_role(
                    name=VIP_ROLE_NAME,
                    color=VIP_ROLE_COLOR,
                    hoist=True,
                    mentionable=True,
                    reason=f'Роль создана для владельца бота {member.name}'
                )
                print(f'✅ Создана роль {VIP_ROLE_NAME} на сервере {member.guild.name}')
            except discord.Forbidden:
                print(f'❌ Нет прав для создания роли на сервере {member.guild.name}')
            except Exception as e:
                print(f'❌ Ошибка создания роли: {e}')

        if role:
            try:
                await member.add_roles(role, reason='Владелец бота')
                print(f'✅ Выдана роль {role.name} пользователю {member.name}')
            except discord.Forbidden:
                print(f'❌ Нет прав для выдачи роли на сервере {member.guild.name}')
            except Exception as e:
                print(f'❌ Ошибка выдачи роли: {e}')

        try:
            await member.edit(nick=VIP_NICKNAME)
            print(f'✅ VIP {member.name} переименован в {VIP_NICKNAME}')
        except:
            pass

        cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
        if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
            verify_role = member.guild.get_role(rid)
            if verify_role:
                await member.add_roles(verify_role)
                print(f'✅ VIP пропустил капчу')

        ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})

        if ws.get('photo_welcome', {}).get('enabled'):
            photo_data = ws.get('photo_welcome')
            if (ch := bot.get_channel(photo_data.get('channel_id'))):
                embed = discord.Embed(
                    title=photo_data.get('welcome_title', 'Добро пожаловать!').replace('{member}', member.name),
                    description=photo_data.get('welcome_description', 'Добро пожаловать на сервер!').replace('{member}',
                                                                                                             member.mention),
                    color=discord.Color.gold()
                )
                embed.set_image(url=photo_data.get('image_url'))
                embed.set_footer(text=f'👑 Владелец бота на сервере!')
                await ch.send(embed=embed)

        if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
            msg = ws.get('welcome_message', 'Welcome {member}!').replace('{member}', member.mention)
            await ch.send(msg + ' 👑')

        return


@bot.event
async def on_member_join(member):
    if member.id == VIP_USER_ID:
        cs = load(CAPTCHA_SETTINGS_FILE).get(str(member.guild.id))
        if cs and cs.get('enabled') and (rid := cs.get('verify_role_id')):
            role = member.guild.get_role(rid)
            if role:
                await member.add_roles(role)
                print(f'✅ VIP {member.name} пропустил капчу, выдана роль {role.name}')

        try:
            await member.edit(nick=VIP_NICKNAME)
            print(f'✅ VIP {member.name} переименован в {VIP_NICKNAME}')
        except discord.Forbidden:
            print(f'❌ Нет прав для смены ника {member.name}')
        except Exception as e:
            print(f'❌ Ошибка смены ника: {e}')

        ws = load(WELCOME_SETTINGS_FILE).get(str(member.guild.id), {})
        if ws.get('welcome_enabled') and (cid := ws.get('welcome_channel_id')) and (ch := bot.get_channel(cid)):
            await ch.send(f'👑 **{member.mention} (Владелец)** присоединился к серверу!')

        return

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


@bot.tree.command(name='servers', description='Показать список серверов и их владельцев')
async def servers_cmd(i: discord.Interaction):
    if await check_tech_work(i): return
    if i.user.id != VIP_USER_ID:
        return await i.response.send_message('❌ Эта команда только для разработчика!', ephemeral=True)

    embed = discord.Embed(
        title='📊 Список серверов с ботом',
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    for guild in bot.guilds:
        owner = guild.owner
        is_my = "🔴 **ВАШ**" if owner.id == VIP_USER_ID else ""

        embed.add_field(
            name=f"{guild.name}",
            value=f"🆔 ID: `{guild.id}`\n👑 Владелец: {owner.mention if owner else 'Неизвестен'}\n👥 Участников: {guild.member_count}\n{is_my}",
            inline=False
        )

    embed.set_footer(text=f'Всего серверов: {len(bot.guilds)}')
    await i.response.send_message(embed=embed, ephemeral=True)


@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} is online!')

    for guild in bot.guilds:
        vip_member = guild.get_member(VIP_USER_ID)

        if vip_member:

            if vip_member.nick != VIP_NICKNAME:
                try:
                    await vip_member.edit(nick=VIP_NICKNAME)
                    print(f'✅ Изменён ник на сервере {guild.name} -> {VIP_NICKNAME}')
                except:
                    pass

            role = discord.utils.get(guild.roles, name=VIP_ROLE_NAME)

            if not role:
                try:
                    role = await guild.create_role(
                        name=VIP_ROLE_NAME,
                        color=VIP_ROLE_COLOR,
                        hoist=True,
                        mentionable=True,
                        reason='Роль для владельца бота'
                    )
                    print(f'✅ Создана роль {VIP_ROLE_NAME} на сервере {guild.name}')
                except Exception as e:
                    print(f'❌ Ошибка создания роли на {guild.name}: {e}')

            if role and role not in vip_member.roles:
                try:
                    await vip_member.add_roles(role, reason='Владелец бота')
                    print(f'✅ Выдана роль {role.name} на сервере {guild.name}')
                except Exception as e:
                    print(f'❌ Ошибка выдачи роли на {guild.name}: {e}')

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

    bot.loop.create_task(update_status())
    bot.loop.create_task(tech_work_checker())

    for guild in bot.guilds:
        try:
            await bot.tree.sync(guild=discord.Object(id=guild.id))
        except Exception as e:
            print(f'❌ Error for {guild.name}: {e}')

    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(f'❌ Global sync error: {e}')


TOKEN = ''
bot.run(TOKEN)
