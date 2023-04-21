import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile
from text import ALL_QUESTS, BOT_TEXT, PRE_QUESTS, RETARGET_QUESTIONS, MEDIA, CALL_BACK_TEXT
from buttons import keyA, keyB, keyC, keyD_1, keyD_2, keyF, inl_keyR, inl_keyR2, keyE, \
	keyG, none, inl_key_state, message_correct, inl_keyRetarget
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # оперативна пам'ять
from aiogram.dispatcher.filters.state import StatesGroup, State  # стан
from aiogram.dispatcher import FSMContext  # запис змінних
from data_managment import create_table, update_table, check_retarget, update_retarget, \
	emotion_state_check, emotion_proxy, emotion_state_road
from datetime import datetime
import random
from dotenv import load_dotenv
import os

load_dotenv()  # підключення до закритого файлу
bot = Bot(token=os.getenv('TOKEN'))
INST_URL = os.getenv('INST_URL')
dp = Dispatcher(bot, storage=MemoryStorage())

class QuestStep(StatesGroup):
	emotion = State()
	emotion_description = State()
	pre_step = State()
	step1 = State()
	step2 = State()
	feedback = State()
	final = State()

async def bot_polling():
	@dp.message_handler(commands=['start'], state='*')
	async def process_start_command(message: types.Message):
		user_id, name, time = message.from_user.id, message.from_user.first_name, datetime.now().replace(microsecond=0)
		create_table(user_id, name, time)  # створюємо та оновлюємо базу даних
		await bot.send_message(message.chat.id, f"Вітаю, {message.from_user.first_name}!", reply_markup=none)
		await bot.send_message(message.chat.id, BOT_TEXT['bot_description'][0])  # беремо значення зі списку bot_description

		await bot.send_chat_action(message.chat.id, action='typing')  # бот імітує написання повідомлення
		await asyncio.sleep(6)

		await bot.send_message(message.chat.id, BOT_TEXT['bot_description'][1], reply_markup=keyA)
		await QuestStep.emotion.set()

	@dp.message_handler(commands=['info'], state='*')  # обробляємо основні команди бота
	async def process_start_command(message: types.Message):
		await bot.send_message(message.chat.id, "Додаткова інформація:")
		await bot.send_chat_action(message.chat.id, action='typing')  # бот імітує написання повідомлення
		await asyncio.sleep(1)
		await bot.send_message(message.chat.id, BOT_TEXT['bot_description'][1])
		await asyncio.sleep(2)
		await bot.send_message(message.chat.id, 'Наш Instagram де ви можете поставити запитання ➡ '
												f'<a href="{INST_URL}">наш Instagram</a>', types.ParseMode.HTML)
	@dp.message_handler(commands=['donate'], state='*')  # обробляємо основні команди бота
	async def process_start_command(message: types.Message):
		photo = 'https://drive.google.com/uc?id=1DTAk3e2FP0UWGWBxF3i4gdUnb89PVX0A'
		await bot.send_photo(message.from_user.id, photo)
		await asyncio.sleep(2)
		await bot.send_message(message.chat.id, CALL_BACK_TEXT[0], parse_mode='HTML')
	@dp.message_handler(state=QuestStep.emotion)
	async def choose_emotion(message: types.Message):
		await bot.send_message(message.chat.id, "Підкажи, що ти зараз відчуваеш? 💙", reply_markup=keyB)
		await QuestStep.emotion_description.set()

	@dp.message_handler(state=QuestStep.emotion_description)
	async def emotion_description(message: types.Message, state: FSMContext):
		emotion = message.text[:-2].lower()   # фіксуємо обрану емоцію
		if emotion not in ALL_QUESTS.keys():  # перевіряємо чи така емоція доступна в списку
			await bot.send_message(message.chat.id, 'Помилка! На жаль я вмію працювати тільки з тими емоціями, '
													'яким мене навчив автор 🤖', reply_markup=keyG)
			await QuestStep.emotion.set()
		else:
			if emotion == 'я не розумію що відчуваю':
				await bot.send_photo(message.chat.id, photo=InputFile.from_url(MEDIA[emotion][2]), reply_markup=none)
				await bot.send_chat_action(message.chat.id, action='typing')  # typing
				await asyncio.sleep(2)  # затримка
				message_text, markup = 'Спробуємо розібратись?', keyA
			else:
				message_text, markup = 'Як би ви оцінили зараз інтенсивність вашого стану по 10-бальній шкалі? 💙', keyC

			async with state.proxy() as data:  # запаковуємо наші змінні у state.proxy() (словник)
				data['step'] = 0
				data['emotion'] = emotion

			await bot.send_message(message.chat.id, PRE_QUESTS[emotion][0], reply_markup=none)
			await bot.send_chat_action(message.chat.id, action='typing')
			await asyncio.sleep(4)

			await bot.send_message(message.chat.id, message_text, reply_markup=markup)
			await QuestStep.pre_step.set()

	@dp.message_handler(state=QuestStep.pre_step)
	async def pre_step(message: types.Message, state: FSMContext):
		async with state.proxy() as data:
			try:
				step = data['step']
				emotion = data['emotion']
			except:
				step = 2
				emotion = await emotion_proxy(message.from_user.id)

			# блок на випадок якщо користувач вводить дані не з клавіатури, але це коректне число
			if 0 < int(message.text) < 11 and message.text.isdigit() is True:
				message.text = await message_correct(message.text)		# виправляємо повідомлення у правильний формат

			# emotion_state - змінна для запису стану. Оскільки в цьому блоку багато обробки повідомлення від юзера
			# довелося створити окремо змінну замість message.text
			if message.text[:-1].rstrip().isdigit() is True and 0 < int(message.text[:-1].rstrip()) < 11:
				current_state = message.text
				update_table(step, emotion, message.text, datetime.now().replace(microsecond=0), message.from_user.id)  # оновлюємо бд
			elif message.text == 'Давай сробуємо  👍':
				current_state = await emotion_state_check(step, message.from_user.id, message.text)
			else:
				current_state = '0❌'  # записуємо в бд 0 якщо інформація не відповідає шаблону
				update_table(step, emotion, current_state, datetime.now().replace(microsecond=0), message.from_user.id)  # оновлюємо бд

			markup = keyD_1 if step == 0 else keyD_2  # клавіатура техніка 1 та техніка 2 в залежності від етапу

			last_check = await emotion_state_check(step=step, user_id=message.from_user.id, message=message.text)  # стан на попередньому етапі

			if int(last_check[:-1]) != 0 and int(current_state[:-1]) > int(last_check[:-1]):
				await bot.send_message(message.chat.id, 'Нам шкода що вас стан погіршився. 😔', reply_markup=keyG)
				await asyncio.sleep(1)
				await bot.send_message(message.chat.id, CALL_BACK_TEXT[1], reply_markup=inl_key_state)
				await QuestStep.emotion.set()
			else:
				step = int(step) + 1 if step != 2 else step
				data['step'] = step
				data['emotion'] = emotion
				await bot.send_message(message.chat.id, PRE_QUESTS[emotion][step], reply_markup=markup, parse_mode='HTML')
				await QuestStep.step1.set() if step == 1 else await QuestStep.step2.set()  # в залежності від поточного прогресу

	@dp.message_handler(state=QuestStep.step1)  # вправа 1
	async def step1(message: types.Message, state: FSMContext):  # 1 квест
		async with state.proxy() as data:  # розпаковуємо наші змінні
			emotions = data['emotion']
			step = data['step']

		photo = MEDIA[emotions][0]  # обираємо потрібне фото під індексом(0) зі словника
		await bot.send_photo(message.chat.id, photo=InputFile.from_url(photo), reply_markup=none)
		await bot.send_chat_action(message.chat.id, action='typing')
		await asyncio.sleep(2)

		await bot.send_message(message.chat.id, ALL_QUESTS[emotions][step], reply_markup=keyF)  # відправляємо завдання 1
		await QuestStep.pre_step.set() if emotions == 'я не розумію що відчуваю' else await QuestStep.feedback.set()

	@dp.message_handler(state=QuestStep.step2)  # вправа 2
	async def step2(message: types.Message, state: FSMContext):  # 2 квест

		async with state.proxy() as data:  # распаковываем нашу переменную
			emotions = data['emotion']
			step = data['step']
		await bot.send_chat_action(message.chat.id, action='typing')

		photo = MEDIA[emotions][1]  # обираємо потрібне фото під індексом(1) зі словника
		await bot.send_photo(message.chat.id, photo=InputFile.from_url(photo), reply_markup=none)

		await bot.send_chat_action(message.chat.id, action='typing')
		await asyncio.sleep(2)

		await bot.send_message(message.chat.id, ALL_QUESTS[emotions][step], reply_markup=keyF)  # відправляємо завдання

		if emotions == 'тривога':  # відправляємо додатково аудіофайл якщо обрана 'тривога'
			await bot.send_chat_action(message.chat.id, action='upload_audio')
			await asyncio.sleep(2)
			try:
				await bot.send_audio(message.chat.id, 'CQACAgIAAxkBAANCZDQqVqaPjMN8TlWfrAkDdytUG1IAAg4rAAL665FJr69UsDX_rRwvBA')
			except:
				await bot.send_message(message.chat.id, 'На жаль не вдалося завантажити аудіофайл 😔 \nАле скоро ми це виправимо!')

		if emotions == 'я не розумію що відчуваю':  # змінюємо логіку при відсутності емоції оскільки фідбек не потрібен
			await QuestStep.final.set() if step == 2 else await QuestStep.feedback.set()
		else:
			await QuestStep.feedback.set()

	@dp.message_handler(state=QuestStep.feedback)
	async def feedback(message: types.Message, state: FSMContext):
		async with state.proxy() as data:  # запаковываем переменные в дату (словарь)
			step = data['step']

		previus_state = await emotion_state_check(step=step, user_id=message.from_user.id, message=message.text)
		await bot.send_message(message.chat.id, f'Вправа завершена!\nВаша попередня оцінка:  <b>{previus_state}</b>', parse_mode='HTML')
		await asyncio.sleep(1)
		await bot.send_message(message.chat.id, '<b>Після проходження даної техніки оцініть '
												'як змінився  ваш стан від 1 до 10? 💙</b>', reply_markup=keyC, parse_mode='HTML')
		await QuestStep.pre_step.set() if step < 2 else await QuestStep.final.set()

	@dp.message_handler(state=QuestStep.final)
	async def feedback(message: types.Message, state: FSMContext):
		async with state.proxy() as data:  # запаковываем переменные в дату (словарь)
			step = data['step']
			emotion = data['emotion']

		# блок на випадок якщо користувач вводить дані не з клавіатури, але це коректне число
		if 0 < int(message.text) < 11 and message.text.isdigit() is True:
			message.text = await message_correct(message.text)  # виправляємо повідомлення у правильний формат

		# отримуємо та обробляємо поточний емоційний стан користувача. Робимо зріз та прибираємо пробіли.
		current_state = message.text if message.text[:-1].rstrip().isdigit() is True and 0 < int(message.text[:-1].rstrip()) < 11 else '0❌'
		#  last_check змінна в якій ми зберінаємо емоційний стан користувача на попередньому етапі
		last_check = await emotion_state_check(step=step, user_id=message.from_user.id, message=message.text)
		# оновлюємо бд
		update_table(step, emotion, current_state, datetime.now().replace(microsecond=0), message.from_user.id)
		# отримуємо весь прогрес користувача із бд
		state_road = await emotion_state_road(message.from_user.id)

		if emotion == 'я не розумію що відчуваю':  # ця емоція не має шкали оцінки стану
			await bot.send_message(message.chat.id, 'Дякую що скористались нашим ботом!', reply_markup=keyE)
			await asyncio.sleep(1)
			await bot.send_message(message.chat.id, CALL_BACK_TEXT[2], reply_markup=inl_keyR)

		elif int(current_state[:-1]) == 0 or int(last_check[:-1]) == 0:
			await bot.send_message(message.chat.id, 'Мої сенсори не можуть підказати чи змінився ваш стан 💔\n\n'
													'Ваш результат:\n\n'
													f'{state_road[0][0]} <b>--></b> {state_road[0][1]} <b>--></b> {state_road[0][2]}'
													f'  <b>невідомий🫥</b>', reply_markup=keyE, parse_mode='HTML')
			await asyncio.sleep(2)
			await bot.send_message(message.chat.id, CALL_BACK_TEXT[4], reply_markup=inl_keyR2)

		elif int(current_state[:-1]) > int(last_check[:-1]):  # текст на випадок коли психологічний стан погіршився
			await bot.send_message(message.chat.id, 'Нажаль мої сенсори підказують, що вам стало гірше 🖤\n\n'
													'Ваш результат:\n\n'
													f'{state_road[0][0]} <b>--></b>  {state_road[0][1]} <b>--></b> {state_road[0][2]}'
													f'  <b>негативний.😔</b>', reply_markup=keyE, parse_mode='HTML')
			await asyncio.sleep(2)
			await bot.send_message(message.chat.id, CALL_BACK_TEXT[1], reply_markup=inl_keyR2)

		elif int(current_state[:-1]) < int(last_check[:-1]):  # текст на випадок коли психологічний стан покращився
			await bot.send_message(message.chat.id, 'Мої сенсори підказують, що вам стало краще 💙\n\n'
													'Ваш результат:\n\n'
													f'{state_road[0][0]} <b>--></b> {state_road[0][1]} <b>--></b> {state_road[0][2]}'
													f'  <b>позитивний!😃</b>', reply_markup=keyE, parse_mode='HTML')
			await asyncio.sleep(2)
			await bot.send_message(message.chat.id, CALL_BACK_TEXT[2], reply_markup=inl_keyR)

		elif int(current_state[:-1]) == int(last_check[:-1]):  # текст на випадок коли психологічний стан не змінився
			await bot.send_message(message.chat.id, 'Мої сенсори підказують, що стан не змінився 💜\n\n'
													'Ваш результат:\n\n'
													f'{state_road[0][0]} <b>--></b> {state_road[0][1]} <b>--></b> {state_road[0][2]}'
													f'  <b>нейтральний😐</b>', reply_markup=keyE, parse_mode='HTML')
			await asyncio.sleep(2)
			await bot.send_message(message.chat.id, CALL_BACK_TEXT[3], reply_markup=inl_keyR2)

		else:
			await bot.send_message(message.chat.id, 'Дякую що скористались нашим ботом!', reply_markup=keyE)
		await QuestStep.emotion.set()

	@dp.callback_query_handler(text=['techniks', 'question', 'donate', 'tech2', 'donate2', 'question2', 'techniks2'], state='*')
	async def callback_retarget(call: types.CallbackQuery):
		if call.data == 'techniks' or call.data == 'techniks2':
			await call.message.answer('Підкажи, що ти зараз відчуваеш? 💙', reply_markup=keyB)
			await QuestStep.emotion_description.set()
		elif call.data == 'question':
			await call.message.answer('Ви можете перейти за посиланням на наш Instagram, '
									'та поставити ваше питання у дірект')
			await asyncio.sleep(1)
			await call.message.answer(f'Поставити питання, клікай ➡ <a href="{INST_URL}">наш Instagram</a>', parse_mode='HTML')
		elif call.data == 'donate':
			photo = 'https://drive.google.com/uc?id=1DTAk3e2FP0UWGWBxF3i4gdUnb89PVX0A'
			await bot.send_photo(call.from_user.id, photo)
			await asyncio.sleep(2)
			await call.message.answer(CALL_BACK_TEXT[0], parse_mode='HTML')
		elif call.data == 'tech2':
			await call.answer('💙')
			await call.message.answer('Ми пишаємося вашою наполегливістю у вирішенні власних питань '
									'і віримо що у вас все вийде!', reply_markup=keyA)
			await QuestStep.pre_step.set()
		elif call.data == 'donate2':
			photo = 'https://drive.google.com/uc?id=1HGee7QeBu70R1bOmcq3K1vYVXy3RmGCY'
			await bot.send_photo(call.from_user.id, photo)
			await asyncio.sleep(2)
			await call.message.answer(CALL_BACK_TEXT[5], parse_mode='HTML')

	await dp.start_polling()

