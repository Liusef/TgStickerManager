import logging
from logging import debug, info, warning, error, critical

from src import utils, gvars
from src.Qt import gui


def main():
    info('===== Main method run =====')
    gui.main()


if __name__ == '__main__':
    main()

