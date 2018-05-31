
import abc
import math
import logging


class Entity:
    """
    Then entity abstract base-class represents all game entities possible.
    As a base all entities possess a position, radius, health, an owner and an
    id. Note that ease of interoperability, Position inherits from Entity.
    """
    __metaclass__ = abc.ABCMeta
    _memory = {}

    def __init__(self, x, y, radius, health, player_id, entity_id):
        self.id = entity_id
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.owner = player_id
        self.map = None  # assigned by game_map after _link is called on this

    #
    # CALCULATIONS
    #

    def __sub__(self, target):
        """
        Calculates the distance (float) between this object and the target.
        """
        # TODO: memoize, and reset any distances with ships involved
        return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)

    def __mod__(self, t):
        """
        Calculates the angle between this object and the target in degrees.
        """
        return math.degrees(math.atan2(t.y - self.y, t.x - self.x)) % 360

    #
    # LOGIC
    #

    def is_mine(self):
        return self.is_owned() and (self.owner.id is self.map.my_id)

    def is_owned(self):
        return self.owner is not None

    def is_someone_elses(self):
        return self.is_owned() and not self.is_mine()

    #
    # MAPS
    #

    def closest_point_to(self, target, gap=2.5):
        """
        Find the closest point to the given ship near the given target,
        outside its given radius, with an added fudge of gap.
        """
        angle = target % self
        radius = target.radius + gap
        x = target.x + radius * math.cos(math.radians(angle))
        y = target.y + radius * math.sin(math.radians(angle))

        return Position(x, y)

    def nearby_planets_by_distance(self, where=None):
        planets = None
        if where:
            planets = list(filter(where, self.map.nearby_planets_by_distance(self)))
        else:
            planets = list(self.map.nearby_planets_by_distance(self))
        return planets

    def closest_planet(self, where=None):
        return self.nearby_planets_by_distance(where=where)[0]

    #
    # REPRESENTATIONS
    #

    def __str__(self):
        return "{}.{}{}".format(self.__class__.__name__, self.id,
            self.task.__name__.replace("handle_", " ") if hasattr(self, "task") else "")

    __repr__ = __str__

    #
    # PARSING AND LINKING
    #

    @abc.abstractmethod
    def _link(self, players, planets):
        pass


class Position(Entity):
    """
    A simple wrapper for a coordinate.
    """
    def __init__(self, x, y):
        super(Position, self).__init__(x, y, 0, None, None, None)

    def _link(self, players, planets):
        raise NotImplementedError("Position should not have link attributes.")
