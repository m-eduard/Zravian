from Framework.infrastructure.builder import enter_building, time_to_seconds
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
	barracks = [TroopType.Legionnaire, TroopType.Praetorian, TroopType.Imperian, TroopType.Clubswinger, TroopType.Spearman, TroopType.Axeman, TroopType.Scout, TroopType.Phalanx, TroopType.Swordsman]
	stable = [TroopType.Equites_Legati, TroopType.Equites_Imperatoris, TroopType.Equites_Caesaris, TroopType.Paladin, TroopType.Teutonic_Knight, TroopType.Pathfinder, TroopType.Theutates_Thunder, TroopType.Druidrider, TroopType.Haeduan]
	siege = [TroopType.RRam, TroopType.Fire_Catapult, TroopType.TRam, TroopType.Catapult, TroopType.Battering_Ram, TroopType.Trebuchet]


	buildingDict = dict()
	for x in barracks:
		buildingDict[x] = BuildingType.Barracks
	for x in stable:
		buildingDict[x] = BuildingType.Stable
	for x in siege:
		buildingDict[x] = BuildingType.SiegeWorkshop
	
	#TODO
	enter_building(sws, buildingDict[tpType])

	status = False
	maxUnits = sws.getElementAttribute(XPATH.TROOP_MAX_UNITS % TROOPS[tpType].name, 'text')
	# The number is between parantheses
	if maxUnits:
		try:
			maxUnits = int(maxUnits[1:-1])
		except ValueError:
			logger.error(f'In make_troops_by_amount: {maxUnits[1:-1]} is not int')
			maxUnits = None
	if maxUnits and maxUnits >= amount:
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
	
	return status

def get_current_building_training_time(sws : SWS):
	"""
	Gets the training time needed for the troops inside the building which page is currently open

	Parameters:
		- sws (SWS): Selenium Web Scraper
	"""
	totalTime = 0
	status = False

	trainingUnits = sws.getElementsAttribute(XPATH.TRAINING_TROOPS_TYPE, 'text')
	trainingTimes = sws.getElementsAttribute(XPATH.TRAINING_TROOPS_TIME, 'text')

	for i in range(len(trainingTimes)):
		if status == False:
			status = True

		if trainingTimes[i] and trainingUnits[i]:
			if trainingTimes[i][-1] != '?':
				logger.success(f'In {get_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
				totalTime += time_to_seconds(trainingTimes[i])
			else:
				logger.error(f'In {get_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
		else:
			logger.error(f'In {get_total_training_time.__name__}: no text could be extracted from the table')

	if status == False:
		logger.warning(f'In {get_total_training_time.__name__}: no troops are queued for training')

	return totalTime

def get_total_training_time(sws : SWS, bdType : BuildingType = None):
	"""
	Gets the execution time needed for the current queued troops to be trained

	Parameters:
		- sws (SWS): Selenium Web Scraper
		- bdType (BuildingType): if a value is offered, the function extracts the time required for the
								 troops inside the specified building to be trained;
								 else, it goes thorugh every building that can train troops
								 and extracts the time
	
	Returns:
		- the training time for the specified building, if a bdType parameteer was offered, a list of times otherwirse
	"""
	time = 0

	if bdType == None:
		time = []
		trainingBuildings= [BuildingType.Barracks, BuildingType.Stable, BuildingType.SiegeWorkshop]

		for bd in trainingBuildings:
			enter_building(sws, bd)
			time.append(get_current_building_training_time(sws))
	else:
		time = get_current_building_training_time(sws)
	
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
				logger.success(f'In {reduce_train_time.__name__}: Succesfuly reduced training time.')
				status = True
			else:
				logger.error(f'In {reduce_train_time.__name__}: Failed to press the button.')
		else:
			logger.warning(f'In {reduce_train_time.__name__}: Not enough gold for speedup.')
	else:
		logger.warning(f'In {reduce_train_time.__name__}: Not training any troops.')

	return status
