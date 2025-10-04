import prettytable
import random
import time
import os

class Game:
	def __init__(self, list_of_players):
		self.list_of_players = list_of_players

	def show_logo(self):
		clear_screen()

		print('''
		                	       (( _______
		                     _______     /\\O    O\\
		                    /O     /\\   /  \\      \\
		                   /   O  /O \\ / O  \\O____O\\ ))
		                ((/_____O/    \\     /O     /
		                  \\O    O\\    / \\  /   O  /
		                   \\O    O\\ O/   \\/_____O/
		                    \\O____O\\/ ))          ))
		                  ((\n\n\n''')

		for k in '                 DICE POKER GAME\n':
			time.sleep(0.04)
			print(k, end='', flush=True)


		for k in '                         BY OLEJAVOEVO':
			time.sleep(0.04)
			print(k, end='', flush=True)

		for k in '\nLoading game...':
			time.sleep(0.06)
			print(k, end='', flush=True)

		time.sleep(2)

	def generate_ascii_table(self, move, nickname, rerolls_count):
		table = prettytable.prettytable.PrettyTable()
		table.title = f'Dice Poker | PLAYER: {nickname} | MOVE: {move} | RE-ROLLS: {rerolls_count}'

		fields = ['Avaliable Moves', 'Points']

		for k in self.list_of_players:
			fields.append(f'[{k.sum_of_points()}] - {k.nickname}')

		table.field_names = fields
		table.align['Score Fields'] = 'l'

		table.add_row(['[s1] Sum of 1', 'Dices * 1'] + [str(k.sum_of_1) + '.' if k.sum_of_1_flag else k.sum_of_1 for k in self.list_of_players])
		table.add_row(['[s2] Sum of 2', 'Dices * 2'] + [str(k.sum_of_2) + '.' if k.sum_of_2_flag else k.sum_of_2 for k in self.list_of_players])
		table.add_row(['[s3] Sum of 3', 'Dices * 3'] + [str(k.sum_of_3) + '.' if k.sum_of_3_flag else k.sum_of_3 for k in self.list_of_players])
		table.add_row(['[s4] Sum of 4', 'Dices * 4'] + [str(k.sum_of_4) + '.' if k.sum_of_4_flag else k.sum_of_4 for k in self.list_of_players])
		table.add_row(['[s5] Sum of 5', 'Dices * 5'] + [str(k.sum_of_5) + '.' if k.sum_of_5_flag else k.sum_of_5 for k in self.list_of_players])
		table.add_row(['[s6] Sum of 6', 'Dices * 6'] + [str(k.sum_of_6) + '.' if k.sum_of_6_flag else k.sum_of_6 for k in self.list_of_players])
		table.add_row(['[th] Three of a kind', 'Value * 3'] + [str(k.three_of_a_kind) + '.' if k.three_of_a_kind_flag else k.three_of_a_kind for k in self.list_of_players])
		table.add_row(['[fo] Four of a kind', 'Value * 4'] + [str(k.four_of_a_kind) + '.' if k.four_of_a_kind_flag else k.five_of_a_kind for k in self.list_of_players])
		table.add_row(['[fh] Full house', '25'] + [str(k.full_house) + '.' if k.full_house_flag else k.full_house for k in self.list_of_players])
		table.add_row(['[ss] Short street', '30'] + [str(k.short_street) + '.' if k.short_street_flag else k.short_street for k in self.list_of_players])
		table.add_row(['[ls] Long street', '40'] + [str(k.long_street) + '.' if k.long_street_flag else k.long_street for k in self.list_of_players])
		table.add_row(['[fi] Five of a kind', '50'] + [str(k.five_of_a_kind) + '.' if k.five_of_a_kind_flag else k.five_of_a_kind for k in self.list_of_players])
		table.add_row(['[cp] Chance point', 'Sum of dices'] + [str(k.chance_point) + '.' if k.chance_point_flag else k.chance_point for k in self.list_of_players])

		return table

	def show_error(self, error_text):
		clear_screen()

		print(error_text)

		leave_error = input('Press enter to continue game...')

	def game_over(self):
		scores = {}

		table = prettytable.prettytable.PrettyTable()
		table.title = f'!!!GAME OVER!!!'

		table.field_names = ['Nickname', 'Score']

		for k in self.list_of_players:
			scores[k.nickname] = k.sum_of_points()

		scores = {k: v for k, v in reversed(sorted(scores.items(), key=lambda item: item[1]))}

		clear_screen()
		
		for k,v in scores.items():
			table.add_row([k, v])

		for k in table.__str__():
			time.sleep(0.04)
			print(k, end='', flush=True)

