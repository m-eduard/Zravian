from Framework.infrastructure.builder import check_building_page_title, enter_building, time_to_seconds
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
    barracks = [1, 2, 3, 11, 12, 13, 14, 21, 22]
    stable = [4, 5, 6, 15, 16, 23, 24, 25, 26]
    siege = [TroopType.RRam, TroopType.Fire_Catapult, TroopType.TRam, TroopType.Catapult, TroopType.Battering_Ram, TroopType.Trebuchet]


    buildingDict = dict()
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
    
    return status

def get_total_training_time(sws : SWS):
    """
	Gets the execution time needed for the current queued troops to be trained
	Parameters:
		- sws (SWS): Selenium Web Scraper
	"""
    totalTime = 0

    status = False

    trainingUnits = sws.getElementsAttribute(XPATH.TROOP_TYPE_TIME, 'text')
    trainingTimes = sws.getElementsAttribute(XPATH.TROOP_TRAIN_TIME, 'text')

    if len(trainingTimes) == len(trainingUnits):
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
    else:
        logger.error(f'In {get_total_training_time.__name__}: lists of attributes for time and queued troop type have different sizes')

    if status == False:
        logger.warning(f'In {get_total_training_time.__name__}: no troops are queued for training')

    return totalTime
