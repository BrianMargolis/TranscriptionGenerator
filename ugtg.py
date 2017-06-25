import logging
from logging import Logger
import os
import sys
import traceback

from getopt import getopt, GetoptError
from urllib.error import URLError

from HTMLParseError import HTMLParseError
from UltimateGuitarInteractor import UltimateGuitarInteractor

DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_IMPORT_FILE_NAME = "links.txt"
DEFAULT_EXPORT_DIRECTORY_NAME = "ugtg_output"
LOGGER_NAME = 'logger'


def main():
    # configure logger
    logger_name = LOGGER_NAME
    logger = configure_logger(DEFAULT_LOG_LEVEL, logger_name)

    # get arguments from command line, else use defaults
    export_directory, import_file, log_level = get_arguments(logger_name, DEFAULT_LOG_LEVEL)

    set_level(log_level, logger_name)

    logger.info("Reading links from {0}".format(import_file))
    links = get_links(import_file, logger_name)
    logger.info("Found {0} links.".format(str(len(links))))

    for link in links:
        logger.info("Getting chords from {0}".format(link))  # TODO: make hyperlink
        ugint = UltimateGuitarInteractor(link, export_directory, logger_name)
        try:
            ugint.run()
            logger.info("Got chords for {0}".format(ugint.get_title_and_artist_string()))
        except URLError:
            logger.error(traceback.format_exc())
            logger.error("URLError: link: {0}".format(link))
        except HTMLParseError as e:
            logger.error(traceback.format_exc())
            if (len(e.args) > 0):
                logger.error("HTMLParseError: {0} link: {1}".format(e.args[0], link))
            else:
                logger.error("HTMLParseError: link: {0}".format(link))

    logger.info("Done. Files exported to {0}".format(export_directory))


def get_arguments(logger_name: str, default_log_level: int) -> [str, str, int]:
    logger = logging.getLogger(logger_name)
    export_directory = ""
    import_file = ""
    log_level = default_log_level

    try:
        opts, args = getopt(sys.argv[1:], "hvdsi:o:")
    except GetoptError:
        display_help()
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            display_help()
            sys.exit(0)
        elif opt == '-s':  # silent
            log_level = logging.CRITICAL
        elif opt == '-v':  # verbose
            log_level = logging.INFO
        elif opt == '-d':  # debug
            log_level = logging.DEBUG
        elif opt == '-i':
            import_file = arg
        elif opt == '-o':
            export_directory = arg

    opts_used = [row[0] for row in opts]

    # attempt default for input file
    if '-i' not in opts_used:
        # no input file provided, default file exists
        if os.path.exists(DEFAULT_IMPORT_FILE_NAME):
            print("No input file specified. Using {0} found in working directory {1} \n".format(DEFAULT_IMPORT_FILE_NAME, os.getcwd()))
            import_file = DEFAULT_IMPORT_FILE_NAME
        # no input file provided, default file doesn't exist. exit
        else:
            logger.critical("No input file specified. Default file {0} not found in {1}".format(DEFAULT_IMPORT_FILE_NAME, os.getcwd()))
            logger.critical("Exiting.")
            sys.exit(1)

    # attempt default for output directory
    if '-o' not in opts_used:
        # directory doesn't exist yet, create it
        if not os.path.exists(DEFAULT_EXPORT_DIRECTORY_NAME):
            print("No output location specified. Creating {0} in working directory {1} \n".format(DEFAULT_EXPORT_DIRECTORY_NAME, os.getcwd()))
            os.makedirs(DEFAULT_EXPORT_DIRECTORY_NAME)
            export_directory = DEFAULT_EXPORT_DIRECTORY_NAME
        # try suffixes if the directory already exists
        else:
            path_suffix = 0
            while os.path.exists("{0}_{1}".format(DEFAULT_EXPORT_DIRECTORY_NAME, str(path_suffix))):
                path_suffix += 1
            print("No output location specified. Creating {0}_{1} in working directory {2} \n".format(DEFAULT_EXPORT_DIRECTORY_NAME, path_suffix, os.getcwd()))
            os.makedirs("{0}_{1}".format(DEFAULT_EXPORT_DIRECTORY_NAME, str(path_suffix)))
            export_directory = "{0}_{1}".format(DEFAULT_EXPORT_DIRECTORY_NAME, str(path_suffix))

    assert export_directory != ""
    assert import_file != ""

    return export_directory, import_file, log_level


def configure_logger(level: int, logger_name: str) -> Logger:
    logger = logging.getLogger(logger_name)  # can use more descriptive name if needed later
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.NOTSET)
    # logger.addHandler(ch)
    set_level(level, logger_name)
    return logger


def set_level(level: int, logger_name: str) -> None:
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)


def get_links(file_name: str, logger_name: str) -> list:
    logger = logging.getLogger(logger_name)
    if not file_name.endswith('.txt'):
        logger.critical("{0} is the incorrect file type. Exiting.".format(file_name))
        sys.exit(1)

    try:
        file = open(file_name)
        links = list(file)
    except FileNotFoundError:
        logger.critical(traceback.format_exc())
        logger.critical("{0} is not a valid file. Exiting.".format(file_name))
        sys.exit(1)

    for i in range(len(links)):
        links[i] = links[i].replace("\n", "")

    return links


def display_help() -> None:
    print("Use:")
    print("python ugtg.py -i [input .txt file] -o [output directory]")
    print("-v for verbose output; -d for very verbose, debug-level output; -s for silence")
    print("python -h to show this help message")
    print("------------------------------------------------------------------------------------")
    print("Default values:")
    print("If no input file is provided, ugtg will default to links.txt in the working directory if it exists.")
    print("If no output directory is provided, output/ will be created in the working directory.")
    print("Defaults to silence.")


if __name__ == '__main__':
    main()
