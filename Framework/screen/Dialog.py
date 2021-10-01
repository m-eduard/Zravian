from enum import Enum, IntEnum
import re
import time
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()
# Polling constants
DEFAULT_POLLING_TIME = 0.5
MAX_POLLING_TIME = 5


# Dialog page
def press_continue_btn(sws: SWS):
	"""
	Presses the continue button after first ever login or after village creation.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if operation was successful, False otherwise.
	"""
	ret = False
	# Continue button text
	CONTINUE_BTN_TEXT = 'Continue'
	if sws.clickElement(XPATH.STRING_ON_SCREEN % CONTINUE_BTN_TEXT, refresh=True):
		ret = True
	else:
		logger.error('In press_continue_btn: Failed to click "continue" button')
	return ret


# Instructions dialog
class InstructionsSearchItem(Enum):
	COSTS = XPATH.INSTRUCTIONS_COSTS


def __search_in_instructions(sws: SWS, locators: list, item: InstructionsSearchItem):
	"""
	Searches information in instructions menu.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- locators ([str]): List with names to incrementally search for instructions page.
		- item (InstructionsSearchItem): Property to extract from last name.

	Returns:
		- String with requested value, None if error occured.
	"""
	ret = None
	# Instructions menu text
	INSTRUCTIONS_MENU = 'Instructions'
	# Instructions iframe name
	INSTRUCTIONS_IFRAME = 'Frame'
	# Open instructions menu
	if sws.clickElement(XPATH.STRING_ON_SCREEN % INSTRUCTIONS_MENU):
		sws.enter_iframe(INSTRUCTIONS_IFRAME)
		for locator in locators:
			if sws.isVisible(XPATH.STRING_ON_SCREEN % locator):
				if not sws.clickElement(XPATH.STRING_ON_SCREEN % locator):
					logger.error(f'In __search_in_instructions: Failed to click locator {locator}')
					break
			else:
				logger.error(f'In __search_in_instructions: Failed to find {locator}')
				break
		else:
			ret = sws.getElementAttribute(item.value, Attr.TEXT)
		sws.exit_iframe()
		if not sws.clickElement(sws.MISSION_CLOSE_BTN):
			ret = None
			logger.error('In __search_in_instructions: Failed to close instructions dialog')
	else:
		logger.error('In __search_in_instructions: Failed to open instructions dialog')
	return ret


def instructions_get_costs(sws: SWS, locators: list):
	"""
	Searches costs information for building/troop.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
		- locators ([str]): List with names to incrementally search for instructions page.

	Returns:
		- List containing: Lumber, Clay, Iron, Crop and Upkeep or None if error encountered.
	"""
	ret = None
	costsText = __search_in_instructions(sws, locators, InstructionsSearchItem.COSTS)
	if costsText:
		# Take second row and split at each '|', leaving out the last one
		try:
			ret = costsText.split('\n')[1].split('|')[:-1]
		except IndexError:
			logger.error(f'In instructions_get_costs: Costs do not respect pattern {costsText}')
	else:
		logger.error('In instructions_get_costs: __search_in_instructions() failed')
	return ret

# Missions dialog
class MissionNum(IntEnum):
	M1 = 1
	M2 = 2
	M3 = 3
	M4 = 4
	M5 = 5
	M6 = 6
	M7 = 7
	M8 = 8
	M9 = 9
	M10 = 10
	M11 = 11
	M12 = 12
	M13 = 13
	M14 = 14
	M15 = 15
	M16 = 16
	M17 = 17
	M18 = 18
	M19 = 19
	M20 = 20
	M21 = 21
	M22 = 22
	M23 = 23
	M24 = 24
	M25 = 25
	# Same number, different tasks
	M20M = 20
	M20E = 20
	M21M = 21
	M21E = 21


def open_mission_dialog(sws : SWS):
	"""
	Will open mission dialog if its closed.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if operation was successful, False otherwise.
	"""
	ret = False
	close_mission_dialog(sws)
	if sws.isVisible(XPATH.TASK_MASTER):
		if sws.clickElement(XPATH.TASK_MASTER):
			startTime = time.time()
			endTime = startTime + MAX_POLLING_TIME
			while startTime < endTime:
				if sws.isVisible(XPATH.MISSION_NAME):
					ret = True
					break
				time.sleep(DEFAULT_POLLING_TIME)
				startTime = time.time()
			else:
				logger.error('In open_mission_dialog: Popup failed to open')
		else:
			logger.error('In open_mission_dialog: Failed to click on task master')
	else:
		logger.warning('In open_mission_dialog: Failed to find task master')
	return ret


def close_mission_dialog(sws : SWS):
	"""
	Closes the mission dialog by refreshing the page.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
	"""
	sws.refresh(hardRefesh=True)


