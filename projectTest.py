from Framework.military.barracks import get_individual_training_time, get_total_training_time, make_troops_by_amount
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import Server, TROOPSInstance, TroopType, get_TROOPS
from Framework.military.military_utils import enter_academy, enter_barracks
from Framework.account.Login import get_account_password, login


logger = get_projectLogger()

logger.set_debugMode(True)

################### testing stuff ###########################
# AS = get_TROOPS()
# print(AS[TroopType.Axeman].costs)

# print(get_account_password('0bomb13', Server.S10k))
with login(Server.S10k, '0bomb13', False) as sws:
	enter_barracks(sws)
	make_troops_by_amount(sws, TroopType.Clubswinger, 10)
	make_troops_by_amount(sws, TroopType.Spearman, 10)
	# make_troops_by_amount(sws, TroopType.Axeman, 100)
	# make_troops_by_amount(sws, TroopType.Scout, 100)
	make_troops_by_amount(sws, TroopType.Clubswinger, 10)
	make_troops_by_amount(sws, TroopType.Spearman, 10)
	# make_troops_by_amount(sws, TroopType.Axeman, 10)
	# make_troops_by_amount(sws, TroopType.Scout, 100)

	print(str(get_total_training_time(sws)) + " " + "seconds")
	print(get_individual_training_time(sws, TroopType.Clubswinger))

	# while(True):
	# 	pass
	# print(dir(sws))

	# time = sws.getElementsAttribute(XPATH.TROOP_QUEUED % tpType.name, 'text')

	# 	for i in time:
	# 		print(i)