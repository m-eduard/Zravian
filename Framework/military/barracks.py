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

##################### Training time extraction ################################
def get_individual_training_time(sws: SWS, tpType: TroopType):
	"""
	Gets the execution time needed for a specific troop to end the training
	(if any amount of troops of the requested kind are currently training)
	Parameters:
		- sws (SWS)         : Selenium Web Scraper.
		- trType (TroopType): Denotes troops.
	"""

	time = None

	if check_building_page_title(sws, BuildingType.Barracks):
		time = sws.getElementAttribute(XPATH.TROOP_QUEUED % tpType.name, 'text')

		if time:
			if time[-1] == '?':
				logger.error('In get_individual_training_time: zravian undefined time error (00:00:00?)')
				time = 0
			else:
				time = time_to_seconds(time)
				logger.success(f'In function get_individual_training_time: {time}s to end {tpType.name} training')
		else:
			logger.error(f'In get_individual_training_time: no {tpType.name}s are queued for training')
	else:
		logger.error('In get_individual_training_time: Not barracks screen')

	return time


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

		for line in sws.getElementsAttribute(f'//*[@class="under_progress"]/tbody//tr/td[@class="dur"]/span[@id="timer1"]', 'text'):
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
			logger.error('In get_training_time: no troops are queued for training')
	
	return totalTime

	# status = False
	# totalTime = 0

	# # iterate through the lines of the table, by xpath
	# # table = sws._SWS__findElement(sws.driver, XPATH.TROOP_TABLE, False)
	# i = 1
	
	# ls = sws.driver.find_elements_by_xpath('//*[@class="under_progress"]//tr')


	# for j in range(len(ls) - 3):
	# 	if not status:
	# 		status = True

	# 	# make a constant with table's XPATH
	# 	tmpTime = sws.getElementAttribute(f'//*[@class="under_progress"]/tbody//tr[{i}]/td[@class="dur"]/span[@id="timer1"]', 'text')

	# 	if not tmpTime:
	# 		tmpTime = 0
	# 	else:
	# 		if tmpTime[-1] == '?':
	# 			logger.error('In get_total_training_time: zravian undefined time error (00:00:00?)')
	# 			tmpTime = 0
	# 		else:
	# 			# next update: add troop type
	# 			logger.success(f'In function get_total_training_time: {tmpTime}s.')

	# 			tmpTime = time_to_seconds(tmpTime)

	# 	totalTime += tmpTime
	# 	i += 1

	# # for row in sws.getElementsAttribute('//*[@class="under_progress"]//tr' , 'text'):
	# # 	print(row)


	# if status == False:
	# 	totalTime = None
	# 	logger.error('In get_training_time: no troops are queued for training')

	# return totalTime
