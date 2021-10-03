from Framework.infrastructure.builder import enter_building, time_to_seconds
from Framework.utility.Constants import  BuildingType, Troop, TroopType, get_TROOPS, get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


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
	barracks = [TroopType.Legionnaire, TroopType.Praetorian, TroopType.Imperian, TroopType.Clubswinger,\
				TroopType.Spearman, TroopType.Axeman, TroopType.Scout, TroopType.Phalanx, TroopType.Swordsman]
	stable = [TroopType.Equites_Legati, TroopType.Equites_Imperatoris, TroopType.Equites_Caesaris,\
			  	TroopType.Paladin, TroopType.Teutonic_Knight, TroopType.Pathfinder, TroopType.Theutates_Thunder,\
			  	TroopType.Druidrider, TroopType.Haeduan]
	siege = [TroopType.RRam, TroopType.Fire_Catapult, TroopType.TRam, TroopType.Catapult, TroopType.Battering_Ram,\
		 	 	TroopType.Trebuchet]
	palace = [TroopType.Chieftain, TroopType.TSettler]

	buildingDict = dict()
	for x in barracks:
		buildingDict[x] = BuildingType.Barracks
	for x in stable:
		buildingDict[x] = BuildingType.Stable
	for x in siege:
		buildingDict[x] = BuildingType.SiegeWorkshop
	for x in palace:
		buildingDict[x] = BuildingType.Palace

	status = False
	if enter_building(sws, buildingDict[tpType]):
		maxUnits = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, Attr.TEXT)
		if maxUnits:
			try:
				maxUnits = int(maxUnits[1:-1])
			except ValueError:
				logger.error(f'In make_troops_by_amount: {maxUnits[1:-1]} is not int')
				maxUnits = None
		if maxUnits and maxUnits >= amount:
			if sws.sendKeys(XPATH.TROOP_INPUT_BOX % TROOPS[tpType].name, amount):
				if sws.clickElement(XPATH.TROOP_TRAIN_BTN, refresh=True):
					logger.success(f'In make_troops_by_amount: {amount} {TROOPS[tpType].name} were trained')
					status = True
				else:
					logger.error('In make_troops_by_amount: Failed to press train')
			else:
				logger.error('In make_troops_by_amount: Failed to insert amount of troops')
		else:
			logger.warning('In make_troops_by_amount: Not enough resources')
	else:
		logger.error(f'In make_troops_by_amount: Failed to enter {buildingDict[tpType]}')
	return status

def troop_max_amount(sws : SWS, tpType : TroopType):
	"""
	Find the maximum amount of units of a specified type that can be trained.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- tpType (TroopType): Denotes troop.

	Returns:
		- The maximum troops that can be trained when the function is called
	"""
	barracks = [TroopType.Legionnaire, TroopType.Praetorian, TroopType.Imperian, TroopType.Clubswinger,\
				TroopType.Spearman, TroopType.Axeman, TroopType.Scout, TroopType.Phalanx, TroopType.Swordsman]
	stable = [TroopType.Equites_Legati, TroopType.Equites_Imperatoris, TroopType.Equites_Caesaris,\
			  	TroopType.Paladin, TroopType.Teutonic_Knight, TroopType.Pathfinder, TroopType.Theutates_Thunder,\
			  	TroopType.Druidrider, TroopType.Haeduan]
	siege = [TroopType.RRam, TroopType.Fire_Catapult, TroopType.TRam, TroopType.Catapult, TroopType.Battering_Ram,\
		 	 	TroopType.Trebuchet]
	palace = [TroopType.Chieftain, TroopType.TSettler]

	buildingDict = dict()
	for x in barracks:
		buildingDict[x] = BuildingType.Barracks
	for x in stable:
		buildingDict[x] = BuildingType.Stable
	for x in siege:
		buildingDict[x] = BuildingType.SiegeWorkshop
	for x in palace:
		buildingDict[x] = BuildingType.Palace
	
	if enter_building(sws, buildingDict[tpType]):
		maxUnits = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, Attr.TEXT)
	else:
		logger.error(f'In troop_max_amount: Failed to enter {buildingDict[tpType]}')
	return int(maxUnits[1:-1])

def get_current_building_time(sws : SWS):
	"""
	Gets the time until the troops inside the current building are training.

	Parameters:
		- sws (SWS): Selenium Web Scraper
	
	Returns:
		- time needed to end the training of the troops inside the current building
	"""
	time = 0
	trainingTimes = sws.getElementsAttribute(XPATH.TRAINING_TROOPS_TIME, Attr.TEXT)
	if trainingTimes:
		logger.success(f'In get_current_building_time: {trainingTimes[-1]}.')
		if trainingTimes[-1][-1] != '?':
			time = time_to_seconds(trainingTimes[-1])
		else:
			time = 0
	else:
		logger.error(f'In get_current_building_time: no text could be extracted from the table');
	return time

def get_total_training_time(sws : SWS, bdType : BuildingType = None):
	"""
	Gets the execution time needed for the current queued troops to be trained

	Parameters:
		- sws (SWS): Selenium Web Scraper
		- bdType (BuildingType): if a value is offered, the function extracts the time required for the
								 troops inside the specified building to be trained;
								 else, it goes through every building that can train troops
								 and extracts the time
	
	Returns:
		- the training time for the specified building, if a bdType parameteer was offered, a list of times otherwise
		- number of undefined times (00:00:00?)

		- None if no troop is in training
	"""
	time = []
	if bdType == None:
		trainingBuildings = [BuildingType.Barracks, BuildingType.Stable, BuildingType.SiegeWorkshop,\
								BuildingType.Palace]
		for bd in trainingBuildings:
			enter_building(sws, bd)
			time.append(get_current_building_time(sws))
	else:
		time.append(get_current_building_time(sws))
	return time


def reduce_train_time(sws : SWS, bdType : BuildingType = None):
	"""
	Presses the "Reduce the troop training time" button
	(works only if you're on the page of a building designed for training troops).

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- bdType (BuildingType): None default; if a value is offered, before pushing the reduce time button,
								 the page corresponding to the specified building will be opened

	Returns:
		- True if the operation is successful, False otherwise.
	"""
	status = False
	if bdType:
		enter_building(sws, bdType)
	if sws.isVisible(XPATH.TRAINING_TROOPS_TABLE):
		if sws.isVisible(XPATH.TROOP_REDUCE_TIME_BTN):
			if sws.clickElement(XPATH.TROOP_REDUCE_TIME_BTN, refresh=True):
				logger.success(f'In reduce_train_time: Succesfuly reduced training time.')
				status = True
			else:
				logger.error(f'In reduce_train_time: Failed to press the button.')
		else:
			logger.warning(f'In reduce_train_time: Reduce train time button is not visible.')
	else:
		logger.warning(f'In reduce_train_time: Not training any troops.')
	return status
