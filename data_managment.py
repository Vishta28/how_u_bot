import sqlite3
from datetime import datetime, timedelta

def create_table(user_id, name, time):
	with sqlite3.connect('database') as source:  # відкриваємо базу данних
		cursor = source.cursor()  # курсор ходит по таблице и выполняет ('execute')
		cursor.execute(f"SELECT EXISTS(SELECT user_id FROM feelings WHERE user_id = {user_id})")
		check_user_id = cursor.fetchone()[0]
		if check_user_id == 0:
			cursor.execute(f''' 
			INSERT INTO feelings(user_id, name, time)
			VALUES ("{user_id}", "{name}", "{time}")
			''')
		else:
			update = (time, user_id)  # вопрос! нужно ли после перезахода обновлять все этапы и эмоции, иначе может быть недостоверная инфа
			cursor.execute(f'''UPDATE feelings
							SET time = ?
							WHERE user_id = ?
							''', update)

def update_table(progress, emotion, feedback, time, user_id):
	with sqlite3.connect('database') as source:  # під'єднуємось до таблиці та оновлюємо колонки в залежності від прогресу
		cursor = source.cursor()
		update = (time, user_id)
		cursor.execute(f'''UPDATE feelings
						SET time =?
						WHERE user_id = ?
						''', update)
		if progress == 0:
			update = (feedback, emotion, user_id)
			cursor.execute(f'''UPDATE feelings
							SET pre_step = ?, emotion = ?
							WHERE user_id = ?
							''', update)
		elif progress == 1:
			update = (feedback, emotion, user_id)
			cursor.execute(f'''UPDATE feelings
							SET step1 = ?, emotion = ?
							WHERE user_id = ?
							''', update)
		else:
			update = (feedback, 'done', user_id)
			cursor.execute(f'''UPDATE feelings
							SET step2 = ?, retarget = ?
							WHERE user_id = ?
							''', update)

def update_retarget(user_id, time):
	with sqlite3.connect('database') as source:
		cursor = source.cursor()
		update = (time, 'done', user_id)
		cursor.execute(f'''UPDATE feelings
					SET time =?, retarget = ?
					WHERE user_id = ?
					''', update)

def check_retarget():
	with sqlite3.connect('database') as source:  # подключаемся к таблице
		cursor = source.cursor()  # курсор ходит по таблице и выполняет ('execute')
		cursor.execute('''CREATE TABLE IF NOT EXISTS feelings(
		user_id INTEGER PRIMARY KEY,
		name TEXT,
		time DATETIME,
		emotion TEXT,
		pre_step TEXT,
		step1 TEXT,
		step2 TEXT,
		retarget TEXT
		)''')
		retarget_status = [el for el in cursor.execute("SELECT retarget, time FROM feelings")]
		message_ready_time = []

		for data in retarget_status:
			now = datetime.now().replace(microsecond=0)
			bd = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')

			if data[0] != 'done' and now > bd + timedelta(minutes=2):
				cursor.execute(f"SELECT user_id, emotion, retarget FROM feelings WHERE time = '{data[1]}'")
				small_retargert = cursor.fetchone()
				message_ready_time.append(small_retargert)
				print('small_retarget', small_retargert)

			elif now > bd + timedelta(minutes=1):
				cursor.execute(f"SELECT user_id, emotion, retarget FROM feelings WHERE time = '{data[1]}'")
				long_retargert = cursor.fetchone()
				message_ready_time.append(long_retargert)
				print('long_retarget', long_retargert)
	return message_ready_time