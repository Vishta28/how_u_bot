from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
	InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

keyA = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Давай сробуємо  👍')
keyA.add(button1)

keyB = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
button2 = KeyboardButton(text='Страх 🫣')
button3 = KeyboardButton(text='Тривога 😬')
button4 = KeyboardButton(text='Провина 😰')
button5 = KeyboardButton(text='Сум ☹')
button6 = KeyboardButton(text='Злість 😡')
button7 = KeyboardButton(text='Я не розумію що відчуваю 🤔')
keyB.add(button2, button5, button6, button3, button4).add(button7)

keyC = ReplyKeyboardMarkup(resize_keyboard=True)
button01 = KeyboardButton(text='1 🟢')
button02 = KeyboardButton(text='2 🟢')
button03 = KeyboardButton(text='3 🟢')
button04 = KeyboardButton(text='4 🟠')
button05 = KeyboardButton(text='5 🟠')
button06 = KeyboardButton(text='6 🟠')
button07 = KeyboardButton(text='7 🔴')
button08 = KeyboardButton(text='8 🔴')
button09 = KeyboardButton(text='9 🔴')
button10 = KeyboardButton(text='10 ⚫')
keyC.add(button01, button02, button03, button04, button05, button06,
		button07, button08, button09, button10)

keyE = ReplyKeyboardMarkup(resize_keyboard=True)
button12 = KeyboardButton(text='Завершити ✅')
keyE.add(button12)

keyF = ReplyKeyboardMarkup(resize_keyboard=True)
button11 = KeyboardButton(text='Готово 👍')
keyF.add(button11)

keyG = ReplyKeyboardMarkup(resize_keyboard=True)
button13 = KeyboardButton(text='Назад ⤴')
keyG.add(button13)

keyD_1 = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Техніка 1️⃣')
keyD_1.add(button_1)

keyD_2 = ReplyKeyboardMarkup(resize_keyboard=True)
button_2 = KeyboardButton(text='Техніка 2️⃣')
keyD_2.add(button_2)

none = ReplyKeyboardRemove()

inl_keyR = InlineKeyboardMarkup(row_width=1)
inl_keyR2 = InlineKeyboardMarkup(row_width=1)
inl_key_state = InlineKeyboardMarkup(row_width=1)
inl_keyRetarget = InlineKeyboardMarkup(row_width=1)

inl_button1 = InlineKeyboardButton(text='Спробувати інші техніки 🔬',
									callback_data='techniks')
inl_button7 = InlineKeyboardButton(text='Скористатися ботом 🤖',
									callback_data='techniks2')
inl_button2 = InlineKeyboardButton(text='Поставити питання спеціалісту 🗣️',
									callback_data='question')
inl_button6 = InlineKeyboardButton(text='Відповісти на питання людині👤', url='https://ig.me/m/yaremenko_dmitry.psy')
inl_button3 = InlineKeyboardButton(text='Підтримати проєкт 💸',
									callback_data='donate')
inl_button4 = InlineKeyboardButton(text='Додаткова допомога 👥',
									callback_data='donate2')
inl_button5 = InlineKeyboardButton(text='Продовжити виконання техніки ⏩',
									callback_data='tech2')

inl_keyR.add(inl_button1, inl_button2, inl_button3)
inl_keyR2.add(inl_button1, inl_button2, inl_button4)
inl_key_state.add(inl_button2, inl_button5)
inl_keyRetarget.add(inl_button7, inl_button6)

async def message_correct(message):
	correct_message = None
	circles = [(1, '🟢'), (2, '🟢'), (3, '🟢'), (4, '🟠'), (5, '🟠'),
			(6, '🟠'), (7, '🔴'), (8, '🔴'), (9, '🔴'), (10, '⚫')]
	for elements in circles:
		if int(message) in elements:
			correct_message = message + elements[1]
	return correct_message