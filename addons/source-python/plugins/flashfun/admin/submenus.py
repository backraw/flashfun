# ../flashfun/admin/submenus.py

"""Provide submenus for the Admin menu."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Menus
from menus import PagedMenu
from menus import PagedOption
#   Players
from players.entity import Player

# Script Imports
#   Admin
from flashfun.admin import admin_menu
#   Colors
from flashfun.colors import MESSAGE_COLOR_ORANGE
from flashfun.colors import MESSAGE_COLOR_WHITE
#   Spawn Locations
from flashfun.spawn_locations import SAFE_SPAWN_DISTANCE
from flashfun.spawn_locations import spawn_locations_manager
from flashfun.spawn_locations import SpawnLocation
#   Util
from flashfun.util import tell_player


# =============================================================================
# >> CONSTANTS
# =============================================================================
# Player location distance tolerance to a spawn location (in units)
SPAWN_LOCATION_TOLERANCE_UNITS = 20.0


# =============================================================================
# >> SPAWN LOCATIONS MANAGER MENU
# =============================================================================
def add_spawn_location_at_player_location(player):
    """Add a the player's current location as a spawn location."""
    # Get a list of the distance of all spawn locations to the player's current location
    distances = [spawn_location.get_distance(player.origin) for spawn_location in spawn_locations_manager]

    # Add the player's current location, if it is far enough away from all other spawn locations
    if not distances or min(distances) >= SAFE_SPAWN_DISTANCE:
        spawn_locations_manager.append(SpawnLocation.from_player_location(player))

        # Tell the player about the addition
        tell_player(
            player,
            f'{spawn_locations_manager_menu.title}: Spawn Location {MESSAGE_COLOR_WHITE}#{len(spawn_locations_manager)}'
            f' {MESSAGE_COLOR_ORANGE}has been added.'
        )

    # Send the spawn locations manager menu back to the player
    spawn_locations_manager_menu.send(player.index)


def remove_spawn_location_at_player_location(player):
    """Remove the spawn location at the player's current location."""
    # Find the spawn location closest to the player's current location
    for spawn_location in spawn_locations_manager.copy():
        if spawn_location in spawn_locations_manager and\
                spawn_location.get_distance(player.origin) < SPAWN_LOCATION_TOLERANCE_UNITS:

            # Store its position
            position = spawn_locations_manager.index(spawn_location) + 1

            # Remove it from the spawn location list
            spawn_locations_manager.remove(spawn_location)

            # Tell the player about the removal
            tell_player(
                player,
                f'{spawn_locations_manager_menu.title}: Spawn Location {MESSAGE_COLOR_WHITE}#{position}'
                f' {MESSAGE_COLOR_ORANGE}has been removed.'
            )

            # Break the loop
            break

    # Send the spawn locations manager menu back to the player
    spawn_locations_manager_menu.send(player.index)


def send_spawn_locations_list_to_player(player):
    """Send the Spawn Locations List menu to the player."""
    _spawn_locations_list_menu.send(player.index)


def save_spawn_locations(player):
    """Save current spawn locationts to file."""
    spawn_locations_manager.save()

    # Tell the player about it
    tell_player(player, f'{spawn_locations_manager_menu.title}: Spawn Locations have been saved.')

    # Send the spawn locations manager menu back to the player
    spawn_locations_manager_menu.send(player.index)


# Create the Spawn Locations Manager menu
spawn_locations_manager_menu = PagedMenu(
    [
        PagedOption('Add', add_spawn_location_at_player_location),
        PagedOption('Remove', remove_spawn_location_at_player_location),
        ' ',
        PagedOption('List', send_spawn_locations_list_to_player),
        ' ',
        PagedOption('Save', save_spawn_locations)
    ], title='Spawn Locations Manager'
)


# =============================================================================
# >> SPAWN LOCATIONS LIST MENU
# =============================================================================
# Create the Spawn Locations List menu
_spawn_locations_list_menu = PagedMenu(title='Spawn Locations List')


# =============================================================================
# >> SPAWN LOCATIONS LIST MENU CALLBACKS
# =============================================================================
@_spawn_locations_list_menu.register_build_callback
def on_spawn_locations_list_menu_build(menu, player_index):
    """Reload the menu with all available spawn locations."""
    menu.clear()
    menu.extend([
        PagedOption(f'#{index + 1}', spawn_location) for index, spawn_location in enumerate(spawn_locations_manager)]
    )


@_spawn_locations_list_menu.register_select_callback
def on_spawn_locations_list_menu_select(menu, player_index, option):
    """Spawn the player at the selected location."""
    # Get a PlayerEntity instance for the player
    player = Player(player_index)

    # Move player to the chosen spawn location
    option.value.move_player(player)

    # Send the Spawn Locations Manager menu to the player
    spawn_locations_manager_menu.send(player.index)


@_spawn_locations_list_menu.register_close_callback
def on_spawn_locations_list_menu_close(menu, player_index):
    """Send the Spawn Locations Manager menu to the player."""
    spawn_locations_manager_menu.send(player_index)


# =============================================================================
# >> SPAWN LOCATIONS MANAGER MENU CALLBACKS
# =============================================================================
@spawn_locations_manager_menu.register_select_callback
def on_spawn_locations_manager_menu_select(menu, player_index, option):
    """Handle the selected option."""
    # Get a PlayerEntity instance for the player
    player = Player(player_index)

    # Call the callback function from `option` on `player`
    option.value(player)


@spawn_locations_manager_menu.register_close_callback
def on_spawn_locations_manager_menu_close(menu, player_index):
    """Send the Admin Menu when the player closes the Spawn Locations Manager menu."""
    admin_menu.send(player_index)