async def timer():  # функція котра відповідає за ретаргет та відлік часу
	while True:
		user_data = check_retarget()
		await asyncio.sleep(10800)
		print(user_data, '>>> user_data')

		if len(user_data) > 0:
			for data in user_data:
				retarget_to_user = data[0]
				ret_question = random.choice(RETARGET_QUESTIONS[data[1]])

				if data[2] != 'done':
					try:
						await bot.send_message(retarget_to_user, '<i>Вибачте що турбую, нагадую що нещодавно'
										'ви користувалися нашим ботом психологоічної допомоги для покращення свого стану.\n'
										'\n'
										'Пропонуємо вам завершити вправу, '
										f'або задати своє питання у нашому</i> <a href="{INST_URL}">Instagram </a>'
										, parse_mode=types.ParseMode.HTML)
					except Exception as er:
						print(er)
						pass
				else:
					try:
						await bot.send_message(retarget_to_user, ret_question, reply_markup=inl_keyRetarget)
					except Exception as er:
						print(er)
						pass
				update_retarget(data[0], time=datetime.now().replace(microsecond=0))
				user_data.clear()
				print('retarget done')
		else:
			pass

async def main():
	await asyncio.gather(timer(), bot_polling())

if __name__ == "__main__":
	asyncio.run(main())
