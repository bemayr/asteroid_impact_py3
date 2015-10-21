************
makelevel.py
************

makelevel.py
==================

makelevel.py is a python script to create new level JSON files for AsteroidImpact.

It requires Python 2.7 and PyGame 1.9.1

See :doc:`/leveljson` for format details of the generated level JSON files.

See :ref:`makelevel-creation-process` below for how levels are created.

.. _makelevel-creation-process:

======================
Creation Process
======================

The output of makelevel.py is a JSON file with positions for each crystal, power-up, and initial positions and directions for each asteroid. To run the same way repeatably, the game when running does not use any random number generator. Only makelevel.py which creates the level files uses a random number generator.

This script creates levels as follows.

1. Initialize the random number generator with the supplied seed, or the current time if no seed is specified. When the seed is specified, the random number generator will generate the same sequence of random numbers, and the same command-line arguments will generate exactly the same level. Changing the command-line arguments other than the seed may or may not change the created level because the same sequence of random numbers will not be used the same way if for example you change the number of crystals in a level, the later parts of level generation will see different random numbers before. However, the seed can be changed to "re-roll" a level with the same settings until you are happy with the values randomly chosen by this script.
2. Using the random number generator, choose random positions in the game area for the crystals to pick up.
3. Using the random number generator, choose random diameter (from list of options at specified size), speed, and location for each asteroid. Choosing a speed avoids finding purely horizontal or vertical movement by doing the following

   1. Choose maximum speed from list chosen by option.
   2. Find random integer for x movement and y movement ranging from 1 to speed, inclusive
   3. Find random sign for x and y movement.

4. Start the power-up list with a power-up delaying power-up if chosen in the options
5. Add each power-up, with a randomly chosen type from the list at a randomly chosen position. After each power-up add a power-up delaying power-up of the specified `--powerup-delay`.


Command-Line Options
==========================

The order of the command-line options does not matter.

Values (where applicable) come immediately after their command-line option. For example ``python makelevel.py --file samplefile.json``.

+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| Option                                            | Values                             | Default        | Description                                                                                                  |
+===================================================+====================================+================+==============================================================================================================+
| ``-h`` or ``--help``                              |                                    |                | Show help message and exit                                                                                   |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--file`` FILE                                   |                                    | [none]         | File to save level json to.                                                                                  |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--seed`` SEED                                   | integer                            | [current time] | Seed used to set initial state of random number generator. If none supplied will use current time.           |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--target-count`` TARGET_COUNT                   | integer                            | 5              | Number of crystals to pick up.                                                                               |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--asteroid-count`` ASTEROID_COUNT               | integer                            | 5              | Number of asteroids to avoid.                                                                                |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--asteroid-sizes`` {small,medium,large,varied}  | one of {small,medium,large,varied} | large          | Approximate size of asteroids.                                                                               |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--asteroid-speeds`` {slow,medium,fast,extreme}  | one of {slow,medium,fast,extreme}  | slow           | Approximate speed of asteroids.                                                                              |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--powerup-count`` POWERUP_COUNT                 | integer                            | 5              | Number of distinct power-ups to create for the player to pick up.                                            |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--powerup-initial-delay`` POWERUP_INITIAL_DELAY | float                              | 0.0            | Delay in seconds before first powerup is available.                                                          |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--powerup-delay`` POWERUP_DELAY                 | float                              | 1.0            | Delay in seconds after powerup is used before next one becomes available.                                    |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
| ``--powerup-types`` {shield,slow,all,none}        | one of {shield,slow,all,none}      | all            | Types of powerups that are in level.                                                                         |
+---------------------------------------------------+------------------------------------+----------------+--------------------------------------------------------------------------------------------------------------+
