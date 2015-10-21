******************
 Game Script JSON 
******************

AsteroidImpact will optionally run a sequence of modes specified in script.json. This can be used to advance the player between multiple lists of levels, with blank screens in between. Advancing to the next step happens after a specified duration, or for the instructions screen when the user clicks with the mouse.

Sample: ::

    [
        {
            "action": "instructions",
            "duration": 10.0
        },
        {
            "action": "game",
            "levels": "levels/standardlevels.json",
            "duration": 20.0
        },
        {
            "action": "text",
            "text": "Custom instructions can appear here. They can be split into paragraphs by escaping newlines.\n\nThis is a second paragraph.\n\nThe next step after this one is a 5 second black screen.",
            "duration": 20.0
        },
        {
            "action": "blackscreen",
            "duration": 5.0
        },
        {
            "action": "game",
            "levels": "levels/hardlevels.json",
            "duration": 20.0
        },
        {
            "action": "blackscreen",
            "duration": 5.0
        }
    ]

Common Attributes
==================

Each step has the following attributes:

 * action: The name of the action. Should be "instructions", "game", "text" or "blackscreen"
 * `duration`: The duration in seconds (such as 12.5) after which to automatically advance to the next step. This can be null for some actions, see below.


Available step actions
=======================

``game``
--------

A null ``duration`` for the game step will prevent the player from advancing to the next step.

The ``levels`` value is required. It must point to a levels list json file. 

``instructions``
----------------

The ``instructions`` step displays instructions on how to play the game and each sprite the player will interact with.

A null ``duration`` for the instructions step will show a "Click to continue" message and allow the player to advance to the next step by clicking with their mouse. If a duration is specified the player will have to wait for that time to complete to move on to the next step.

``text``
----------------

The ``text`` step will display text specified in the ``text`` attribute on the screen for the specified duration with no available interaction to the player. The ``duration`` must be specified.

The text will be wrapped to fit on screen, but you can include newlines in the string and they will be included on string. Newlines in JSON must be escaped like ``\n``.

For example, here is text step with two lines of text with a blank line in between using two newline characters. ::

        {
            "action": "text",
            "text": "First Line\n\nSecond Line",
            "duration": 20.0
        },


``blackscreen``
----------------

The ``blackscreen`` step will display a black screen with no available interaction to the player. The ``duration`` must be specified.
