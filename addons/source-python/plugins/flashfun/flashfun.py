# ../flashfun/flashfun.py

"""Kill enemies using flashbang grenades."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
from contextlib import suppress

# Source.Python Imports
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


# =============================================================================
# >> HELPER FUNCTIONS
# =============================================================================
def prepare_player(player):
    """Prepare the player."""
    # Set starting health and armor
    player.health = 1
    player.armor = 0

    # Give the player a flashbang
    player.give_named_item('weapon_flashbang',)


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
    """Respawn the victim."""
    victim = Player.from_userid(game_event['userid'])
    victim.delay(1.0, victim.spawn, (True, ))


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
