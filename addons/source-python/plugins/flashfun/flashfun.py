# ../flashfun/flashfun.py

"""Kill enemies using flashbang grenades."""

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
#   Entities
from entities.hooks import EntityPreHook
from entities.hooks import EntityCondition
#   Events
from events import Event
#   Memory
from memory import make_object
#   Players
from players.entity import Player
#   Weapons
from weapons.entity import Weapon

# Plugin Imports
from flashfun.config import cvar_armor_max
from flashfun.config import cvar_armor_start
from flashfun.config import cvar_armor_reward
from flashfun.config import cvar_health_max
from flashfun.config import cvar_health_start
from flashfun.config import cvar_health_reward
from flashfun.config import cvar_respawn_delay
from flashfun.config import cvar_spawn_protection_time


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def enable_spawn_protection(player):
    """Enable spawn protection for the player."""
    player.godmode = True
    player.color = RED


def disable_spawn_protection(player_index):
    """Disable spawn protection for the player."""
    with suppress(ValueError):
        player = Player(player_index)

        player.godmode = False
        player.color = WHITE


def prepare_player(player):
    """Prepare the player."""
    # Set starting health and armor
    player.health = int(cvar_health_start)
    player.armor = int(cvar_armor_start)

    # Give the player a flashbang
    player.give_named_item('weapon_flashbang',)

    # Enable spawn protection
    enable_spawn_protection(player)
    player.delay(abs(int(cvar_spawn_protection_time)), disable_spawn_protection, (player.index,))


def handle_player_reward(player, attr, gain, max_value):
    """Handle a player reward."""
    # Calculate the new value for the reward attribute ('health' or 'armor')
    new_value = getattr(player, attr) + gain

    # If it exceeds the maximum value, set the maximum value as the new value
    if new_value > max_value:
        new_value = max_value

    # Set the new reward attribute value
    setattr(player, attr, new_value)


def remove_weapon(weapon_index):
    """Remove a weapon entity from the server if it is still valid."""
    with suppress(ValueError):
        weapon = Weapon(weapon_index)

        if weapon.owner is None:
            weapon.remove()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event('player_spawn')
def on_player_spawn(game_event):
    """Prepare the spawning player."""
    player = Player.from_userid(game_event['userid'])

    if not player.dead and player.team > 1:
        prepare_player(player)


@Event('player_death')
def on_player_death(game_event):
    """Respawn the victim and handle attacker rewards."""
    # Respawn the victim
    victim = Player.from_userid(game_event['userid'])
    victim.delay(int(cvar_respawn_delay), victim.spawn, (True, ))

    # Handle attacker rewards, if the attacker and the victim are not on the same team
    attacker = Player.from_userid(game_event['attacker'])

    if attacker.team != victim.team:
        handle_player_reward(
            attacker, 'armor', abs(int(cvar_armor_reward)), abs(int(cvar_armor_max)) or 999
        )

        handle_player_reward(
            attacker, 'health', abs(int(cvar_health_reward)), abs(int(cvar_health_max)) or 999
        )


@Event('weapon_fire')
def on_weapon_fire(game_event):
    """Equip the player with another flashbang grenade."""
    player = Player.from_userid(game_event['userid'])
    player.delay(1.0, player.give_named_item, ('weapon_flashbang',), cancel_on_level_end=True)


# =============================================================================
# >> ENTITY HOOKS
# =============================================================================
@EntityPreHook(EntityCondition.is_bot_player, 'blind')
@EntityPreHook(EntityCondition.is_human_player, 'blind')
def on_pre_blind(stack_data):
    """Block blinding players."""
    return False


@EntityPreHook(EntityCondition.is_bot_player, 'deafen')
@EntityPreHook(EntityCondition.is_human_player, 'deafen')
def on_pre_deafen(stack_data):
    """Block deafening players."""
    return False


@EntityPreHook(EntityCondition.is_bot_player, 'drop_weapon')
@EntityPreHook(EntityCondition.is_human_player, 'drop_weapon')
def on_pre_drop_weapon(stack_data):
    """Remove the droppped weapon after about two seconds."""
    # Get a Player object for the first stack_data item
    player = make_object(Player, stack_data[0])

    # Get the player's active weapon
    active_weapon = player.get_active_weapon()

    # Remove the weapon after two seconds, if it is valid
    if active_weapon is not None:
        player.delay(2.0, remove_weapon, (player.get_active_weapon().index,), cancel_on_level_end=True)


@EntityPreHook(EntityCondition.is_bot_player, 'bump_weapon')
@EntityPreHook(EntityCondition.is_human_player, 'bump_weapon')
def on_pre_bump(stack_data):
    """Block bumping into another flashbang, if the player already owns one."""
    # Get a Weapon object from the second stack_data item
    weapon = make_object(Weapon, stack_data[1])

    # Block bumping into the weapon and remove it later, if it is not a flashbang
    if weapon.classname != 'weapon_flashbang':
        weapon.delay(2.0, remove_weapon, (weapon.index,), cancel_on_level_end=True)
        return False

    # Get a Player object from the first stack_data item
    player = make_object(Player, stack_data[0])

    # Get the player's active weapon
    active_weapon = player.get_active_weapon()

    # Remove it later, if it is no flashbang
    if active_weapon is not None:
        if active_weapon.classname != 'weapon_flashbang':
            player.delay(2.0, remove_weapon, (active_weapon.index,), cancel_on_level_end=True)
            player.delay(1.0, player.give_named_item, ('weapon_flashbang',), cancel_on_level_end=True)

        # Also block bumping into it
        return False
