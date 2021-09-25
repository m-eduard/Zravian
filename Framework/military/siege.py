from Framework.infrastructure.builder import check_building_page_title
from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import  BuildingType, TroopType, get_TROOPS, get_XPATH, time_to_seconds
from Framework.utility.SeleniumUtils import SWS


logger = get_projectLogger()
TROOPS = get_TROOPS()
XPATH = get_XPATH()

def make_siege_troops_by_amount(sws : SWS, tpType : TroopType, amount : int):
	"""
	Trains Troops inside Siege by specified type and amount.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.
		- amount: Denotes the amount of troop to be trained.
	
	Returns:
		- True, if the operations succeded, False otherwise
	"""
	status = False
	if check_building_page_title(sws, BuildingType.SiegeWorkshop):
		# get the maximum amount of troops that can be trained
		maxUnits = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, 'text')

		if maxUnits:
			try:
				maxUnits = int(maxUnits[1:-1])
			except ValueError:
				logger.error(f'In {make_siege_troops_by_amount.__name__}: {maxUnits[1:-1]} is not int')
				maxUnits = None
		
			if maxUnits and maxUnits >= amount:
				if sws.sendKeys(XPATH.TROOP_INPUT_BOX % TROOPS[tpType].name, amount):
					if sws.clickElement(XPATH.TROOP_TRAIN_BTN, refresh=True):
						logger.success(f'In {make_siege_troops_by_amount.__name__}: {amount} {TROOPS[tpType].name} were trained')
						status = True
					else:
						logger.error(f'In {make_siege_troops_by_amount.__name__}: Failed to press Train')
				else:
					logger.error(f'In {make_siege_troops_by_amount.__name__}: Failed to insert amount of troops')
			else:
				logger.warning(f'In {make_siege_troops_by_amount.__name__}: Not enough resources')
		else:
			logger.error(f'In {make_siege_troops_by_amount.__name__}: Failed to extract maximum units that can be trained')
	else:
		logger.error(f'In {make_siege_troops_by_amount.__name__}: Not Siege screen')

	return status

def get_siege_total_training_time(sws: SWS):
	"""
	Gets the execution time needed for the current queued troops to be trained inside the Siege
	Parameters:
		- sws (SWS): Selenium Web Scraper
	"""
	totalTime = 0

	if not check_building_page_title(sws, BuildingType.SiegeWorkshop):
		logger.error(f'In {get_siege_total_training_time.__name__}: Not Siege screen')
	else:
		status = False

		trainingUnits = sws.getElementsAttribute(XPATH.TROOP_TYPE_TIME, 'text')
		trainingTimes = sws.getElementsAttribute(XPATH.TROOP_TRAIN_TIME, 'text')

		if len(trainingTimes) == len(trainingUnits):
			for i in range(len(trainingTimes)):
				if status == False:
					status = True
				
				if trainingTimes[i] and trainingUnits[i]:
					if trainingTimes[i][-1] != '?':
						logger.success(f'In {get_siege_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
						totalTime += time_to_seconds(trainingTimes[i])
					else:
						logger.error(f'In {get_siege_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
				else:
					logger.error(f'In {get_siege_total_training_time.__name__}: no text could be extracted from the table')
		else:
			logger.error(f'In {get_siege_total_training_time.__name__}: lists of attributes for time and queued troop type have different sizes')
		
		if status == False:
			logger.warning(f'In {get_siege_total_training_time.__name__}: no troops are queued for training')
	
	return totalTime
