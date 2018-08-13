# ../flashfun/config.py

"""Provide plugin configuration options."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Config
from config.manager import ConfigManager

# Plugin Imports
from flashfun.info import info


# =============================================================================
# >> PLUGIN CONFIGURATION
# =============================================================================
with ConfigManager(info.name, cvar_prefix=f'{info.name}_') as config:

    config.section('PLAYER ATTRIBUTES', '=')

    cvar_health_spawn = config.cvar(
        'health_spawn',
        1,
        'The health value the player starts with.'
    )

    cvar_health_max = config.cvar(
        'health_max',
        50,
        'The maximum health value a player can have (0 = 999).'
    )

    cvar_armor_spawn = config.cvar(
        'armor_spawn',
        0,
        'The armor value the player starts with.'
    )

    cvar_armor_max = config.cvar(
        'armor_max',
        30,
        'The maximum armor value a player can have (0 = 999).'
    )

    config.section('PLAYER REWARDS', '=')

    cvar_health_reward = config.cvar(
        'health_reward',
        2,
        'The health value the player gets as a reward for killing an enemy (0 to turn off).'
    )

    cvar_armor_reward = config.cvar(
        'armor_reward',
        1,
        'The armor value the player gets as a reword for killing an enemy (0 to turn off).'
    )

    cvar_hegrenade_reward_type = config.cvar(
        'hegrenade_reward_type',
        'kills',
        'The High Explosive reward type. Can be "health" or "kills" (see the multiplier option below).'
    )

    cvar_hegrenade_reward_multiplier = config.cvar(
        'hegrenade_reward_multiplier',
        5,
        'The multiplier at which players receive a High Explosive grenade depending on the reward type.'
    )

    config.section('GAMEPLAY', '=')

    cvar_respawn_delay = config.cvar(
        'respawn_delay',
        1,
        'The respawn delay in seconds.'
    )

    cvar_spawn_protection_time = config.cvar(
        'spawn_protection_time',
        3,
        'The spawn protection time in seconds.'
    )

    config.section('SAY COMMANDS', '=')

    cvar_admin_saycommand = config.cvar(
        'admin_saycommand',
        '!flashfun',
        'The admin say command.'
    )
