from enum import IntEnum
import re
import time
from Framework.screen.HomeUI import press_continue_btn
from Framework.utility.Constants import get_XPATH, get_projectLogger
from Framework.utility.SeleniumWebScraper import SWS, Attr


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()
# Polling constants
DEFAULT_POLLING_TIME = 0.5
MAX_POLLING_TIME = 5


# Enum containing all missions
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
	M20M = 201
	M20E = 202
	M21M = 211
	M21E = 212
	M22 = 22
	M23 = 23
	M24 = 24
	M25 = 25


# Utils
def open_mission_dialog(sws : SWS):
	"""
	Will open mission dialog if its closed.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the operation was successful, False otherwise.
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
		logger.error('In open_mission_dialog: Failed to find task master')
	return ret


def close_mission_dialog(sws : SWS):
	"""
	Closes the mission dialog by refreshing the page.

	Parameters:
		- sws (SWS): Selenium Web Scraper.
	"""
	sws.refresh(hardRefesh=True)


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
		title = sws.getElementAttribute(XPATH.MISSION_NAME, Attr.TEXT, waitFor=True)
		if title:
			titleRe = re.search('([0-9]+)(.*)', title)
			titleNum, titleWord = None, None
			try:
				titleNum = int(titleRe.group(1))
				titleWord = str(titleRe.group(2))
			except (AttributeError, ValueError) as err:
				logger.warning(f'In get_mission_number: Title does not respect pattern: {err}')
			if titleNum and titleWord:
				for item in MissionNum:
					if item.value == titleNum or \
							(item == MissionNum.M20M and 'Barracks' in titleWord) or \
							(item == MissionNum.M20E and 'Warehouse' in titleWord) or \
							(item == MissionNum.M21M and 'Train' in titleWord) or \
							(item == MissionNum.M21E and 'Marketplace' in titleWord):
						num = item
						break
				else:
					logger.warning('In get_mission_number: Unknown mission')
		else:
			logger.error('In get_mission_number: Failed to get title')
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
