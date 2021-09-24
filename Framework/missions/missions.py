from enum import IntEnum
import time
from Framework.screen.HomeUI import press_continue_btn
from Framework.utility.Constants import get_XPATH
from Framework.utility.Logger import get_projectLogger
from Framework.utility.SeleniumUtils import SWS


# Project constants
logger = get_projectLogger()
XPATH = get_XPATH()

# Polling constants
DEFAULT_POLLING_TIME = 0.5
MAX_POLLING_TIME = 5


def check_mission_dialog_open(sws : SWS):
	"""
	Waits for mission dialog to be stable and checks if it is open.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the dialog is open, False otherwise.
	"""
	ret = False
	# Text to indicate a stable state
	STABLE_TEXT = 'hidden'
	startTime = time.time()
	endTime = startTime + MAX_POLLING_TIME
	while startTime < endTime:
		if STABLE_TEXT in sws.getElementAttribute(XPATH.MISSION_DIALOG_STATUS, 'style'):
			ret = sws.isVisible(XPATH.MISSION_DIALOG)
			break
		time.sleep(DEFAULT_POLLING_TIME)
		startTime = time.time()
	else:
		logger.error('In check_mission_dialog_open: Failed to achieve stable state')
	return ret


def open_mission_dialog(sws : SWS):
	"""
	Will open mission dialog if its closed.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the operation was successful, False otherwise.
	"""
	ret = False
	if not check_mission_dialog_open(sws):
		if sws.isVisible(XPATH.TASK_MASTER):
			if sws.clickElement(XPATH.TASK_MASTER):
				time.sleep(1)
				if check_mission_dialog_open(sws) and sws.isVisible(XPATH.MISSION_NAME):
					ret = True
				else:
					# Retry opening
					if sws.clickElement(XPATH.TASK_MASTER):
						if check_mission_dialog_open(sws) and sws.isVisible(XPATH.MISSION_NAME):
							ret = True
						else:
							logger.error('In open_mission_dialog: Failed to open')
					else:
						logger.error('In open_mission_dialog: Failed to click on task master')
			else:
				logger.error('In open_mission_dialog: Failed to click on task master')
		else:
			logger.error('In open_mission_dialog: Failed to find task master')
	else:
		ret = True
		logger.info('In open_mission_dialog: Mission dialog already open')
	return ret


def close_mission_dialog(sws : SWS):
	"""
	Attempts to close mission dialog.

	Parameters:
		- sws (SWS): Selenium Web Scraper.

	Returns:
		- True if the operation was successful, False otherwise.
	"""
	ret = False
	if sws.isVisible(XPATH.MISSION_CLOSE_BTN):
		if sws.clickElement(XPATH.MISSION_CLOSE_BTN, waitFor=True):
			if not check_mission_dialog_open(sws):
				ret = True
			else:
				sws.refresh(hardRefesh=True)
				if not check_mission_dialog_open(sws):
					ret = True
				else:
					logger.error('In close_mission_dialog: Failed to close')
		else:
			logger.error('In close_mission_dialog: Failed to press close')
	else:
		ret = True
		logger.info('In close_mission_dialog: Mission dialog was not open')
	return ret


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
		title = sws.getElementAttribute(XPATH.MISSION_NAME, 'text', waitFor=True)
		if title:
			ret = INITIAL_SCREEN_TEXT in title
		else:
			logger.error('In is_initial_setup: Failed to get title')
	else:
		logger.error('In is_initial_setup: Failed to open mission dialog')
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
				if close_mission_dialog(sws):
					if press_continue_btn(sws):
						ret = True
						logger.success('In accept_missions: Accepted missions')
					else:
						logger.error('In accept_missions: Failed to press continue')
				else:
					logger.error('In accept_missions: Failed to close mission dialog')
			else:
				logger.error('In accept_missions: Failed to accept missions')
		else:
			if close_mission_dialog(sws):
				ret = True
				logger.warning('In accept_missions: Not initial screen')
			else:
				logger.error('In accept_missions: Failed to close mission dialog')
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
				if close_mission_dialog(sws):
					if press_continue_btn(sws):
						ret = True
						logger.success('In skip_missions: Refused missions')
					else:
						logger.error('In accept_missions: Failed to press continue')
				else:
					logger.error('In skip_missions: Failed to close mission dialog')
		else:
			if close_mission_dialog(sws):
				ret = True
				logger.warning('In skip_missions: Not initial screen')
			else:
				logger.error('In skip_missions: Failed to close mission dialog')
	else:
		logger.error('In skip_missions: Failed to open mission dialog')
	return ret

