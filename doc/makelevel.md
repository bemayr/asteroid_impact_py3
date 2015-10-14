# makelevel.py

makelevel.py is a python script to create new level JSON files for AsteroidImpact.

It requires Python 2.7 and PyGame 1.9.1

## command-line options

```
$ python2.7 makelevel.py --help
usage: makelevel.py [-h] [--file FILE] [--seed SEED]
                    [--target-count TARGET_COUNT]
                    [--asteroid-count ASTEROID_COUNT]
                    [--asteroid-sizes {small,medium,large,varied}]
                    [--asteroid-speeds {slow,medium,fast,extreme}]
                    [--powerup-count POWERUP_COUNT]
                    [--powerup-initial-delay POWERUP_INITIAL_DELAY]
                    [--powerup-delay POWERUP_DELAY]
                    [--powerup-types {shield,slow,all,none}]

Create Asteroid Impact level.

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           File to save level json to.
  --seed SEED           Random number seed. If none supplied will use current
                        time.
  --target-count TARGET_COUNT
                        Number of crystals to pick up.
  --asteroid-count ASTEROID_COUNT
                        Number of asteroids to avoid.
  --asteroid-sizes {small,medium,large,varied}
                        Approximate size of asteroids.
  --asteroid-speeds {slow,medium,fast,extreme}
                        Approximate speed of asteroids.
  --powerup-count POWERUP_COUNT
                        Number of asteroids to avoid.
  --powerup-initial-delay POWERUP_INITIAL_DELAY
                        Delay in seconds before first powerup is available.
  --powerup-delay POWERUP_DELAY
                        Delay in seconds after powerup is used before next one
                        becomes available.
  --powerup-types {shield,slow,all,none}
                        Types of powerups that are in level.


```