def get_mission_number(sws : SWS):
	"""
	Gets current mission title.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- MissionNum representing mission number or None.
	"""
	num = None
	if open_mission_dialog(sws):
		dialogHeadline = sws.getElementAttribute(XPATH.MISSION_NAME, Attr.TEXT)
		if dialogHeadline:
			dialogRe = re.search('([0-9]+)(.*)', dialogHeadline)
			missionTitleNum, missionTitleName = None, None
			try:
				missionTitleNum = int(dialogRe.group(1))
				missionTitleName = str(dialogRe.group(2))
			except (AttributeError, ValueError) as err:
				logger.warning(f'In get_mission_number: Title does not respect pattern: {err}')
			if missionTitleNum and missionTitleName:
				# Search for mission number
				for mission in MissionNum:
					if missionTitleNum == mission.value:
						# Check if mission has multiple candidates
						if mission.value == MissionNum.M20.value:
							if 'Barracks' in missionTitleName:
								num = MissionNum.M20M
							elif 'Warehouse' in missionTitleName:
								num = MissionNum.M20E
						elif mission.value == MissionNum.M21.value:
							if 'Train' in missionTitleName:
								num = MissionNum.M21M
							elif 'Marketplace' in missionTitleName:
								num = MissionNum.M21E
						else:
							num = mission
						if num is None:
							logger.error(f'In get_mission_number: Failed to identify mission {dialogHeadline}')
						break
				else:
					logger.warning('In get_mission_number: Unknown mission')
		else:
			logger.error('In get_mission_number: Failed to get headline')
	else:
		logger.error('In get_mission_number: Failed to open mission dialog')
	return num


def press_accomplish_mission(sws : SWS):
	"""
	Press acomplish mission button.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if operation was successful, False otherwise.
	"""
	ret = False
	if sws.clickElement(XPATH.ACCOMPLISH_MISSION, waitFor=True):
		ret = True
	else:
		logger.error('In accomplish_mission: Failed to press accomplish')
	return ret


# Setup
def is_initial_setup(sws : SWS):
	"""
	Checks if mission dialog is on initial screen.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the mission dialog is in initial state, False otherwise.
	"""
	ret = False
	INITIAL_SCREEN_TEXT = 'Welcome to Zravian!'
	if open_mission_dialog(sws):
		title = sws.getElementAttribute(XPATH.MISSION_NAME, Attr.TEXT, waitFor=True)
		if title:
			ret = INITIAL_SCREEN_TEXT in title
		else:
			logger.error('In is_initial_setup: Failed to get title')
	else:
		logger.error('In is_initial_setup: Failed to open mission dialog')
	return ret


def accept_missions(sws : SWS):
	"""
	Accepts missions in initial dialog.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if operation was successful, False otherwise.
	"""
	ret = False
	# Accept tasks text
	ACCEPT_TASKS_TEXT = 'To the first task!'
	if open_mission_dialog(sws):
		if is_initial_setup(sws):
			if sws.clickElement(XPATH.STRING_ON_SCREEN % ACCEPT_TASKS_TEXT, javaScriptClick=True):
				close_mission_dialog(sws)
				if press_continue_btn(sws):
					ret = True
					logger.success('In accept_missions: Accepted missions')
				else:
					logger.error('In accept_missions: Failed to press continue')
			else:
				logger.error('In accept_missions: Failed to accept missions')
		else:
			close_mission_dialog(sws)
			ret = True
			logger.warning('In accept_missions: Not initial screen')
	else:
		logger.error('In accept_missions: Failed to open mission dialog')
	return ret


def skip_missions(sws : SWS):
	"""
	Refuses missions in initial dialog.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if operation was successful, False otherwise.
	"""
	ret = False
	# Refuse tasks text
	REFUSE_TASKS_TEXT = 'Skip tasks'
	# Number of times required to press 'Skip tasks'
	REFUSE_COUNTER = 3
	if open_mission_dialog(sws):
		if is_initial_setup(sws):
			for _ in range(REFUSE_COUNTER):
				if not sws.clickElement(XPATH.STRING_ON_SCREEN % REFUSE_TASKS_TEXT, waitFor=True, \
						javaScriptClick=True):
					logger.error('In skip_missions: Failed to click Refuse button')
					break
			else:
				close_mission_dialog(sws)
				if press_continue_btn(sws):
					ret = True
					logger.success('In skip_missions: Refused missions')
				else:
					logger.error('In accept_missions: Failed to press continue')
		else:
			close_mission_dialog(sws)
			ret = True
			logger.warning('In skip_missions: Not initial screen')
	else:
		logger.error('In skip_missions: Failed to open mission dialog')
	return ret
