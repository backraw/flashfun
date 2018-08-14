# ../flashfun/rewards.py

"""Provides player reward functions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Site-Packages Imports
#   ConfigObj
from configobj import ConfigObj

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Paths
from paths import PLUGIN_DATA_PATH
#   Weapons
from weapons.manager import weapon_manager

# Plugin Imports
#   Config
from flashfun.config import cvar_enable_player_rewards
#   Info
from flashfun.info import info


# =============================================================================
# >> REWARD CONFIG
# =============================================================================
if int(cvar_enable_player_rewards):
    _rewards_config_ini = ConfigObj(PLUGIN_DATA_PATH.joinpath(info.name, 'rewards', f'{GAME_NAME}.ini'))
else:
    _rewards_config_ini = dict()


# =============================================================================
# >> GET WEAPON AND PLAYER ATTRIBUTE REWARDS
# =============================================================================
weapon_rewards = {key: value for key, value in _rewards_config_ini.items() if key in weapon_manager}
allowed_weapons = [weapon_manager[basename].name for basename in weapon_rewards]

player_attribute_rewards = {key: value for key, value in _rewards_config_ini.items() if key not in weapon_manager}


# =============================================================================
# >> LIST OF PLAYERS WHO RECEIVED A WEAPON REWARD
# =============================================================================
player_rewards_list = list()
