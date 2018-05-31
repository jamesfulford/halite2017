"""
Halite II Python 3 starter kit

See MyBot.py for a basic usage example. In short, you should initialize() at
the start, then in a loop, call get_map() to get the current game state, then
build up a list of commands and send them with send_command_queue().
"""

from . import constants
from .entity import Entity, Position
from .planet import Planet
from .ship import Ship
from . import game_map
from .networking import Game
from .assignments import IS
