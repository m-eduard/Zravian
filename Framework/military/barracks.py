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
	Gets the execution time needed for the current queued troops to be trained inside the Barracks
	Parameters:
		- sws (SWS): Selenium Web Scraper
	"""
	totalTime = 0

	if not check_building_page_title(sws, BuildingType.Barracks):
		logger.error(f'In {get_total_training_time.__name__}: Not Stable screen')
	else:
		status = False

		trainingUnits = sws.getElementsAttribute(XPATH.TRAINING_TROOPS_TYPE, 'text')
		trainingTimes = sws.getElementsAttribute(XPATH.TRAINING_TROOPS_TIME, 'text')

		if len(trainingTimes) == len(trainingUnits):
			for i in range(len(trainingTimes)):
				if status == False:
					status = True
				
				if trainingTimes[i] and trainingUnits[i]:
					if trainingTimes[i][-1] != '?':
						logger.success(f'In {get_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
						totalTime += time_to_seconds(trainingTimes[i])
					else:
						logger.warning(f'In {get_total_training_time.__name__}: {trainingTimes[i]}s for {trainingUnits[i]}.')
				else:
					logger.error(f'In {get_total_training_time.__name__}: No text could be extracted from the table')
		else:
			logger.error(f'In {get_total_training_time.__name__}: Lists of attributes for time and queued troop type have different sizes')
		
		if status == False:
			logger.warning(f'In {get_total_training_time.__name__}: No troops are queued for training')
	
	return totalTime
