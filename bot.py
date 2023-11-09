import telebot
import sqlite3

token = '6157856042:AAFOLJBBLPqq2ogGe7t-......'
bot = telebot.TeleBot(token)

HELP = '''
Список доступных команд:
* /show  - После команды ввседите фамилию дожника, что бы посмотреть всех /show
* /add - Что бы добавить должника введите фамилию пробел то что он взял
* /help - Напечатать help
'''

def add_todo(conn, date, task):
    date = date.lower()
    task = task.lower()
    c = conn.cursor()
    c.execute('''INSERT INTO todos VALUES (?, ?)''', (date, task))
    conn.commit()

def get_todos(conn):
    c = conn.cursor()
    c.execute('''SELECT date, task FROM todos''')
    rows = c.fetchall()
    if len(rows) == 0:
        return None
    else:
        return '\n'.join([f'{row[0]}: {row[1]}' for row in rows])

def delete_last_todo(conn, date):
    date = date.lower()
    c = conn.cursor()
    c.execute('''SELECT rowid FROM todos WHERE date=? ORDER BY rowid DESC LIMIT 1''', (date,))
    rows = c.fetchall()
    if len(rows) > 0:
        rowid = rows[0][0]
        c.execute('''DELETE FROM todos WHERE rowid=?''', (rowid,))
        conn.commit()
        return True
    else:
        return False

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands=['add'])
def add(message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.send_message(message.chat.id, "Необходимо ввести фамилию должника и то, что он взял после команды /add")
    else:
        _, date, task = args
        if not date.strip() or not task.strip():
            bot.send_message(message.chat.id, "Пожалуйста, введите действительные параметры.")
        else:
            conn = sqlite3.connect('todos.db')
            add_todo(conn, date, task)
            conn.close()
            bot.send_message(message.chat.id, f'{date}, взял {task}')

@bot.message_handler(commands=['show'])
def show(message):
    conn = sqlite3.connect('todos.db')
    tasks = get_todos(conn)
    conn.close()
    if tasks is None:
        bot.send_message(message.chat.id, 'Список должников пуст')
    else:
        bot.send_message(message.chat.id, tasks)

@bot.message_handler(commands=['del'])
def delete(message):
    _, date = message.text.split(maxsplit=1)
    conn = sqlite3.connect('todos.db')
    if delete_last_todo(conn, date):
        bot.send_message(message.chat.id, f'Последний должник {date} удален из списка')
    else:
        bot.send_message(message.chat.id, f'Нет должников за {date} в списке или список пуст')
    conn.close()

bot.polling(none_stop=True)
