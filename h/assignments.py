# assignments.py


from enum import Enum
from .planet import Planet
import logging


#
# Handlers should mutate the ship. No need to return values.
#


def handle_free(ship):
    #
    # Make it mine, then consider defending.
    #
    try:
        p = ship.closest_planet(where=lambda p: p.is_mineable())
        ship.navigate(p)
        ship.task = IS.MINING
        ship.target = p
    except IndexError as e:
        # logging.exception("handle_free: " + str(e))
        ship.task = IS.DEFENDING
        ship.target = None  # figure out what to defend later.


def handle_mining(ship):
    if (not ship.target) or not isinstance(ship.target, Planet):
        try:
            ship.target = ship.closest_planet(where=lambda p: p.is_mineable())
        except IndexError:
            # no more planets to mine
            ship.task = IS.FREE
            ship.target = None
            return None

    if ship.docking_status is ship.DockingStatus.DOCKED:
        return None  # assumes that is currently docked at ship.target
    elif ship.docking_status is ship.DockingStatus.DOCKING:
        pass
        # if (not ship.target.is_mine()) or ship.target.is_full():
        #     pass
        #     # ship.task = IS.FREE
        #     # ship.target = None
        #     # ship.undock()  # can we undock while docking? can we just thrust?
        # return None  # NOTE: is extra weak at this time...
    elif ship.docking_status is ship.DockingStatus.UNDOCKING:
        pass
        # if ship.target.is_mine() and (not ship.target.is_full()):
        #     ship.dock(ship.target)  # can we dock? Do we have to wait?
        # return None  # TODO: can you stop undocking?
    elif ship.docking_status is ship.DockingStatus.UNDOCKED:
        if ship.target.is_mineable():
            if ship.can_dock(ship.target):
                ship.dock(ship.target)
            else:
                ship.navigate(ship.closest_point_to(ship.target))
        else:
            ship.task = IS.FREE
            ship.target = None
            return None


def handle_invading(ship):
    # INVADING - add to target's invasion forces
    if not ship.target:
        try:
            ship.target = ship.closest_planet(where=lambda p: p.is_someone_elses())
        except IndexError:
            ship.target = ship.closest_planet(where=lambda p: p.is_mine())

    if ship.target.is_mineable():
        ship.task = IS.MINING
    elif ship.target.is_mine():
        ship.task = IS.DEFENDING
    else:
        ship.target.forces.add(ship)


def handle_defending(ship):
    # Assign a reasonable target
    if not ship.target or not isinstance(ship.target, Planet):
        try:  # find planet to defend
            ship.target = ship.closest_planet(where=lambda p: p.is_mine())
        except IndexError:
            # TODO: what to do when we don't have anymore planets
            logging.info("handle_defending: Could not find planet to defend.")
            ship.task = IS.INVADING
            ship.target = None
            return None

    # DEFENDING - add self to nearest planet's forces
    if ship.target.is_mine():
        ship.target.forces.add(ship)
    else:
        ship.task = IS.INVADING


# def handle_skirmishing(ship):
#     # Assign
#     if not ship.target or not isinstance(ship.target, Planet):
#         try:
#             ship.target = ship.closest_planet(
#                 where=lambda p: p.is_someone_elses()
#             )
#         except IndexError:
#             ship.task = IS.FREE
#             return None

#     # SKIRMISHING - add self to nearest enemy planet's forces
#     if not ship.target.is_someone_elses():
#         if ship.target.is_empty():
#             ship.task = IS.MINING
#         else:  # is mine
#             ship.task = IS.DEFENDING
#     else:  # ship.is_someone_elses():  # is someone else's
#         ship.target.forces.add(ship)


def handle_crashing(ship):
    #
    # Crashing into a PLANET
    #
    if ship.target.is_mine():
        ship.target = None
        ship.task = IS.FREE
    else:
        ship.navigate(ship.target)  # TODO: make sure it ACTUALLY crashes


def handle_kamikaze(ship):
    #
    # Crashing into a SHIP
    #
    if ship.target.is_mine():
        # change course?
        ship.target = None
        ship.task = IS.FREE  # maybe find someone else?
    else:
        ship.navigate(ship.target)  # TODO: crash where this ship WILL BE.


class IS(Enum):
    FREE = handle_free

    DEFENDING = handle_defending  # planet

    MINING = handle_mining

    INVADING = handle_invading  # targeting planets

    CRASHING = handle_crashing  # colliding with planets
    KAMIKAZE = handle_kamikaze  # colliding with ships
