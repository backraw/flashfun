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

    cvar_armor_spawn = config.cvar(
        'armor_spawn',
        0,
        'The armor value the player starts with.'
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

    config.section('PLAYER REWARDS', '=')

    cvar_enable_player_rewards = config.cvar(
        'enable_player_rewards',
        1,
        'Enable player rewards (0 disable).'
    )

    config.section('SAY COMMANDS', '=')

    cvar_admin_saycommand = config.cvar(
        'admin_saycommand',
        '!flashfun',
        'The admin say command.'
    )
