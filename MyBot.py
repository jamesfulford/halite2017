import h
import logging
import traceback
import sys


try:
    GAME = h.Game("Maccabee")

    #
    #
    ##############
    # Game Start #
    ##############
    #
    #

    while True:
        MAP = GAME.update_map()
        ME = MAP.get_me()

        #
        # Execute assigned tasks
        #
        for ship in ME.all_ships():
            try:
                ship.resolve_task()
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                for line in lines:
                    logging.exception(line)

        for planet in MAP.all_planets():
            if planet.forces:
                if planet.is_empty():
                    logging.info("{} is empty".format(planet))
                    for ship in planet.forces:
                        ship.target = planet
                        ship.task = h.IS.MINING
                        ship.resolve_task()
                elif planet.is_mine():
                    if planet.is_mineable():
                        logging.info("{} is mineable".format(planet))
                        for ship in planet.forces:
                            ship.target = planet
                            ship.task = h.IS.MINING
                            ship.resolve_task()
                    else:
                        logging.info("{} is mine".format(planet))
                        if len(planet.forces) > 4:
                            for ship in planet.forces:
                                ship.task = h.IS.INVADING
                                ship.target = None
                                ship.resolve_task()
                            planet.forces = set()
                        else:
                            for ship in planet.forces:
                                ship.navigate(ship.closest_point_to(planet))

                elif planet.is_someone_elses():
                    logging.info("{} is someone elses".format(planet))
                    ds = planet.all_docked_ships()
                    for ship in planet.forces:
                        ds.sort(key=lambda s: s - ship)
                        ship.navigate(ship.closest_point_to(ds[0]))

                logging.info("{}".format(planet.forces))

        for ship in ME.all_ships():
            if ship.command:
                # logging.info(ship.command)
                GAME.command(ship.command)
            else:
                pass
                # logging.info("No command: {}".format(ship))

        GAME.end_turn()
except Exception as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    for line in lines:
        logging.exception(line)
