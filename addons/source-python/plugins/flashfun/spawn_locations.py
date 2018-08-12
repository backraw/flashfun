# ../flashfun/spawn_locations/__init__.py

"""Provides spawn location management."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python Imports
#   JSON
import json
#   Random
import random

# Source.Python Imports
#   Core
from core import GAME_NAME
#   Engines
from engines.server import global_vars
#   Filters
from filters.players import PlayerIter
#   Listeners
from listeners import OnLevelInit
#   Mathlib
from mathlib import QAngle
from mathlib import Vector
#   Paths
from paths import PLUGIN_DATA_PATH

# Script Imports
#   Info
from flashfun.info import info


# =============================================================================
# >> CONSTANTS
# =============================================================================
# Safe distance between spawn locations (in units)
SAFE_SPAWN_DISTANCE = 150.0


# =============================================================================
# >> PRIVATE GLOBAL VARIABLES
# =============================================================================
# Store the path to the plugin's spawn locations data
# ../addons/source-python/data/plugins/flashfun/spawn_locations
_spawn_locations_path = PLUGIN_DATA_PATH.joinpath(info.name, 'spawn_locations', GAME_NAME)

# Create the spawn locations data path if it does not exist
if not _spawn_locations_path.exists():
    _spawn_locations_path.makedirs()


# =============================================================================
# >> CLASSES
# =============================================================================
class SpawnLocation(Vector):
    """Class used to attach a QAngle to a Vector and provide a JSON representation for the respective locations."""

    def __init__(self, x, y, z, angle):
        """Object initialization."""
        # Call Vector's constructor using the given xyz-coordinates
        super().__init__(x, y, z)

        # Store the QAngle object
        self._angle = angle

    @classmethod
    def from_player_location(cls, player):
        """Return a `SpawnLocation` (subclass) object from a player's location."""
        return cls(player.origin.x, player.origin.y, player.origin.z, player.view_angle)

    @staticmethod
    def find_spawn_location(player):
        """Return a unique spawn location for the player."""
        # Get a list of current player origins
        other_origins = [other.origin for other in PlayerIter(is_filters='alive') if player.userid != other.userid]

        shuffled_spawn_locations = spawn_locations_manager.copy()
        random.shuffle(shuffled_spawn_locations)

        # Loop through the shuffled list of spawn locations
        for spawn_location in shuffled_spawn_locations:

            # Calculate the distances between the spawn location and all player origins
            distances = [origin.get_distance(spawn_location) for origin in other_origins]

            # Return the spawn location found, if it is far enough away from the player
            if distances and min(distances) >= SAFE_SPAWN_DISTANCE:
                return spawn_location

        # Return the player's current location as a spawn location if no other one has been found
        return SpawnLocation.from_player_location(player)

    def move_player(self, player):
        """Move the player to this spawn location location."""
        player.origin = self
        player.view_angle = self.angle

    @property
    def angle(self):
        """Return the QAngle object."""
        return self._angle

    @property
    def json(self):
        """Return a JSON representation of the spawn location."""
        return {
            'vector': [self.x, self.y, self.z],
            'angle': [self.angle.x, self.angle.y, self.angle.z]
        }


class SpawnLocationDispatcher(object):
    """Class used to move a player to a spawn location location from another thread."""

    @staticmethod
    def perform_action(player):
        """Move the player to a spawn location location."""
        # Choose a random spawn location
        spawn_location = SpawnLocation.find_spawn_location(player)

        # Move the player to the spawn location found
        spawn_location.move_player(player)


class _SpawnLocationManager(list):
    """Class used to provide spawn location management.

        * load spawn locations from a JSON file
        * save spawn locations to a JSON file
    """

    def load(self):
        """Load spawn locations from the spawn locations data file for the current map."""
        # Skip if the file doesn't exist
        if not self.json_file.exists():
            return

        # Read the spawn locations data file into memory
        with self.json_file.open() as f:
            contents = json.load(f)

        # Append each entry as a `SpawnLocation` object
        for data in contents:
            self.append(SpawnLocation(*data['vector'], QAngle(*data['angle'])))

    def save(self):
        """Save spawn locations to the spawn locations data file for the current map."""
        # Skip if we have nothing to save
        if not self:
            return

        # Dump the contents of this list to file
        with self.json_file.open('w') as f:
            json.dump([spawn_location.json for spawn_location in self], f, indent=4)

    @property
    def json_file(self):
        """Return the path to the JSON file for the current map."""
        return _spawn_locations_path.joinpath(global_vars.map_name + '.json')


# =============================================================================
# >> PUBLIC GLOBAL VARIABLES
# =============================================================================
# Store a global instance of `_SpawnLocationManager`
spawn_locations_manager = _SpawnLocationManager()

# Load all spawn locations for the current map
spawn_locations_manager.load()


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def on_level_init(map_name):
    """Reload spawn locations."""
    spawn_locations_manager.clear()
    spawn_locations_manager.load()
