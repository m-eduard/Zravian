from Framework.utility.Logger import get_projectLogger
from Framework.utility.Constants import BuildingType, Server
from Framework.infrastructure.builder import construct_building
from Framework.account.Login import login


logger = get_projectLogger()
logger.set_debugMode(True)
with login(Server.S10k, '0bomb13', headless=False) as sws:
    assert construct_building(sws, BuildingType.Stable, forced=True, waitToFinish=True)

