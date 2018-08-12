# ../flashfun/util.py

"""Provides utility functions."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
from contextlib import suppress

# Source.Python Imports
#   Colors
from colors import RED
from colors import WHITE
#   Listeners
from listeners.tick import GameThread
#   Messages
from messages import SayText2
#   Players
from players.entity import Player
#   Weapons
from weapons.entity import Weapon

# Plugin Imports
#   Config
from flashfun.config import cvar_armor_start
from flashfun.config import cvar_health_start
from flashfun.config import cvar_spawn_protection_time
#   Colors
from flashfun.colors import MESSAGE_COLOR_ORANGE
from flashfun.colors import MESSAGE_COLOR_WHITE
#   Info
from flashfun.info import info
#   Spawn Locations
from flashfun.spawn_locations import SpawnLocationDispatcher


# =============================================================================
# >> UTILITY FUNCTIONS
# =============================================================================
def enable_damage_protection(player):
    """Enable spawn protection for the player."""
    player.godmode = True
    player.color = RED


def disable_damage_protection(player_index):
    """Disable spawn protection for the player."""
    with suppress(ValueError):
        player = Player(player_index)

        player.godmode = False
        player.color = WHITE


def handle_player_reward(player, attr, gain, max_value):
    """Handle a player reward."""
    # Calculate the new value for the reward attribute ('health' or 'armor')
    new_value = getattr(player, attr) + gain

    # If it exceeds the maximum value, set the maximum value as the new value
    if new_value > max_value:
        new_value = max_value

    # Set the new reward attribute value
    setattr(player, attr, new_value)


def prepare_player(player):
    """Prepare the player."""
    # Perform setting the player's spawn location on another thread
    spawn_location_dispatch_thread = GameThread(target=SpawnLocationDispatcher.perform_action, args=(player,))
    spawn_location_dispatch_thread.start()

    # Set starting health and armor
    player.health = int(cvar_health_start)
    player.armor = int(cvar_armor_start)

    # Give the player a flashbang
    player.give_named_item('weapon_flashbang',)

    # Enable spawn protection
    enable_damage_protection(player)

    # Disable spawn protection later
    player.delay(abs(int(cvar_spawn_protection_time)), disable_damage_protection, (player.index,))


def remove_weapon(weapon_index):
    """Remove a weapon entity from the server if it is still valid."""
    with suppress(ValueError):
        weapon = Weapon(weapon_index)

        if weapon.owner is None:
            weapon.remove()


def tell_player(player, message):
    """Send a prefixed SayText2 message to the player."""
    SayText2(
        f'{MESSAGE_COLOR_ORANGE}[{MESSAGE_COLOR_WHITE}{info.verbose_name}{MESSAGE_COLOR_ORANGE}] {message}'
    ).send(player.index)
