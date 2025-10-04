from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import datetime
import telebot
import random
import pickle
import time
import os

tg_bot_token = '8345402206:AAF-qV7lGoiLeee18dooVOU_ZQCSzHi5RBQ'

bot = telebot.TeleBot(tg_bot_token)

log_filename = f'dice_poker_log_{datetime.datetime.now().strftime("%d.%m.%YT%H:%M:%S")}.txt'

admin_id = 6458256191

def make_log(log):
	pass

if not os.path.exists('dump.db'):
	db = {
		'users': {
			
			},

		'games': {
			
			},

		'settings': {
			'players_can_create_rooms': True,
			'admins': [admin_id],
			'last_db_save': None,
		}
		
	}

	make_log('База данных рядом с ботом не обнаружена, создается новая')

else:
	with open('dump.db') as f:
		db = pickle.load(f)

		make_log('Загружена база данных, последнее изменение: {db["settings"]["last_db_save"]}')

def db_save():
	db['settings']['last_db_save'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')

def start_game(game_name):
	for player_id in db['games'][game_name]['players'].keys():
		db['games'][game_name]['stats'][player_id] = {
			'sum_of_1': 0,
			'sum_of_2': 0,
			'sum_of_3': 0,
			'sum_of_4': 0,
			'sum_of_5': 0,
			'sum_of_6': 0,
			'three_of_a_kind': 0,
			'four_of_a_kind': 0,
			'full_house': 0,
			'short_straigth': 0,
			'long_straigth': 0,
			'five_of_a_kind': 0,
			'chance_point': 0,

			'sum_of_1_flag': False,
			'sum_of_2_flag': False,
			'sum_of_3_flag': False,
			'sum_of_4_flag': False,
			'sum_of_5_flag': False,
			'sum_of_6_flag': False,
			'three_of_a_kind_flag': False,
			'four_of_a_kind_flag': False,
			'full_house_flag': False,
			'short_straigth_flag': False,
			'long_straigth_flag': False,
			'five_of_a_kind_flag': False,
			'chance_point_flag': False
		}

	rounds_count = 13

	for game_round in range(rounds_count):
		for player_id, player_nickname in db['games'][game_name]['players'].items():
			db['games'][game_name]['hold'] = []

			db['games'][game_name]['dices'] = {
				'dice_a': random.randint(1,6),
				'dice_b': random.randint(1,6),
				'dice_c': random.randint(1,6),
				'dice_d': random.randint(1,6),
				'dice_e': random.randint(1,6)
			}

			db['games'][game_name]['reroll_counts'] = 3

			db['games'][game_name]['round_num'] = game_round + 1

			db['games'][game_name]['finished_move'] = False

			round_info = f'Раунд {db["games"][game_name]["round_num"]}/13\n\nСписок игроков:\n'

			for nickname in db['games'][game_name]['players'].values():
				round_info += f'\n{list(db['games'][game_name]['players'].values()).index(nickname) + 1}. {nickname}'

			round_info += f'\n\nХод игрока {player_nickname}'

			for player in db['games'][game_name]['players'].keys():
				if player_id != player:
					bot.send_message(player,
						round_info)

			game_string = f'Ход игрока {player_nickname}'
			game_string += f'\n\nОсталось перебросов кубиков: {db["games"][game_name]["reroll_counts"]}'
			game_string += f'\n\nВыпавшие кубики: {db["games"][game_name]["dices"]["dice_a"]}, {db["games"][game_name]["dices"]["dice_b"]}, {db["games"][game_name]["dices"]["dice_c"]}, {db["games"][game_name]["dices"]["dice_d"]}, {db["games"][game_name]["dices"]["dice_e"]}'
			game_string += '\nЗамороженные кубики: '
			game_string += 'нет' if len(db['games'][game_name]['hold']) == 0 else ''
			game_string += f'1-й ' if db["games"][game_name]["dices"]["dice_a"] in db['games'][game_name]['hold'] else ""
			game_string += f'2-й ' if db["games"][game_name]["dices"]["dice_b"] in db['games'][game_name]['hold'] else ""
			game_string += f'3-й ' if db["games"][game_name]["dices"]["dice_c"] in db['games'][game_name]['hold'] else ""
			game_string += f'4-й ' if db["games"][game_name]["dices"]["dice_d"] in db['games'][game_name]['hold'] else ""
			game_string += f'5-й ' if db["games"][game_name]["dices"]["dice_e"] in db['games'][game_name]['hold'] else ""
			game_string += '\n\nВыбери ход кнопками клавиатуры бота!'

			msg = bot.send_message(player_id,
				game_string,
				reply_markup=gen_move_player_markup(db['games'][game_name]['stats'][player_id]))

			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, [db["games"][game_name]["dices"]["dice_a"], db["games"][game_name]["dices"]["dice_b"], db["games"][game_name]["dices"]["dice_c"], db["games"][game_name]["dices"]["dice_d"], db["games"][game_name]["dices"]["dice_e"]])

			while not db['games'][game_name]['finished_move']:
				pass

			db_save()