class Player:
	def __init__(self, nickname):
		self.nickname = nickname

		# поля
		self.sum_of_1 = 0
		self.sum_of_2 = 0
		self.sum_of_3 = 0
		self.sum_of_4 = 0
		self.sum_of_5 = 0
		self.sum_of_6 = 0

		self.three_of_a_kind = 0
		self.four_of_a_kind = 0
		self.full_house = 0
		self.short_street = 0
		self.long_street = 0
		self.five_of_a_kind = 0
		self.chance_point = 0

		self.sum_of_1_flag = False
		self.sum_of_2_flag = False
		self.sum_of_3_flag = False
		self.sum_of_4_flag = False
		self.sum_of_5_flag = False
		self.sum_of_6_flag = False

		self.three_of_a_kind_flag = False
		self.four_of_a_kind_flag = False
		self.full_house_flag = False
		self.short_street_flag = False
		self.long_street_flag = False
		self.five_of_a_kind_flag = False
		self.chance_point_flag = False

	def sum_of_points(self):
		return self.sum_of_1 + self.sum_of_2 + self.sum_of_3 + self.sum_of_4 + self.sum_of_5 + self.sum_of_6 + self.three_of_a_kind + self.four_of_a_kind + self.full_house + self.short_street + self.long_street + self.five_of_a_kind + self.chance_point

def clear_screen():
	os.system('cls') if os.name == 'nt' else os.system('clear')

