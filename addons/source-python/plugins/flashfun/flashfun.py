# ../flashfun/flashfun.py

"""Kill enemies using flashbang grenades."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   Contextlib
from contextlib import suppress

# Source.Python Imports
#   Commands
from commands.typed import TypedSayCommand
#   Core
from core import OutputReturn
#   Entities
from entities.hooks import EntityPreHook
from entities.hooks import EntityCondition
#   Events
from events import Event
#   Memory
from memory import make_object
#   Listeners
from listeners import OnServerOutput
#   Players
from players.entity import Player
#   Weapons
from weapons.entity import Weapon

# Plugin Imports
#   Admin
from flashfun.admin import admin_menu
from flashfun.admin.submenus import spawn_locations_manager_menu
#   Config
from flashfun.config import cvar_armor_max
from flashfun.config import cvar_armor_reward
from flashfun.config import cvar_health_max
from flashfun.config import cvar_health_reward
from flashfun.config import cvar_respawn_delay
from flashfun.config import cvar_admin_saycommand
#   Info
from flashfun.info import info
#   Util
from flashfun.util import enable_damage_protection
from flashfun.util import handle_player_reward
from flashfun.util import prepare_player
from flashfun.util import remove_weapon


# =============================================================================
# >> REGISTER ADMIN MENU SUBMENUS
# =============================================================================
admin_menu.register_submenu(spawn_locations_manager_menu)


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
    with suppress(ValueError):
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

    # Block bumping into the weapon and remove it later, if the player is currently using the Admin menu
    if player.userid in admin_menu.users:
        weapon.delay(2.0, remove_weapon, (weapon.index,), cancel_on_level_end=True)
        return False

    # Get the player's active weapon
    active_weapon = player.get_active_weapon()

    # Remove it later, if it is no flashbang
    if active_weapon is not None:
        if active_weapon.classname != 'weapon_flashbang':
            player.delay(2.0, remove_weapon, (active_weapon.index,), cancel_on_level_end=True)
            player.delay(1.0, player.give_named_item, ('weapon_flashbang',), cancel_on_level_end=True)

        # Also block bumping into it
        return False


# =============================================================================
# >> SAY COMMANDS
# =============================================================================
@TypedSayCommand(str(cvar_admin_saycommand), permission=f'{info.name}.admin')
def on_saycommand_admin(command_info):
    """Send the Admin menu to the player."""
    # Get a PlayerEntity instance for the player
    player = Player(command_info.index)

    # Protect the player indefinitely
    enable_damage_protection(player)

    # Remove all the player's weapons
    for weapon in player.weapons():
        weapon.remove()

    # Send the Admin menu to the player
    admin_menu.users.append(player.userid)
    admin_menu.send(command_info.index)

    # Block the text from appearing in the chat window
    return False


# =============================================================================
# >> CONSOLE OUTPUT
# =============================================================================
@OnServerOutput
def on_server_output(severity, msg):
    """Block server warnings this plugin causes."""
    if 'bot spawned outside of a buy zone' in msg:
        return OutputReturn.BLOCK

    if 'hostage position' in msg:
        return OutputReturn.BLOCK

    return OutputReturn.CONTINUE
