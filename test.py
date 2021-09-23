from Framework.infrastructure.builder import enter_building
from time import sleep
# from Framework.military.academy import research
from Framework.utility.Logger import get_projectLogger
from Framework.military.military_utils import enter_barracks
# enter_academy
from Framework.utility.Constants import Server, TroopType
from Framework.account.Login import login
from Framework.military.barracks import get_total_training_time, reduce_train_time, make_troops_by_amount



logger = get_projectLogger()

if __name__ == "__main__":
	logger.set_debugMode(True)
	with login(Server.S10k, username="0bomb8", headless=False) as sws:
		# assert enter_academy(sws)
		# research(sws, )
		assert enter_barracks(sws)

		# enter_building(a, )

		make_troops_by_amount(sws, TroopType.Axeman, 250)
		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)
		make_troops_by_amount(sws, TroopType.Spearman, 250)
		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)

		if not make_troops_by_amount(sws, TroopType.Scout, 250):
			sleep(1)
			make_troops_by_amount(sws, TroopType.Scout, 250)
		print(str(get_total_training_time(sws)) + ' s')


		if not make_troops_by_amount(sws, TroopType.Clubswinger, 250):
			sleep(1)
			make_troops_by_amount(sws, TroopType.Clubswinger, 250)

		print(str(get_total_training_time(sws)) + ' s')
		sleep(1)

		print(str(get_total_training_time(sws)) + ' s')

		print(str(get_total_training_time(sws)) + ' s')

		
		reduce_train_time(sws)
