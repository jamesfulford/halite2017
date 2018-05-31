# planet.py
from .entity import Entity


class Planet(Entity):
    """
    A planet on the game map.
    """

    def __init__(self, planet_id, x, y, hp, radius, docking_spots, current,
                 remaining, owned, owner, docked_ships):
        super(Planet, self).__init__(x, y, radius, hp, owner, planet_id)
        self.num_docking_spots = docking_spots
        self.current_production = current
        self.remaining_resources = remaining
        self.owner = owner if bool(int(owned)) else None  # overrides
        self._docked_ship_ids = docked_ships
        self._docked_ships = {}
        self.forces = set()

    def get_docked_ship(self, ship_id):
        return self._docked_ships.get(ship_id)

    def all_docked_ships(self):
        return list(self._docked_ships.values())

    def is_empty(self):
        return not self.is_owned()

    def is_full(self):
        return len(self._docked_ship_ids) >= self.num_docking_spots

    def spaces_left(self):
        return max(p.num_docking_spots - len(p.all_docked_ships()), 0)

    def is_mineable(self):
        return (self.is_mine() and not self.is_full()) or self.is_empty()

    #
    # PARSING AND LINKING
    #

    def _link(self, map_state):
        """
        This function serves to take the id values set in the parse function and use it to populate the planet
        owner and docked_ships params with the actual objects representing each, rather than IDs
        """
        if self.owner is not None:
            self.owner = map_state._players.get(self.owner)
            for ship in self._docked_ship_ids:
                self._docked_ships[ship] = self.owner.get_ship(ship)

    @staticmethod
    def _parse_single(tokens):
        """
        Parse a single planet given tokenized input from the game environment.
        """
        plid, x, y, hp, r, docking, current, remaining, owned, owner, num_docked_ships, *remainder = tokens
        plid = int(plid)
        docked_ships = []

        for _ in range(int(num_docked_ships)):
            ship_id, *remainder = remainder
            docked_ships.append(int(ship_id))

        planet = Planet(int(plid),
                        float(x), float(y),
                        int(hp), float(r), int(docking),
                        int(current), int(remaining),
                        bool(int(owned)), int(owner),
                        docked_ships)

        return plid, planet, remainder

    @staticmethod
    def _parse(tokens):
        """
        Parse planet data given a tokenized input.
        """
        num_planets, *remainder = tokens
        num_planets = int(num_planets)
        planets = {}

        for _ in range(num_planets):
            plid, planet, remainder = Planet._parse_single(remainder)
            planets[plid] = planet

        return planets, remainder
