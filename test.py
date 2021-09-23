from time import sleep
from Framework.military.academy import research
from Framework.utility.Logger import get_projectLogger
from Framework.military.military_utils import enter_academy, enter_barracks
from Framework.utility.Constants import Server, TroopType
from Framework.account.Login import login
from Framework.military.barracks import reduce_train_time, make_troops_by_amount

logger = get_projectLogger()

if __name__ == "__main__":
    logger.set_debugMode(True)
    with login(Server.S10k, username="0bomb8", headless=False) as sws:
        assert enter_academy(sws)
        research(sws, TroopType.RRam, forced=True)