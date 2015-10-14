# makelevel.py

makelevel.py is a python script to create new level JSON files for AsteroidImpact.

It requires Python 2.7 and PyGame 1.9.1

see leveljson.md for format details of the generated level JSON files.

See section down below for how levels are created.

## command-line options


| Option                                       | Values | Default | Description |
|----------------------------------------------|--------|---------|-------------|
|`-h`, `--help`                                | | | Show help message and exit|
|--file FILE                                   | | [none] |        File to save level json to.|
|--seed SEED                                   | integer | [current time] |  Random number seed. If none supplied will use current time. |
|--target-count TARGET_COUNT                   | integer | 5 | Number of crystals to pick up. |
|--asteroid-count ASTEROID_COUNT               | integer | 5 | Number of asteroids to avoid. |
|--asteroid-sizes {small,medium,large,varied}  | one of {small,medium,large,varied} | large | Approximate size of asteroids. |
|--asteroid-speeds {slow,medium,fast,extreme}  | one of {slow,medium,fast,extreme} | slow | Approximate speed of asteroids. |
|--powerup-count POWERUP_COUNT                 | integer | 5 | Number of distinct power-ups to create for the player to pick up. |
|--powerup-initial-delay POWERUP_INITIAL_DELAY | float | 0.0 | Delay in seconds before first powerup is available. |
|--powerup-delay POWERUP_DELAY                 | float | 1.0 | Delay in seconds after powerup is used before next one becomes available.|
|--powerup-types {shield,slow,all,none}        | one of {shield,slow,all,none} | all | Types of powerups that are in level.|


# creation process
This script creates levels as follows.

1. Seed random number generator with supplied seed.
2. Choose random positions in the game area for the crystals to pick up.
3. Choose random diameter (from list of options at specified size), speed, and location for each asteroid. Choosing a speed avoids finding purely horizontal or vertical movement by doing the following
   1. Choose maximum speed from list chosen by option.
   2. Find random integer for x movement and y movement ranging from 1 to speed, inclusive
   3. Find random sign for x and y movement.
4. Start the power-up list with a power-up delaying power-up if chosen in the options
5. Add each power-up, with a randomly chosen type from the list at a randomly chosen position. After each power-up add a power-up delaying power-up of the specified `--powerup-delay`.

