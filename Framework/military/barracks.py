from Framework.infrastructure.builder import check_building_page_title, time_to_seconds
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def make_troops_by_amount(sws : SWS, tpType : TroopType, amount : int):
	"""
	Trains Troops by specified type and amount.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.
		- amount: Denotes the amount of troops to be trained.

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = False
	if check_building_page_title(sws, BuildingType.Barracks):
		maxUnits = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, 'text')
		# The number is between parantheses
		if maxUnits:
			try:
				maxUnits = int(maxUnits[1:-1])
			except ValueError:
				logger.error(f'In make_troops_by_amount: {maxUnits[1:-1]} is not int')
				maxUnits = None
		if maxUnits and maxUnits > amount:
			if sws.sendKeys(XPATH.TROOP_INPUT_BOX % TROOPS[tpType].name, amount):
				if sws.clickElement(XPATH.TROOP_TRAIN_BTN, refresh=True):
					logger.success(f'In function make_troops_by_amount: {amount} {TROOPS[tpType].name} were trained')
					status = True
				else:
					logger.error('In function make_troops_by_amount: Failed to press train')
			else:
				logger.error('In function make_troops_by_amount: Failed to insert amount of troops')
		else:
			logger.warning('In function make_troops_by_amount: Not enough resources')
	else:
		logger.error('In function make_troops_by_amount: Not barracks screen')

	return status

	## Dupa ce se apasa train, 2 functii suplimentare ce obtin total duration si refresh time-ul
	## O functie care apasa pe reduce troop training time
	## La final, un test pt barracks->

def reduce_train_time(sws : SWS):
	"""
	Presses the "Reduce the troop training time" button on Barracks screen.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = False
	if check_building_page_title(sws, BuildingType.Barracks):
		if sws.isVisible(XPATH.TROOP_REDUCE_TIME_BTN):
			gold = sws.getElementAttribute(XPATH.GOLD_AMOUNT, 'text')
			print(gold)
			if gold:
				try:
					gold = int(gold)
				except ValueError:
					logger.error(f'In reduce_train_time: {gold} is not int')
					gold = None
			goldReq = 10
			if gold and gold >= goldReq:
				if sws.clickElement(XPATH.TROOP_REDUCE_TIME_BTN, refresh=True):
					logger.success('In reduce_train_time: Succesfuly reduced training time.')
					status = True
				else:
					logger.error('In reduce_train_time: Failed to press the button.')
			else:
				logger.warning(f'In reduce_train_time: 10 gold needed to reduce time, but {gold} gold available')
		else:
			logger.warning('In reduce_train_time: Not training any troops.')
	else:
		logger.error('In reduce_train_time: Not barracks screen.')
	return status


def get_total_training_time(sws: SWS):
	"""
	Gets the execution time needed for the current queued troops to be trained
	Parameters:
		- sws (SWS): Selenium Web Scraper
	"""
	totalTime = 0

	if not check_building_page_title(sws, BuildingType.Barracks):
		logger.error('In get_total_training_time: Not barracks screen')
	else:
		status = False

		for line in sws.getElementsAttribute(XPATH.TROOP_TRAIN_TIME, 'text'):
			if status == False:
				status = True
			
			if line:
				if line[-1] != '?':
					logger.success(f'In function get_total_training_time: {line}s.')
					totalTime += time_to_seconds(line)
				else:
					logger.error(f'In function get_total_training_time: {line}s.')
			else:
				logger.error(f'In function get_total_training_time: no text could be extracted from the table')
			
		if status == False:
			logger.warning('In get_training_time: no troops are queued for training')
	
	return totalTime
