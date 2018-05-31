# ship.py

import math
from enum import Enum
import logging

from .entity import Entity
from .entity import Position
from .persist import Persist
from . import constants
from .assignments import IS


class Ship(Entity):
    task = Persist("task", IS.FREE)
    target = Persist("target", None)

    class DockingStatus(Enum):
        UNDOCKED = 0
        DOCKING = 1  # usually leave them alone
        DOCKED = 2  # usually leave them alone
        UNDOCKING = 3  # leave alone until they are UNDOCKED

    def __init__(self, player_id, ship_id, x, y, hp, vel_x, vel_y,
                 docking_status, planet, progress, cooldown):
        super(Ship, self).__init__(x, y, constants.SHIP_RADIUS, hp, player_id, ship_id)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.docking_status = docking_status
        self.planet = planet if (docking_status is not Ship.DockingStatus.UNDOCKED) else None
        self._docking_progress = progress
        self._weapon_cooldown = cooldown

        # custom
        # self.task = IS.FREE  # TODO: make sure not forgotten
        self.target = None  # TODO: make sure not forgotten
        self.command = None  # holds string command to send to game.
        self.map = None  # set when linked

    #
    # LOGIC
    #

    def can_dock(self, planet):
        return self - planet <= planet.radius + constants.DOCK_RADIUS + constants.SHIP_RADIUS

    def resolve_task(self):
        if not self.task:
            self.task = IS.FREE

        # logging.info("{0}: {1.__name__}".format(self, self.task))
        prev = self.task
        self.task(self)
        while prev != self.task:
            # logging.info("{0}: reassigned to {1.__name__}".format(self, self.task))
            prev = self.task
            self.task(self)

    #
    # COMMANDS
    #

    def thrust(self, mag, angle):
        # we want to round angle to nearest integer, but we want to round
        # magnitude down to prevent overshooting and unintended collisions
        self.command = "t {} {} {}".format(self.id, int(mag), round(angle))

    def dock(self, planet):
        self.command = "d {} {}".format(self.id, planet.id)

    def undock(self):
        self.command = "u {}".format(self.id)

    def navigate(self, target, speed=constants.MAX_SPEED, avoid_obstacles=True,
                 max_corrections=90, angular_step=1, ignore_ships=False,
                 ignore_planets=False):
        """
        Move a ship to a specific target position (Entity). It is recommended to place the position
        itself here, else navigate will crash into the target. If avoid_obstacles is set to True (default)
        will avoid obstacles on the way, with up to max_corrections corrections. Note that each correction accounts
        for angular_step degrees difference, meaning that the algorithm will naively try max_correction degrees before giving
        up (and returning None). The navigation will only consist of up to one command; call this method again
        in the next turn to continue navigating to the position.

        :param Entity target: The entity to which you will navigate
        :param game_map.Map game_map: The map of the game, from which obstacles will be extracted
        :param int speed: The (max) speed to navigate. If the obstacle is nearer, will adjust accordingly.
        :param bool avoid_obstacles: Whether to avoid the obstacles in the way (simple pathfinding).
        :param int max_corrections: The maximum number of degrees to deviate per turn while trying to pathfind. If exceeded returns None.
        :param int angular_step: The degree difference to deviate if the original destination has obstacles
        :param bool ignore_ships: Whether to ignore ships in calculations (this will make your movement faster, but more precarious)
        :param bool ignore_planets: Whether to ignore planets in calculations (useful if you want to crash onto planets)
        :return string: The command trying to be passed to the Halite engine or None if movement is not possible within max_corrections degrees.
        :rtype: str
        """
        # Assumes a position, not planet (as it would go to the center of the planet otherwise)
        distance = self - target
        angle = self % target
        ignore = () if not (ignore_ships or ignore_planets) \
            else Ship if (ignore_ships and not ignore_planets) \
            else Planet if (ignore_planets and not ignore_ships) \
            else Entity
        if avoid_obstacles:
            while (max_corrections > 0 and
                   self.map.obstacles_between(self, target, ignore)):
                angle += angular_step
                dx = math.cos(math.radians(angle)) * distance
                dy = math.sin(math.radians(angle)) * distance
                target = Position(self.x + dx, self.y + dy)
                max_corrections -= 1
            if max_corrections <= 0:
                # logging.info("Navigate: {} to {}".format(self, target))
                return None  # just no command
        speed = speed if (distance >= speed) else distance
        self.thrust(speed, angle)

    #
    # PARSING AND LINKING
    #

    def _link(self, map_state):
        """
        This function serves to take the id values set in the parse function and use it to populate the ship
        owner and docked_ships params with the actual objects representing each, rather than IDs
        """
        self.owner = map_state._players.get(self.owner)  # All ships should have an owner. If not, this will just reset to None
        self.planet = map_state._planets.get(self.planet)  # If not will just reset to none

    @staticmethod
    def _parse_single(player_id, tokens):
        """
        Parse a single ship given tokenized input from the game environment.
        """
        (sid, x, y, hp, vel_x, vel_y,
         docked, docked_planet, progress, cooldown, *remainder) = tokens

        sid = int(sid)
        docked = Ship.DockingStatus(int(docked))

        ship = Ship(player_id,
                    sid,
                    float(x), float(y),
                    int(hp),
                    float(vel_x), float(vel_y),
                    docked, int(docked_planet),
                    int(progress), int(cooldown))

        return sid, ship, remainder

    @staticmethod
    def _parse(player_id, tokens):
        """
        Parse ship data given a tokenized input.
        """
        ships = {}
        num_ships, *remainder = tokens
        for _ in range(int(num_ships)):
            ship_id, ships[ship_id], remainder = Ship._parse_single(player_id, remainder)
        return ships, remainder
