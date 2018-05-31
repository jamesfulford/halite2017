from . import collision
from .entity import Position
from .planet import Planet
from .ship import Ship

import logging


class Map:
    """
    Map which houses the current game information/metadata.
    :ivar my_id: Current player id associated with the map
    :ivar width: Map width
    :ivar height: Map height
    """

    def __init__(self, my_id, width, height):
        self.my_id = my_id
        self.width = width
        self.height = height
        self._players = {}
        self._planets = {}

    #
    # PLAYERS
    #

    def get_me(self):
        """
        Returns the user's player
        """
        return self._players.get(self.my_id)

    def get_player(self, player_id):
        """
        Returns player with given id
        """
        return self._players.get(player_id)

    def all_players(self):
        """
        Lists all players
        """
        return list(self._players.values())

    #
    # PLANETS
    #

    def get_planet(self, planet_id):
        """
        Gets planet with that id
        """
        return self._planets.get(planet_id)

    def all_planets(self, exclude=None):
        """
        Lists all planets
        """
        results = list(self._planets.values())
        if exclude:
            results = list(filter(lambda s: s not in exclude, results))
        return results

    #
    # SHIPS
    #

    def all_ships(self, exclude=None):
        all_ships = []
        for player in self.all_players():
            all_ships.extend(player.all_ships())
        if exclude:
            all_ships = list(filter(lambda s: s not in exclude, all_ships))
        return all_ships

    #
    # CALCULATIONS
    #

    def _intersects_entity(self, target):
        """
        Check if the specified entity (x, y, r) intersects any planets. Entity is assumed to not be a planet.

        :param entity.Entity target: The entity to check intersections with.
        :return: The colliding entity if so, else None.
        :rtype: entity.Entity
        """
        for celestial_object in self.all_ships() + self.all_planets():
            if celestial_object is target:
                continue
            d = celestial_object - target
            if d <= celestial_object.radius + target.radius + 0.1:
                return celestial_object
        return None

    def obstacles_between(self, ship, target, ignore=()):
        """
        Check whether there is a straight-line path to the given point, without planetary obstacles in between.

        :param entity.Ship ship: Source entity
        :param entity.Entity target: Target entity
        :param entity.Entity ignore: Which entity type to ignore
        :return: The list of obstacles between the ship and target
        :rtype: list[entity.Entity]
        """
        obstacles = []
        excl = [ship, target]
        entities = ([] if issubclass(Planet, ignore) else self.all_planets(exclude=excl)) \
            + ([] if issubclass(Ship, ignore) else self.all_ships(exclude=excl))
        for foreign_entity in entities:
            if collision.intersect_segment_circle(ship, target, foreign_entity, fudge=ship.radius + 0.1):
                obstacles.append(foreign_entity)
        return obstacles

    def nearby_entities(self, entity, exclude=True):
        if exclude and not isinstance(exclude, list):
            exclude = [entity]

        return sorted(
            [e for e in
                self.all_ships(exclude=exclude) + self.all_planets(exclude=exclude)],
            key=lambda e: e - entity
        )

    def nearby_ships(self, entity, exclude=True):
        if exclude and not isinstance(exclude, list):
            exclude = [entity]

        return sorted(
            [e for e in
                self.all_ships(exclude=exclude)],
            key=lambda e: e - entity
        )

    def nearby_planets_by_distance(self, entity, exclude=True):
        if exclude and not isinstance(exclude, list):
            exclude = [entity]

        return sorted(
            [e for e in
                self.all_planets(exclude=exclude)],
            key=lambda e: e - entity
        )

    #
    # LINKING AND PARSING
    #

    def _link(self):
        """
        Updates all the entities with the correct ship and planet objects
        """
        for celestial_object in self.all_planets() + self.all_ships():
            celestial_object._link(self)
            celestial_object.map = self

    def _parse(self, map_string):
        """
        Parse the map description from the game.

        :param map_string: The string which the Halite engine outputs
        :return: nothing
        """
        tokens = map_string.split()

        self._players, tokens = Player._parse(tokens)
        self._planets, tokens = Planet._parse(tokens)

        assert(len(tokens) == 0)  # There should be no remaining tokens at this point
        self._link()


class Player:
    """
    :ivar id: The player's unique id
    """
    def __init__(self, player_id, ships={}):
        """
        :param player_id: User's id
        :param ships: Ships user controls (optional)
        """
        self.id = player_id
        self._ships = ships

    #
    # SHIPS
    #

    def all_ships(self):
        """
        :return: A list of all ships which belong to the user
        :rtype: list[entity.Ship]
        """
        return list(self._ships.values())

    def get_ship(self, ship_id):
        """
        :param int ship_id: The ship id of the desired ship.
        :return: The ship designated by ship_id belonging to this user.
        :rtype: entity.Ship
        """
        return self._ships.get(ship_id)

    #
    # REPRESENTATIONS
    #

    def __str__(self):
        return "Player {} with ships {}".format(self.id, self.all_ships())

    def __repr__(self):
        return self.__str__()

    #
    # LINKING AND PARSING
    #

    @staticmethod
    def _parse_single(tokens):
        """
        Parse one user given an input string from the Halite engine.

        :param list[str] tokens: The input string as a list of str from the Halite engine.
        :return: The parsed player id, player object, and remaining tokens
        :rtype: (int, Player, list[str])
        """
        player_id, *remainder = tokens
        player_id = int(player_id)
        ships, remainder = Ship._parse(player_id, remainder)
        player = Player(player_id, ships)
        return player_id, player, remainder

    @staticmethod
    def _parse(tokens):
        """
        Parse an entire user input string from the Halite engine for all users.

        :param list[str] tokens: The input string as a list of str from the Halite engine.
        :return: The parsed players in the form of player dict, and remaining tokens
        :rtype: (dict, list[str])
        """
        num_players, *remainder = tokens
        num_players = int(num_players)
        players = {}

        for _ in range(num_players):
            player, players[player], remainder = Player._parse_single(remainder)

        return players, remainder
