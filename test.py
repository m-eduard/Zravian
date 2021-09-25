from Framework.infrastructure.builder import enter_building
from time import sleep
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Server, TroopType, BuildingType
from Framework.account.Login import login
from Framework.military.barracks import get_total_training_time, reduce_train_time, make_troops_by_amount



logger = get_projectLogger()

if __name__ == "__main__":
	logger.set_debugMode(True)
	with login(Server.S10k, username="0bomb8", headless=False) as sws:
		enter_building(sws, BuildingType.Barracks)

		ls = ['Clubswinger', 'Axeman', 'Spearman', 'Scout']
		for i in ls:
		    print(i)
	

		make_troops_by_amount(sws, TroopType.Axeman, 1000)
		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)
		make_troops_by_amount(sws, TroopType.Spearman, 1000)
		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)

		if not make_troops_by_amount(sws, TroopType.Scout, 1000):
			sleep(1)
			make_troops_by_amount(sws, TroopType.Scout, 1000)
		print(str(get_total_training_time(sws)) + ' s')


		if not make_troops_by_amount(sws, TroopType.Clubswinger, 1000):
			sleep(1)
			make_troops_by_amount(sws, TroopType.Clubswinger, 1000)

		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)

		# make_troops_by_amount(sws, TroopType.Clubswinger, 1000)
		# sleep(1)
		
		# make_troops_by_amount(sws, TroopType.Axeman, 1000)
		# make_troops_by_amount(sws, TroopType.Spearman, 400)

		# sleep(1)
		# make_troops_by_amount(sws, TroopType.Scout, 200)

		print(str(get_total_training_time(sws)) + ' s')

		# reduce_train_time(sws)

		print(str(get_total_training_time(sws)) + ' s')

		
		#reduce_train_time(sws)
