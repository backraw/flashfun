# FlashFun

FlashFun is a [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python) plugin.

It allows you to kill enemies using Flashbang grenades by setting each player's health and armor to something low (default: 1 HP, 0 AP) on spawn.

See the [issues list](https://github.com/backraw/flashfun/issues) for current bugs. You can also post feature requests there.

## Features
* Free Flashbang grenades, of course
* Spawn Points - manageable in game via the Admin menu (say command: `!flashfun`)
* Damage Protection (timed on spawn, but indefinitely when using the Admin Menu)
* Reward system for killing sprees

## Game Support
| Game | Status |
| ---- | ------ |
| Counter-Strike: Source | Untested, but should work out of the box |
| Counter-Strike: Global Offensive | Stable |

## Installation
1. [Install Source.Python](http://wiki.sourcepython.com/general/installation.html)
2. Download the [latest FlashFun release](https://github.com/backraw/flashfun/releases) and unzip its contents to the game server's root folder (i.e.: **cstrike** for Counter-Strike: Source, **csgo** for Counter-Strike: Global Offensive)
3. Put `sp plugin load flashfun` into your server configuration file (i.e.: autoexec.cfg) - this can be any file that gets read after a map has changed
4. Change the map

## Configuration
The config file is generated and placed under `../<game root>/cfg/source-python/flashfun.cfg` after the plugin has been loaded up the first time.
```
// ========================================================================= //
//                             PLAYER ATTRIBUTES                             //
// ========================================================================= //

// Default Value: 1
// The health value the player starts with.
   flashfun_health_spawn 1


// Default Value: 0
// The armor value the player starts with.
   flashfun_armor_spawn 0


// ========================================================================= //
//                                  GAMEPLAY                                 //
// ========================================================================= //

// Default Value: 1
// The respawn delay in seconds.
   flashfun_respawn_delay 1


// Default Value: 3
// The spawn protection time in seconds.
   flashfun_spawn_protection_time 3


// ========================================================================= //
//                               PLAYER REWARDS                              //
// ========================================================================= //

// Default Value: 1
// Enable player rewards (0 disable).
   flashfun_enable_player_rewards 1


// ========================================================================= //
//                                SAY COMMANDS                               //
// ========================================================================= //

// Default Value: "!flashfun"
// The admin say command.
   flashfun_admin_saycommand "!flashfun"
```


## Reward System
In the plugin's data files (`../addons/source-python/data/plugins/flashfun/rewards/<game-name>.ini`), you can change the rewards a player can receive. Currently, only CS:GO is supported. The file contains something like this:
```
[health]
value = 3
max_value = 50

[armor]
value = 1
max_value = 30

[hegrenade]
type = "kills"
multiplier = 5

[glock]
type = "health"
multiplier = 7
clip = 2
ammo = 0

[hkp2000]
type = "kills"
multiplier = 12
clip = 2
ammo = 0

[deagle]
type = "kills"
multiplier = 20
clip = 1
ammo = 0

[fiveseven]
type = "health"
multiplier = 20
clip = 3
ammo = 0
```

### Property rewards
The player properties (`health`, `armor`) have a value and a maximum value. If the maximum value is `0`, it will be converted to `999` internally. You can turn those rewards off by setting the respective `value` to `0`.

Let's look at them more closely:
```
[health]
value = 3
max_value = 50

[armor]
value = 1
max_value = 30
```

Each time a player kills an enemy, they will gain 3 HP if their current HP is below 50 and 1 AP if their current AP is below 30.

**Note**: `value` is required, `max_value` is optional and will be set to `0` internally if it is not provided.

### Weapon rewards
The weapon rewards (`hegrenade`, `glock`, `usp`, ...) have a `type` and a `multiplier`. `type` defines which player property to respect for the `multiplier`. `type` can be any player property the Source.Python Player API exposes. This can be `kills`, `health`, `armor`, etc. I don't restrict the type, but, be sure to only set types which make sense. The weapon properties `clip` and `ammo` can be set for weapons which have those properties (everything besides grenades and melee weapons).

**Note**: `type` and `multiplier` are required. Everything else is optional.

Let's take a closer look at the HE grenade reward:
```
[hegrenade]
type = "kills"
multiplier = 5
```
As soon as the player reaches any number of kills that is in the range of `5` (5, 10, 15, ...), the player receives a HE grenade.

For `glock` and other weapons of the same type, `clip` and `ammo` can be set:
```
[glock]
type = "health"
multiplier = 7
clip = 2
ammo = 0
```

Here, the player receives a `glock` as soon as their HP is in the range of `7` (7, 14, 21, ...). If the weapon has the clip and ammo properties, it will be removed as soon as the it runs out of ammo.

You can add or remove any type of player property or weapon reward to your liking.


### Enjoy!
