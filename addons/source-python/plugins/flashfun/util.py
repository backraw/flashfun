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
#   Rewards
from flashfun.rewards import player_rewards_list
#   Weapons
from weapons.entity import Weapon
from weapons.manager import weapon_manager

# Plugin Imports
#   Config
from flashfun.config import cvar_armor_spawn
from flashfun.config import cvar_health_spawn
from flashfun.config import cvar_spawn_protection_time
#   Colors
from flashfun.colors import MESSAGE_COLOR_ORANGE
from flashfun.colors import MESSAGE_COLOR_WHITE
#   Info
from flashfun.info import info
#   Rewards
from flashfun.rewards import player_rewards_list
from flashfun.rewards import weapon_rewards
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
    # Fix the maximum value if it is zero
    if max_value == 0:
        max_value = 999

    # Calculate the new value for the reward attribute
    new_value = getattr(player, attr) + gain

    # If it exceeds the maximum value, set the maximum value as the new value
    if new_value > max_value:
        new_value = max_value

    # Set the new reward attribute value
    setattr(player, attr, new_value)


def handle_weapon_reward(player, reward_type, reward_multiplier, basename):
    """Handle weapon rewards."""
    # Get the player's property value for the reward type
    reward_type_value = getattr(player, reward_type)

    # Only respect values higher than zero
    if reward_type_value > 0:

        # If the player has reached the multiplier, handle the reward
        if reward_type_value % reward_multiplier == 0:
            classname = weapon_manager[basename].name

            player_rewards_list.append((player.userid, classname))
            equip_player(player, classname)


def handle_weapon_reward_properties(weapon):
    """Handle weapon reward properties."""
    with suppress(AttributeError):

        # Get a Player object fort the player
        player = Player(weapon.owner.index)

        # Ignore handling if the reward properties have already been prepared
        if (player.userid, weapon.classname) not in player_rewards_list:
            return

        # Get the reward values
        reward_values = weapon_rewards[weapon_manager[weapon.classname].basename]

        # Set the weapon properties
        with suppress(ValueError):
            weapon.clip = int(reward_values.get('clip', weapon.clip))
            weapon.ammo = int(reward_values.get('ammo', weapon.ammo))

        # Remove the player from the player rewards list
        player_rewards_list.remove((player.userid, weapon.classname))


def equip_player(player, classname='weapon_flashbang'):
    """Equip the player with a weapon, if they don't already own one."""
    if player.get_weapon(classname) is None:
        player.give_named_item(classname)


def prepare_player(player):
    """Prepare the player."""
    # Perform setting the player's spawn location on another thread
    spawn_location_dispatch_thread = GameThread(target=SpawnLocationDispatcher.perform_action, args=(player,))
    spawn_location_dispatch_thread.start()

    # Set health and armor spawn values
    player.health = int(cvar_health_spawn)
    player.armor = int(cvar_armor_spawn)

    # Equip the player
    equip_player(player)

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
