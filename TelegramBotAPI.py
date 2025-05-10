import telebot
from telebot import types

# Токен для бота от BotFather
TOKEN = '7706937394:AAEO4HWY8RubKHlnQbJRL51zVhThg89Du0o'

# Инициализация бота
bot = telebot.TeleBot('7706937394:AAEO4HWY8RubKHlnQbJRL51zVhThg89Du0o')

# Хранение пользовательских данных
user_data = {}  # {chat_id: {'state': '...', 'login': '...', 'password': '...', 'reminder': None}}

# --- Функции создания клавиатур ---

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_login = types.KeyboardButton("🔐 Войти в ЛМС")
    btn_faq = types.KeyboardButton("❓ FAQ")
    btn_commands = types.KeyboardButton("📋 Список команд")
    markup.add(btn_login, btn_faq, btn_commands)
    return markup

def get_logged_in_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_logout = types.KeyboardButton("🚪 Выйти из аккаунта")
    btn_deadlines = types.KeyboardButton("📅 Посмотреть дедлайны")
    btn_reminders = types.KeyboardButton("🔔 Настроить напоминания")
    btn_faq = types.KeyboardButton("❓ FAQ")
    btn_commands = types.KeyboardButton("📋 Список команд")
    markup.add(btn_logout, btn_deadlines, btn_reminders, btn_faq, btn_commands)
    return markup

def get_reminder_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_3_days = types.KeyboardButton("📅 За 3 дня")
    btn_1_day = types.KeyboardButton("📅 За 1 день")
    btn_1_hour = types.KeyboardButton("⏰ За 1 час")
    btn_back = types.KeyboardButton("↩️ Назад")
    markup.add(btn_3_days, btn_1_day, btn_1_hour, btn_back)
    return markup

# --- Команды и обработка нажатий ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'state': 'logged_out'}
    bot.send_message(chat_id, "Привет! 👋\n\nЭтот бот поможет тебе следить за дедлайнами и управлять учётной записью ЛМС.\nНажмите на нужную кнопку ниже.", reply_markup=get_main_menu())

# --- Обработка всех сообщений ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {'state': 'logged_out'}

    current_state = user_data[chat_id].get('state')

    # --- Главное меню (пользователь не вошёл) ---
    if current_state == 'logged_out':
        if text == "🔐 Войти в ЛМС":
            user_data[chat_id]['state'] = 'awaiting_login'
            bot.send_message(chat_id, "Введите ваш логин:")

        elif text == "❓ FAQ":
            bot.send_message(chat_id, "Здесь будет текст с частыми вопросами и ответами.")

        elif text == "📋 Список команд":
            show_commands(chat_id)

        else:
            bot.send_message(chat_id, "Не понял вас. Вот доступные команды:", reply_markup=get_main_menu())

    # --- Авторизация: ввод логина ---
    elif current_state == 'awaiting_login':
        user_data[chat_id]['login'] = text
        user_data[chat_id]['state'] = 'awaiting_password'
        bot.send_message(chat_id, "Введите ваш пароль:")

    # --- Авторизация: ввод пароля ---
    elif current_state == 'awaiting_password':
        user_data[chat_id]['password'] = text
        login = user_data[chat_id]['login']
        bot.send_message(chat_id, f"✅ Вы успешно вошли как *{login}*", parse_mode='Markdown')
        user_data[chat_id]['state'] = 'logged_in'
        bot.send_message(chat_id, "Выберите действие:", reply_markup=get_logged_in_menu())

    # --- Меню после авторизации ---
    elif current_state == 'logged_in':
        if text == "📅 Посмотреть дедлайны":
            bot.send_message(chat_id, "📌 Ближайшие дедлайны:\n1. Домашнее задание по математике — 05.04.2025\n2. Эссе по литературе — 08.04.2025")

        elif text == "🔔 Настроить напоминания":
            user_data[chat_id]['state'] = 'awaiting_reminder'
            bot.send_message(chat_id, "Выберите периодичность напоминаний:", reply_markup=get_reminder_menu())

        elif text == "🚪 Выйти из аккаунта":
            user_data[chat_id]['state'] = 'logged_out'
            user_data[chat_id]['login'] = ''
            user_data[chat_id]['password'] = ''
            bot.send_message(chat_id, "🚪 Вы вышли из аккаунта.", reply_markup=get_main_menu())

        elif text == "❓ FAQ":
            bot.send_message(chat_id, "Здесь будет текст с частыми вопросами и ответами.")

        elif text == "📋 Список команд":
            show_commands(chat_id)

        else:
            bot.send_message(chat_id, "Неизвестная команда. Показываю список доступных команд:", reply_markup=get_logged_in_menu())

    # --- Настройка напоминаний ---
    elif current_state == 'awaiting_reminder':
        reminder_map = {
            "📅 За 3 дня": "3 дня",
            "📅 За 1 день": "1 день",
            "⏰ За 1 час": "1 час"
        }

        if text in reminder_map:
            selected = reminder_map[text]
            user_data[chat_id]['reminder'] = selected
            bot.send_message(chat_id, f"🔔 Напоминания установлены: за {selected}")
            user_data[chat_id]['state'] = 'logged_in'
            bot.send_message(chat_id, "Выберите действие:", reply_markup=get_logged_in_menu())

        elif text == "↩️ Назад":
            user_data[chat_id]['state'] = 'logged_in'
            bot.send_message(chat_id, "Выберите действие:", reply_markup=get_logged_in_menu())

        else:
            bot.send_message(chat_id, "Пожалуйста, выберите один из вариантов ниже:", reply_markup=get_reminder_menu())

    # --- Резервный случай ---
    else:
        bot.send_message(chat_id, "Произошла ошибка. Попробуйте начать заново с /start")


# --- Функция показа списка команд ---
def show_commands(chat_id):
    bot.send_message(chat_id, """
📄 Список доступных команд:
- 🔐 Войти в ЛМС — войти в систему обучения
- 📅 Посмотреть дедлайны — получить информацию о ближайших задачах
- 🔔 Настроить напоминания — выбрать частоту уведомлений о дедлайнах
- 🚪 Выйти из аккаунта — завершить сессию
- ❓ FAQ — получить полезную информацию
- 📋 Список команд — вызвать это меню
    """)

# --- Запуск бота ---
print("Бот запущен...")
bot.polling(none_stop=True)