def proceed_move(message, game_name, player_id, player_nickname, dices):
	if message.text == '❌ Выход из игры (поражение)':
		msg = bot.send_message(player_id,
			'Вы уверены, что хотите покинуть игру? Вам будет автоматически засчитано поражение, очки за эту игру не будут добавлены в статистику!',
			reply_markup=gen_exit_markup())
			
		bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '✅ Я уверен, выхожу из игры':
		db['games'][game_name]['left_players'][player_id] = player_nickname

		del db['games'][game_name]['players'][player_id]
		del db['games'][game_name]['stats'][player_id]

		db['users'][player_id]['active_game'] = False
		db['users'][player_id]['in_room'] = None
		db['users'][player_id]['stats']['games'] += 0

		if db['users'][player_id]['stats']['games'] > 0:
			db['users'][player_id]['stats']['win_rate'] = int(db['users'][player_id]['stats']['games_won'] / db['users'][player_id]['stats']['games'] * 100)

		bot.send_message(message.from_user.id, 
			f'Поражение! Счёт: 0', 
			reply_markup=gen_menu_markup())

	elif message.text == '❌ \'Партия будет доиграна!\' - Лосяш ©':
		msg = bot.send_message(player_id,
			'Желаю удачи!',
			reply_markup=gen_move_player_markup(db['games'][game_name]['stats'][player_id]))
			
		bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '1️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_1_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_1_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_1'] = dices.count(1)

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_1"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_1"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '2️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_2_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_2_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_2'] = dices.count(2) * 2

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_2"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_2"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '3️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_3_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_3_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_3'] = dices.count(3) * 3

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_3"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_3"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '4️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_4_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_4_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_4'] = dices.count(4) * 4

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_4"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_4"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '5️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_5_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_5_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_5'] = dices.count(5) * 5

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_5"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_5"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '6️⃣ Сумма':
		if not db['games'][game_name]['stats'][player_id]['sum_of_6_flag']:
			db['games'][game_name]['stats'][player_id]['sum_of_6_flag'] = True
			db['games'][game_name]['stats'][player_id]['sum_of_6'] = dices.count(6) * 6

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["sum_of_6"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["sum_of_6"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '✨ Три одинаковых':
		if not db['games'][game_name]['stats'][player_id]['three_of_a_kind_flag']:
			db['games'][game_name]['stats'][player_id]['three_of_a_kind_flag'] = True

			for dice in dices:
				if dices.count(dice) == 3:
					db['games'][game_name]['stats'][player_id]['three_of_a_kind'] = dice * 3

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["three_of_a_kind"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["three_of_a_kind"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🔡 Четыре одинаковых':
		if not db['games'][game_name]['stats'][player_id]['four_of_a_kind_flag']:
			db['games'][game_name]['stats'][player_id]['four_of_a_kind_flag'] = True

			for dice in dices:
				if dices.count(dice) == 4:
					db['games'][game_name]['stats'][player_id]['four_of_a_kind'] = dice * 4

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["four_of_a_kind"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["four_of_a_kind"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🍌 Короткий стрит':
		if not db['games'][game_name]['stats'][player_id]['short_straigth_flag']:
			db['games'][game_name]['stats'][player_id]['short_straigth_flag'] = True

			if sorted(list(set(dices)))[:4] == [1,2,3,4] or sorted(list(set(dices)))[1:] == [2,3,4,5]:
				db['games'][game_name]['stats'][player_id]['short_straigth'] = 30

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["short_straigth"]}!')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["short_straigth"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🍆 Длинный стрит':
		if not db['games'][game_name]['stats'][player_id]['long_straigth_flag']:
			db['games'][game_name]['stats'][player_id]['long_straigth_flag'] = True

			if sorted(dices) == [1,2,3,4,5]:
				db['games'][game_name]['stats'][player_id]['long_straigth'] = 40

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["long_straigth"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["long_straigth"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🃏 Фулл Хаус':
		if not db['games'][game_name]['stats'][player_id]['full_house_flag']:
			db['games'][game_name]['stats'][player_id]['full_house_flag'] = True

			if (dices.count(sorted(dices)[0]) == 3 and dices.count(sorted(dices)[-1]) == 2) or (dices.count(sorted(dices)[0]) == 2 and dices.count(sorted(dices)[-1]) == 3):
				db['games'][game_name]['stats'][player_id]['full_house'] = 25

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["full_house"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["full_house"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🏆 Пять одинаковых':
		if not db['games'][game_name]['stats'][player_id]['five_of_a_kind_flag']:
			db['games'][game_name]['stats'][player_id]['five_of_a_kind_flag'] = True

			for dice in dices:
				if dices.count(dice) == 5:
					db['games'][game_name]['stats'][player_id]['five_of_a_kind'] = 50

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["five_of_a_kind"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["five_of_a_kind"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())
		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🟰 Сумма всех':
		if not db['games'][game_name]['stats'][player_id]['chance_point_flag']:
			db['games'][game_name]['stats'][player_id]['chance_point_flag'] = True
			db['games'][game_name]['stats'][player_id]['chance_point'] = sum(dices)

			db['games'][game_name]['finished_move'] = True

			for player in db['games'][game_name]['players'].keys():
				if player != player_id:
					bot.send_message(player,
						f'Игрок {player_nickname} завершил ход!\n\nОчков получено: {db["games"][game_name]["stats"][player_id]["chance_point"]}')

			if db['games'][game_name]['round_num'] != 13:
				bot.send_message(player_id,
					f'Ход завершен, получено {db["games"][game_name]["stats"][player_id]["chance_point"]} очков. Ждите следующего раунда!',
					reply_markup=ReplyKeyboardRemove())

		else:
			msg = bot.send_message(player_id,
				'Этот ход уже использовался!')
			
			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, dices)

	elif message.text == '🎲 Перебросить':
		if db['games'][game_name]['reroll_counts'] > 0:
			db['games'][game_name]['reroll_counts'] -= 1

			db["games"][game_name]["dices"]["dice_a"] = random.randint(1,6) if "dice_a" not in db["games"][game_name]['hold'] else db["games"][game_name]["dices"]["dice_a"]
			db["games"][game_name]["dices"]["dice_b"] = random.randint(1,6) if "dice_b" not in db["games"][game_name]['hold'] else db["games"][game_name]["dices"]["dice_b"]
			db["games"][game_name]["dices"]["dice_c"] = random.randint(1,6) if "dice_c" not in db["games"][game_name]['hold'] else db["games"][game_name]["dices"]["dice_c"]
			db["games"][game_name]["dices"]["dice_d"] = random.randint(1,6) if "dice_d" not in db["games"][game_name]['hold'] else db["games"][game_name]["dices"]["dice_d"]
			db["games"][game_name]["dices"]["dice_e"] = random.randint(1,6) if "dice_e" not in db["games"][game_name]['hold'] else db["games"][game_name]["dices"]["dice_e"]

			game_string = f'Ход игрока {player_nickname}'
			game_string += f'\n\nОсталось перебросов кубиков: {db["games"][game_name]["reroll_counts"]}'
			game_string += f'\n\nВыпавшие кубики: {db["games"][game_name]["dices"]["dice_a"]}, {db["games"][game_name]["dices"]["dice_b"]}, {db["games"][game_name]["dices"]["dice_c"]}, {db["games"][game_name]["dices"]["dice_d"]}, {db["games"][game_name]["dices"]["dice_e"]}'
			game_string += '\nЗамороженные кубики: '
			game_string += f'1-й ' if db["games"][game_name]["dices"]["dice_a"] in db['games'][game_name]['hold'] else ""
			game_string += f'2-й ' if db["games"][game_name]["dices"]["dice_b"] in db['games'][game_name]['hold'] else ""
			game_string += f'3-й ' if db["games"][game_name]["dices"]["dice_c"] in db['games'][game_name]['hold'] else ""
			game_string += f'4-й ' if db["games"][game_name]["dices"]["dice_d"] in db['games'][game_name]['hold'] else ""
			game_string += f'5-й ' if db["games"][game_name]["dices"]["dice_e"] in db['games'][game_name]['hold'] else ""
			game_string += '\n\nВыбери ход кнопками клавиатуры бота!'

			msg = bot.send_message(player_id,
				game_string,
				reply_markup=gen_move_player_markup(db['games'][game_name]['stats'][player_id]))

			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, [db["games"][game_name]["dices"]["dice_a"], db["games"][game_name]["dices"]["dice_b"], db["games"][game_name]["dices"]["dice_c"], db["games"][game_name]["dices"]["dice_d"], db["games"][game_name]["dices"]["dice_e"]])

		else:
			msg = bot.send_message(player_id,
				'Количество перебросов исчерпано!',
				reply_markup=gen_move_player_markup(db['games'][game_name]['stats'][player_id]))

			bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, [db["games"][game_name]["dices"]["dice_a"], db["games"][game_name]["dices"]["dice_b"], db["games"][game_name]["dices"]["dice_c"], db["games"][game_name]["dices"]["dice_d"], db["games"][game_name]["dices"]["dice_e"]])

	elif message.text == '🎲 Управление кубиками':
		msg = bot.send_message(player_id,
			'Меню управления кубиками\n\nНажми кнопку с номером кубика, чтобы его заморозить. Нажми еще раз, чтобы разморозить. Когда закончишь, нажми готово',
			reply_markup=gen_dice_control_markup())
		
		bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

	db_save()

def proceed_dice(message, game_name, player_id, player_nickname):
	if message.text != '✅ Готово':
		if message.text == '1-й':
			if 'dice_a' not in db['games'][game_name]['hold']:
				db['games'][game_name]['hold'].append('dice_a')

				msg = bot.send_message(player_id,
					'Первый кубик заморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)
			else:
				db['games'][game_name]['hold'].remove('dice_a')

				msg = bot.send_message(player_id,
					'Первый кубик разморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		elif message.text == '2-й':
			if 'dice_b' not in db['games'][game_name]['hold']:
				db['games'][game_name]['hold'].append('dice_b')

				msg = bot.send_message(player_id,
					'Второй кубик заморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)
			else:
				db['games'][game_name]['hold'].remove('dice_b')

				msg = bot.send_message(player_id,
					'Второй кубик разморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		elif message.text == '3-й':
			if 'dice_c' not in db['games'][game_name]['hold']:
				db['games'][game_name]['hold'].append('dice_c')

				msg = bot.send_message(player_id,
					'Третий кубик заморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)
			else:
				db['games'][game_name]['hold'].remove('dice_c')

				msg = bot.send_message(player_id,
					'Третий кубик разморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		elif message.text == '4-й':
			if 'dice_d' not in db['games'][game_name]['hold']:
				db['games'][game_name]['hold'].append('dice_d')

				msg = bot.send_message(player_id,
					'Четвертый кубик заморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)
			else:
				db['games'][game_name]['hold'].remove('dice_d')

				msg = bot.send_message(player_id,
					'Четвертый кубик разморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		elif message.text == '5-й':
			if 'dice_e' not in db['games'][game_name]['hold']:
				db['games'][game_name]['hold'].append('dice_e')

				msg = bot.send_message(player_id,
					'Пятый кубик заморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)
			else:
				db['games'][game_name]['hold'].remove('dice_e')

				msg = bot.send_message(player_id,
					'Пятый кубик разморожен!')
		
				bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		else:
			msg = bot.send_message(player_id,
				'Неверная команда!\n\nМеню управления кубиками\n\nНажми кнопку с номером кубика, чтобы его заморозить. Нажми еще раз, чтобы разморозить. Когда закончишь, нажми готово')
		
			bot.register_next_step_handler(msg, proceed_dice, game_name, player_id, player_nickname)

		db_save()

	else:
		game_string = f'Ход игрока {player_nickname}'
		game_string += f'\n\nОсталось перебросов кубиков: {db["games"][game_name]["reroll_counts"]}'
		game_string += f'\n\nВыпавшие кубики: {db["games"][game_name]["dices"]["dice_a"]}, {db["games"][game_name]["dices"]["dice_b"]}, {db["games"][game_name]["dices"]["dice_c"]}, {db["games"][game_name]["dices"]["dice_d"]}, {db["games"][game_name]["dices"]["dice_e"]}'
		game_string += '\nЗамороженные кубики: '
		game_string += f'1-й ' if 'dice_a' in db['games'][game_name]['hold'] else ""
		game_string += f'2-й ' if 'dice_b' in db['games'][game_name]['hold'] else ""
		game_string += f'3-й ' if 'dice_c' in db['games'][game_name]['hold'] else ""
		game_string += f'4-й ' if 'dice_d' in db['games'][game_name]['hold'] else ""
		game_string += f'5-й ' if 'dice_e' in db['games'][game_name]['hold'] else ""
		game_string += '\n\nВыбери ход кнопками клавиатуры бота!'

		msg = bot.send_message(player_id,
			game_string,
			reply_markup=gen_move_player_markup(db['games'][game_name]['stats'][player_id]))

		bot.register_next_step_handler(msg, proceed_move, game_name, player_id, player_nickname, [db["games"][game_name]["dices"]["dice_a"], db["games"][game_name]["dices"]["dice_b"], db["games"][game_name]["dices"]["dice_c"], db["games"][game_name]["dices"]["dice_d"], db["games"][game_name]["dices"]["dice_e"]])

def finish_game(game_name):
	scores = {}

	for player_id, player_nickname in db['games'][game_name]['players'].items():
		player_total_score = 0

		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_1']
		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_2']
		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_3']
		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_4']
		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_5']
		player_total_score += db['games'][game_name]['stats'][player_id]['sum_of_6']
		player_total_score += db['games'][game_name]['stats'][player_id]['three_of_a_kind']
		player_total_score += db['games'][game_name]['stats'][player_id]['four_of_a_kind']
		player_total_score += db['games'][game_name]['stats'][player_id]['full_house']
		player_total_score += db['games'][game_name]['stats'][player_id]['short_straigth']
		player_total_score += db['games'][game_name]['stats'][player_id]['long_straigth']
		player_total_score += db['games'][game_name]['stats'][player_id]['five_of_a_kind']
		player_total_score += db['games'][game_name]['stats'][player_id]['chance_point']

		scores[player_id] = {
			'nickname': player_nickname,
			'score': player_total_score
		}

	if db['users'][player_id]['stats']['games'] > 0:
		db['users'][player_id]['stats']['win_rate'] = int(db['users'][player_id]['stats']['games_won'] / db['users'][player_id]['stats']['games'] * 100)

	scores = {k: v for k, v in reversed(sorted(scores.items(), key=lambda item: item[1]['score']))}

	winner_id, winner_nickname = list(scores.keys())[0], scores[list(scores.keys())[0]]['nickname']

	final_string = f'Игра окончена! Победитель: 🎉{winner_nickname}🎉'
	final_string += '\n\nИтоги игры:'

	for player_id, score in scores.items():
		final_string += f'\n{list(scores.keys()).index(player_id) + 1}. {scores[player_id]["nickname"]} - {scores[player_id]["score"]}'

	for player_id, player_nickname in db['games'][game_name]['players'].items():
		db['users'][player_id]['active_game'] = False
		db['users'][player_id]['in_room'] = None
		db['users'][player_id]['stats']['games'] += 1

		db['users'][player_id]['stats']['total_scores'] += scores[player_id]['score']

		if player_id == winner_id:
			db['users'][player_id]['stats']['games_won'] += 1

		db['users'][player_id]['stats']['win_rate'] = int(db['users'][player_id]['stats']['games_won'] / db['users'][player_id]['stats']['games'] * 100)

		bot.send_message(player_id, 
			final_string + '\n\nПоздравляем с победой!' if player_id == winner_id else final_string + '',
			reply_markup=gen_menu_markup())

	del db['games'][game_name]
	del scores
	del winner_id
	del winner_nickname
	del final_string

	db_save()

def get_list_of_nicknames():
	return [db['users'][k]['nickname'] for k in db['users'].keys()]

def get_list_of_rooms():
	return [k for k in db['games'].keys()]

def get_profile_data(user_id):
	profile_string = f'Данные об игроке {db["users"][user_id]["nickname"]}'
	profile_string += f'\nЗарегистрировался: {db["users"][user_id]["registered_at"]}'
	profile_string += f'\n\nСыграно игр: {db["users"][user_id]['stats']["games"]}'
	profile_string += f'\nИз них выиграно: {db["users"][user_id]['stats']["games_won"]}'
	profile_string += f'\nПроцент побед: {db["users"][user_id]['stats']["win_rate"] if db["users"][user_id]['stats']["win_rate"] else "-"}'
	profile_string += f'\n\nВсего заработано очков: {db["users"][user_id]['stats']["total_scores"]}'

	return profile_string

def get_lobby_data(game_name, password, players, game_owner):
	game_string = f'Лобби игры {game_name}'
	game_string += f'\n\nПароль: {password}'
	game_string += '\n\nСписок игроков:'

	for player in players:
		if player == game_owner:
			game_string += f'\n🌟 {player}'
		else:
			game_string += f'\n{player}'

	return game_string

def gen_return_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	markup.add('🔙 Назад в меню')

	return markup

def gen_exit_markup():
	markup = ReplyKeyboardMarkup()

	markup.add('✅ Я уверен, выхожу из игры', '❌ \'Партия будет доиграна!\' - Лосяш ©')

	return markup

def gen_menu_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	markup.add('🆕 Создать игру', '➕ Присоединиться к игре')
	markup.add('👨‍🦲 Профиль')

	return markup

def gen_lobby_player_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	markup.add('❌ Покинуть комнату')

	return markup

def gen_lobby_owner_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	markup.add('✅ Начать игру', '❌ Удалить комнату')

	return markup

def gen_games_list_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	available_games = list(db['games'].keys())

	for game in available_games:
		if db['games'][game]['game_started']:
			available_games.remove(game)

	for l in [available_games[k:k + 3] for k in range(0, len(available_games), 3)]:
		if len(l) == 3:
			markup.add(l[0], l[1], l[2])

		elif len(l) == 2:
			markup.add(l[0], l[1])

		else:
			markup.add(l[0])

	markup.add('🔙 Назад в меню')

	return markup

def gen_move_player_markup(game_stats):
	markup = ReplyKeyboardMarkup(resize_keyboard=True)

	list_of_move_buttons = {
		'1️⃣ Сумма': 'sum_of_1_flag', 
		'2️⃣ Сумма': 'sum_of_2_flag', 
		'3️⃣ Сумма': 'sum_of_3_flag',
		'4️⃣ Сумма': 'sum_of_4_flag', 
		'5️⃣ Сумма': 'sum_of_5_flag', 
		'6️⃣ Сумма': 'sum_of_6_flag',
		'✨ Три одинаковых': 'three_of_a_kind_flag', 
		'🔡 Четыре одинаковых': 'four_of_a_kind_flag', 
		'🍌 Короткий стрит': 'short_straigth_flag', 
		'🍆 Длинный стрит': 'long_straigth_flag',
		'🃏 Фулл Хаус': 'full_house_flag', 
		'🏆 Пять одинаковых': 'five_of_a_kind_flag', 
		'🟰 Сумма всех': 'chance_point_flag'
	}

	for button_title, button_state in list_of_move_buttons.copy().items():
		if game_stats[button_state]:
			del list_of_move_buttons[button_title]

	list_of_available_buttons = list(list_of_move_buttons.keys())

	for l in [list_of_available_buttons[k:k + 3] for k in range(0, len(list_of_available_buttons), 3)]:
		if len(l) == 3:
			markup.add(l[0], l[1], l[2])

		elif len(l) == 2:
			markup.add(l[0], l[1])

		else:
			markup.add(l[0])

	markup.add('🎲 Перебросить', '🎲 Управление кубиками', '❌ Выход из игры (поражение)')

	return markup

def gen_dice_control_markup():
	markup = ReplyKeyboardMarkup(resize_keyboard=True)
	markup.add('1-й', '2-й', '3-й')
	markup.add('4-й', '5-й', '✅ Готово')

	return markup

@bot.message_handler(func=lambda message: message.text == '🔙 Назад в меню')
@bot.message_handler(commands=['start'])
def init_bot(message):
	if message.from_user.id not in db['users'].keys():
		msg = bot.send_message(message.from_user.id, 
			'Шалом! Введи свой ник. Он должен быть уникальным и длиной от 3 до 15 символов')

		bot.register_next_step_handler(msg, register_user)

	else:
		bot.send_message(message.from_user.id, 
			f'И снова шалом, {db["users"][message.from_user.id]["nickname"]}!', 
			reply_markup=gen_menu_markup())

@bot.message_handler(func=lambda message: message.text == '!выкл')
@bot.message_handler(commands=['disable_bot'])
def disable_bot(message):
	if message.from_user.id in db['settings']['admins']:
		db['settings']['players_can_create_rooms'] = False

		bot.send_message(message.from_user.id, 
			'Команда принята, бот будет отключён как только закончатся все активные игры')

		while len(list(db['games'].keys())) != 0:
			pass

		bot.send_message(message.from_user.id, 
			'Активные игры закончились, завершаю работу бота!')

		db['settings']['players_can_create_rooms'] = True

		db_save()

		exit('Бот отключён!')

def register_user(message):
	if len(message.text) > 15:
		msg = bot.send_message(message.from_user.id, 
			'Слишком длинный ник!\n\nНикнейм должен быть уникальным и длиной от 3 до 15 символов')

		bot.register_next_step_handler(msg, register_user)

	elif len(message.text) < 3:
		msg = bot.send_message(message.from_user.id, 
			'Слишком короткий ник!\n\nНикнейм должен быть уникальным и длиной от 3 до 15 символов')

		bot.register_next_step_handler(msg, register_user)

	elif message.text in get_list_of_nicknames():
		msg = bot.send_message(message.from_user.id, 
			'Такой ник уже есть!\n\nНикнейм должен быть уникальным и длиной от 3 до 15 символов')

		bot.register_next_step_handler(msg, register_user)

	else:
		db['users'][message.from_user.id] = {'nickname': message.text, 
			'active_game': None,
			'in_room': None,
			'registered_at': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),

			'stats': {
				'games': 0,
				'games_won': 0,
				'win_rate': 0,
				'total_scores': 0
			}
		}

		db_save()

		bot.send_message(message.from_user.id, 
			f'Добро пожаловать, {db["users"][message.from_user.id]["nickname"]}!', 
			reply_markup=gen_menu_markup())

@bot.message_handler(func=lambda message: message.text == '👨‍🦲 Профиль')
def show_profile(message):
	if message.from_user.id in db['users'].keys():
		bot.send_message(message.from_user.id, 
			get_profile_data(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == '🆕 Создать игру')
def request_new_game_name(message):
	if message.from_user.id in db['users'].keys():
		if not db['settings']['players_can_create_rooms']:
			bot.send_message(message.from_user.id, 
				'Бот готовится к отключению в связи с тех. обслуживанием. Создание новых комнат недоступно, бот будет отключен по завершению всех активных игр. Простите и возвращайтесь позже :(')

		else:
			if db['users'][message.from_user.id]['active_game']:
				bot.send_message(message.from_user.id, 
					'Активная игра уже есть!')

			else:
				msg = bot.send_message(message.from_user.id, 
					'Введи название комнаты, от 3 до 15 символов', 
					reply_markup=gen_return_markup())

				bot.register_next_step_handler(msg, request_new_game_code)

def request_new_game_code(message):
	if message.text == '🔙 Назад в меню':
		bot.send_message(message.from_user.id, 
			f'И снова шалом, {db["users"][message.from_user.id]["nickname"]}!', 
			reply_markup=gen_menu_markup())

	elif len(message.text) > 15:
		msg = bot.send_message(message.from_user.id, 
			'Слишком длинное название!\n\nВведи название комнаты, от 3 до 15 символов', 
			reply_markup=gen_return_markup())

		bot.register_next_step_handler(msg, request_new_game_code)

	elif len(message.text) < 3:
		msg = bot.send_message(message.from_user.id, 
			'Слишком короткое название!\n\nВведи название комнаты, от 3 до 15 символов', 
			reply_markup=gen_return_markup())

		bot.register_next_step_handler(msg, request_new_game_code)

	elif message.text in get_list_of_rooms():
		msg = bot.send_message(message.from_user.id, 
			'Такая комната уже есть!\n\nВведи название комнаты, от 3 до 15 символов', 
			reply_markup=gen_return_markup())

		bot.register_next_step_handler(msg, request_new_game_code)

	else:
		msg = bot.send_message(message.from_user.id, 
			'Введи пароль для комнаты, 4 цифры', 
			reply_markup=gen_return_markup())

		bot.register_next_step_handler(msg, create_game, message.text)

def create_game(message, game_name):
	if message.text == '🔙 Назад в меню':
		bot.send_message(message.from_user.id, 
			f'И снова шалом, {db["users"][message.from_user.id]["nickname"]}!', 
			reply_markup=gen_menu_markup())

	elif len(message.text) != 4:
		msg = bot.send_message(message.from_user.id, 
			'Неверная длина пароля!\n\nВведи пароль для комнаты, 4 цифры', 
			reply_markup=gen_return_markup())

		bot.register_next_step_handler(msg, create_game, game_name)

	else:
		try:
			db['games'][game_name] = {
				'players': {message.from_user.id: db['users'][message.from_user.id]['nickname']},
				'left_players': {},
				'owner': message.from_user.id,
				'password': int(message.text),
				'game_started': False,
				'stats': {}
			}

			db['users'][message.from_user.id]['active_game'] = True
			db['users'][message.from_user.id]['in_room'] = game_name

			bot.send_message(message.from_user.id, 
				get_lobby_data(game_name, 
					message.text, 
					[db['users'][message.from_user.id]['nickname']],
					db['users'][message.from_user.id]['nickname']),
					reply_markup=gen_lobby_owner_markup()
				)

			db_save()

		except ValueError:
			msg = bot.send_message(message.from_user.id, 
				'Пароль должен состоять только из цифр!\n\nВведи пароль для комнаты, 4 цифры',
				reply_markup=gen_return_markup())

			bot.register_next_step_handler(msg, create_game, game_name)

@bot.message_handler(func=lambda message: message.text == '➕ Присоединиться к игре')
def request_game_name(message):
	if message.from_user.id in db['users'].keys():
		if db['users'][message.from_user.id]['active_game']:
			bot.send_message(message.from_user.id, 
				'Активная игра уже есть!')

		else:
			bot.send_message(message.from_user.id, 
				'Выбери комнату из списка при помощи клавиатуры бота', 
				reply_markup=gen_games_list_markup())

@bot.message_handler(func=lambda message: message.text in get_list_of_rooms())
def request_game_password(message):
	if message.from_user.id in db['users'].keys():
		if db['users'][message.from_user.id]['active_game']:
			bot.send_message(message.from_user.id, 'Активная игра уже есть!')

		else:
			if message.text not in db['games'].keys():
				bot.send_message(message.from_user.id, 
					'Такой комнаты уже не существует!\n\nВыбери комнату из списка при помощи клавиатуры бота', 
					reply_markup=gen_games_list_markup())

			elif db['games'][message.text]['game_started']:
				bot.send_message(message.from_user.id, 
					'Игра в этой комнате уже началась, присоединиться к ней не получится!\n\nВыбери комнату из списка при помощи клавиатуры бота', 
					reply_markup=gen_games_list_markup())

			else:
				msg = bot.send_message(message.from_user.id, 
					'🔐 Введи пароль от комнаты', 
					reply_markup=gen_return_markup())

				bot.register_next_step_handler(msg, join_game, message.text)

def join_game(message, game_name):
	if message.text == '🔙 Назад в меню':
		bot.send_message(message.from_user.id, 
			f'И снова шалом, {db["users"][message.from_user.id]["nickname"]}!', 
			reply_markup=gen_menu_markup())

	elif game_name not in db['games'].keys():
		bot.send_message(message.from_user.id, 
			'Такой комнаты уже не существует!\n\nВыбери комнату из списка при помощи клавиатуры бота', 
			reply_markup=gen_games_list_markup())

	else:
		try:
			if int(message.text) != db['games'][game_name]['password']:
				msg = bot.send_message(message.from_user.id, 
					'Неверный пароль!\n\n🔐 Введи пароль от комнаты', 
					reply_markup=gen_return_markup())

				bot.register_next_step_handler(msg, join_game, game_name)

			else:
				for old_player_id in db['games'][game_name]['players'].keys():
					bot.send_message(old_player_id, 
						f'Игрок {db["users"][message.from_user.id]["nickname"]} присоединился к лобби!')

				db['games'][game_name]['players'][message.from_user.id] = db['users'][message.from_user.id]['nickname']
				db['users'][message.from_user.id]['active_game'] = True
				db['users'][message.from_user.id]['in_room'] = game_name

				for player_id, player_nickname in db['games'][game_name]['players'].items():
					bot.send_message(player_id, 
						get_lobby_data(game_name, 
							message.text, 
							db['games'][game_name]['players'].values(),
							db['users'][db['games'][game_name]['owner']]['nickname']),
							reply_markup=gen_lobby_owner_markup() if db['games'][game_name]['owner'] == player_id else gen_lobby_player_markup())

				db_save()

		except ValueError:
			msg = bot.send_message(message.from_user.id, 
				'Пароль должен состоять только из цифр!\n\nВведи пароль для комнаты, 4 цифры',
				reply_markup=gen_return_markup())

			bot.register_next_step_handler(msg, join_game, game_name)

@bot.message_handler(func=lambda message: message.text == '❌ Покинуть комнату')
def request_game_name(message):
	if message.from_user.id in db['users'].keys():
		if not db['users'][message.from_user.id]['in_room']:
			pass
		else:
			game_name = db['users'][message.from_user.id]['in_room']

			del db['games'][game_name]['players'][message.from_user.id]

			db['users'][message.from_user.id]['active_game'] = False
			db['users'][message.from_user.id]['in_room'] = None

			bot.send_message(message.from_user.id, 
				f'Комната {game_name} покинута!', 
				reply_markup=gen_menu_markup())

			for player_id in db['games'][game_name]['players'].keys():
				bot.send_message(player_id, 
					f'Игрок {db["users"][message.from_user.id]["nickname"]} покинул лобби!')

				bot.send_message(player_id, 
					get_lobby_data(game_name, 
						db['games'][game_name]['password'],
						db['games'][game_name]['players'].values(),
						db['users'][db['games'][game_name]['owner']]['nickname']),
						reply_markup=gen_lobby_owner_markup() if db['games'][game_name]['owner'] == player_id else gen_lobby_player_markup())

			db_save()

@bot.message_handler(func=lambda message: message.text == '✅ Начать игру')
def request_game_name(message):
	if message.from_user.id in db['users'].keys():
		if not db['users'][message.from_user.id]['in_room']:
			bot.send_message(message.from_user.id, 
				'Ты не создал никакую комнату!')

		elif message.from_user.id != db['games'][db['users'][message.from_user.id]['in_room']]['owner']:
			bot.send_message(message.from_user.id, 
				'Ты не владелец комнаты!')

		else:
			game_name = db['users'][message.from_user.id]['in_room']

			for player_id in db['games'][game_name]['players'].keys():
				bot.send_message(player_id, 
					f'Игра начинается!\n\nОжидайте своего хода...',
					reply_markup=ReplyKeyboardRemove())

			db['games'][game_name]['game_started'] = True

			db_save()

			start_game(game_name)

			finish_game(game_name)

@bot.message_handler(func=lambda message: message.text == '❌ Удалить комнату')
def request_game_name(message):
	if message.from_user.id in db['users'].keys():
		if not db['users'][message.from_user.id]['in_room']:
			bot.send_message(message.from_user.id, 
				'Ты не создал никакую комнату!')

		elif message.from_user.id != db['games'][db['users'][message.from_user.id]['in_room']]['owner']:
			bot.send_message(message.from_user.id, 
				'Ты не владелец комнаты!')

		else:
			game_name = db['users'][message.from_user.id]['in_room']

			for player_id in db['games'][game_name]['players'].keys():
				bot.send_message(player_id, 
					f'Комната {game_name} была удалена!', 
					reply_markup=gen_menu_markup())

				db['users'][player_id]['active_game'] = False
				db['users'][player_id]['in_room'] = None

			del db['games'][game_name]

			db_save()

bot.infinity_polling()