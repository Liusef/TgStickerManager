import logging
from logging import debug, info, warning, error, critical

from src import utils, gvars
from src.Qt import gui


def main():
    utils.setup_logging(
        level=logging.DEBUG,
        console=True,
        file=True,
        path=gvars.DATAPATH + 'log.txt'
    )
    info('===== Main method run =====')
    debug('logger instantiated')
    gui.main()


if __name__ == '__main__':
    main()

