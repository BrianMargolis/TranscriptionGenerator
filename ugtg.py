from UltimateGuitarInteractor import UltimateGuitarInteractor
import sys
import logging


def main():
    # example command line call:
    # python ugtg.py [import file] [export location] [silent]
    import_file_name = sys.argv[1]  # sys.argv[0] is the name of the script, sys.argv[1] is the first argument
    export_location_name = sys.argv[2]
    run_silent = sys.argv[3] == 1

    logger_name = 'logger'
    logger = configure_logger(run_silent, logger_name)

    logger.info("Beginning operation. Import ")

    links = get_links(import_file_name, logger_name)  # TODO: test. need to modify file name as it comes in?

    for link in links:
        logger.info("Getting chords from {0}".format(link))  # TODO: make hyperlink
        ugint = UltimateGuitarInteractor(link, export_location_name, logger_name)
        success = ugint.run()
        if success:
            logger.info("Got chords for {0}".format(ugint.get_title_and_artist()))
        else:
            logger.warning("Failed to get chords.")

    logger.info("Done. Files exported to {0}".format(export_location_name))


def configure_logger(run_silent, logger_name):
    logger = logging.getLogger(logger_name)  # can use more descriptive name if needed later
    ch = logging.StreamHandler()
    if run_silent:
        ch.setLevel(logging.WARNING)
    else:
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger


def get_links(file_name, logger_name):
    logger = logging.getLogger(logger_name)
    if not file_name.endswith('.txt'):
        logger.severe("{0} is the incorrect file type. Exiting.".format(file_name))
        sys.exit(1)

    try:
        file = open(file_name)
        links = list(file)
    except FileNotFoundError:
        logger.severe("{0} is not a valid file. Exiting.".format(file_name))
        sys.exit(1)

    return links  # TODO: test. need to trim whitespace, etc.?


if __name__ == '__main__':
    main()