def start_game(game):
	for k in range(13):
		for player in game.list_of_players:

			move_commands = ['s1', 's2', 's3', 's4', 's5', 's6', 'th', 'fo', 'fh', 'ss', 'ls', 'fi', 'cp']

			rerolls_count = 3
			hold = []
			finished_move = False

			dice_a = random.randint(1,6)
			dice_b = random.randint(1,6)
			dice_c = random.randint(1,6)
			dice_d = random.randint(1,6)
			dice_e = random.randint(1,6)

			while not finished_move:

				dices_string = f'''  +---+ +---+ +---+ +---+ +---+
  | {dice_a} | | {dice_b} | | {dice_c} | | {dice_d} | | {dice_e} |
  +---+ +---+ +---+ +---+ +---+'''

				table = game.generate_ascii_table(k, player.nickname, rerolls_count)

				clear_screen()

				print(table)

				print(dices_string)

				print(f'\n  HOLD: {hold}')

				command = input('command> ')

				if command.lower() == 'help':

					game.show_error('''HELP\n\n> hold / h (a | b | c | d | e) - hold dice
	> unhold / u (a | b | c | d | e) - unhold dice
	> reroll / r- reroll all unholded dices
	> [MV] - make a move. MV is 2 letters in box
	nearly required score field, for example: fk
	> help - show this manual
	> quit / q - quit game''')

				elif command.lower().startswith('h'):
					if command.lower().split()[-1] not in ['a', 'b', 'c', 'd', 'e']:
						game.show_error('You should select dice from list: a, b, c, d, e!')

					else:
						if command.lower().split()[-1] not in hold:
							eval(f'hold.append(command.lower().split()[-1])')

						else:
							eval(f'hold.remove(command.lower().split()[-1])')

				elif command.lower().startswith('u'):
					if command.lower().split()[-1] not in ['a', 'b', 'c', 'd', 'e']:
						game.show_error('You should select dice from list: a, b, c, d, e!')

					else:
						if command.lower().split()[-1] not in hold:
							print('This dice not in hold!')

							time.sleep(3)

						else:
							eval(f'hold.remove(command.lower().split()[-1])')

				elif command.lower().startswith('r'):
					if rerolls_count > 0:
						rerolls_count -= 1

						dice_a = dice_a if 'a' in hold else random.randint(1,6)
						dice_b = dice_b if 'b' in hold else random.randint(1,6)
						dice_c = dice_c if 'c' in hold else random.randint(1,6)
						dice_d = dice_d if 'd' in hold else random.randint(1,6)
						dice_e = dice_e if 'e' in hold else random.randint(1,6)
					else:
						game.show_error('Out of rerolls!')

						time.sleep(3)

				elif command.lower().startswith('q'):
					clear_screen()

					exit('Goodbye!')

				elif command.lower() in move_commands:
					if command.lower() == 's1':
						if player.sum_of_1 == 0 and not player.sum_of_1_flag:
							player.sum_of_1 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(1)

							player.sum_of_1_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 's2':
						if player.sum_of_2 == 0 and not player.sum_of_2_flag:
							player.sum_of_2 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(2) * 2

							player.sum_of_2_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 's3':
						if player.sum_of_3 == 0 and not player.sum_of_3_flag:
							player.sum_of_3 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(3) * 3

							player.sum_of_3_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 's4':
						if player.sum_of_4 == 0 and not player.sum_of_4_flag:
							player.sum_of_4 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(4) * 4

							player.sum_of_4_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 's5':
						if player.sum_of_5 == 0 and not player.sum_of_5_flag:
							player.sum_of_5 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(5) * 5

							player.sum_of_5_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 's6':
						if player.sum_of_6 == 0 and not player.sum_of_6_flag:
							player.sum_of_6 = [dice_a, dice_b, dice_c, dice_d, dice_e].count(6) * 6

							player.sum_of_6_flag = True
							finished_move = True
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'th':
						if player.three_of_a_kind == 0 and not player.three_of_a_kind_flag:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							for dice in dices:
								if dices.count(dice) == 3:
									player.three_of_a_kind = dice * 3

									break

							player.three_of_a_kind_flag = True
							finished_move = True
								
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'fo':
						if player.four_of_a_kind == 0 and not player.four_of_a_kind_flag:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							for dice in dices:
								if dices.count(dice) == 4:
									player.four_of_a_kind = dice * 4

									break

							player.four_of_a_kind_flag = True
							finished_move = True
								
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'fh':
						if player.full_house == 0 and not player.full_house_flag:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							if (dices.count(sorted(dices)[0]) == 3 and dices.count(sorted(dices)[-1]) == 2) or (dices.count(sorted(dices)[0]) == 2 and dices.count(sorted(dices)[-1]) == 3):
								player.full_house = 25

							player.full_house_flag = True
							finished_move = True

						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'ss':
						if player.short_street == 0 and not player.short_street:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							if sorted(list(set(dices)))[:4] == [1,2,3,4] or sorted(list(set(dices)))[1:] == [2,3,4,5]:
								player.short_street = 30
								
							player.short_street_flag = True
							finished_move = True

						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'ls':
						if player.long_street == 0 and not player.long_street:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							if sorted(dices) == [1,2,3,4,5]:
								player.long_street = 40

							player.long_street_flag = True
							finished_move = True

						else:
							game.show_error('You already used this field for move!')


					elif command.lower() == 'fi':
						if player.five_of_a_kind == 0 and not player.five_of_a_kind_flag:
							dices = [dice_a, dice_b, dice_c, dice_d, dice_e]

							for dice in dices:
								if dices.count(dice) == 5:
									player.five_of_a_kind = 50

									break

							player.five_of_a_kind_flag = True
							finished_move = True
								
						else:
							game.show_error('You already used this field for move!')

					elif command.lower() == 'cp':
						if player.chance_point == 0 and not player.chance_point_flag:
							player.chance_point = sum([dice_a, dice_b, dice_c, dice_d, dice_e])

							player.chance_point_flag = True
							finished_move = True
								
						else:
							game.show_error('You already used this field for move!')

				else:
					game.show_error('''HELP\n\n> hold (a | b | c | d | e) - hold dice
	> unhold (a | b | c | d | e) - unhold dice
	> reroll - reroll all unholded dices
	> [MV] - make a move. MV is 2 letters in box
	nearly required score field, for example: fk
	> help - show this manual''')

	game.game_over()

try:
	players_count = input('Enter players count: ')
	players_count = int(players_count)
except:
	players_count = input('\n\nPlayers count should be a number\nEnter players count: ')

players_nicknames = []
players = []

for k in range(players_count):
	nickname = input('Enter nickname: ')

	players.append(Player(nickname))

game = Game(players)

game.show_logo()

start_game(game)