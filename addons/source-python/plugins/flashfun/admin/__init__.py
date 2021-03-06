# ../flashfun/admin.py

"""Provides the Admin menu."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python Imports
#   Listeners
from listeners import OnLevelInit
#   Menus
from menus import PagedMenu
from menus import PagedOption
#   Players
from players.entity import Player

# Plugin Imports
#   Util
from flashfun.util import equip_player
from flashfun.util import disable_damage_protection


# =============================================================================
# >> ADMIN MENU
# =============================================================================
class _AdminMenu(PagedMenu):
    """Class used to provide a way to send this menu when a submenu is closed."""

    # Store players who are currently using the Admin menu
    users = list()

    def register_submenu(self, submenu):
        """Always send this menu when a submenu is closed."""
        # Add the submenu
        self.append(PagedOption(submenu.title, submenu))

    def _unload_instance(self):
        """Clear the users dict on unload."""
        # Clear the users dict
        self.users.clear()

        # Continue base routine
        super()._unload_instance()


# Store a global instance of `_AdminMenu`
admin_menu = _AdminMenu(title='Admin Menu')


# =============================================================================
# >> ADMIN MENU CALLBACKS
# =============================================================================
@admin_menu.register_close_callback
def on_close_admin_menu(menu, player_index):
    """Enable default gameplay for the admin player who just closed the Admin menu."""
    player = Player(player_index)

    # Remove the player from the Admin menu users storage
    admin_menu.users.remove(player.userid)

    # Equip the player
    equip_player(player)

    # Disable spawn protection for the player
    disable_damage_protection(player.index)


@admin_menu.register_select_callback
def on_select_admin_submenu(menu, player_index, option):
    """Send the submenu chosen to the player."""
    option.value.send(player_index)


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    """Clear the Admin menu users dict."""
    admin_menu.users.clear()
