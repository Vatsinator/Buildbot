#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from ConfigParser import ConfigParser

import logger
from txutils import txupdate


def read_config(file='config.ini'):
    """
    Read config file.
    @param file:  The config file location.
    @return: Config.
    """
    if not os.path.isfile(file):
        print("Config file missing")
        sys.exit(1)

    config = ConfigParser()
    config.read(file)
    return config


def main():
    """
    Parse command line options, read config and run desired action.
    """
    description = "Vatsinator Buildbot automates server-side procedures for Vatsinator."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('command', choices=['txupdate'],
                        help='command to be run', metavar='command')
    parser.add_argument('--config', '-c', dest='config_file', default='config.ini',
                        help='config file location (default: config.ini)',
                        metavar='config_file')
    parser.add_argument('--logfile', '-l', dest='log_file', default='stdout',
                        help='file to log actions (default: stdout)', metavar='log_file')

    args = parser.parse_args()

    config = read_config(args.config_file)
    log_file = args.log_file
    if log_file != 'stdout':
        f = open(log_file, 'a')
        logger.output = f

    if args.command == 'txupdate':
        if not config.has_section('Repository'):
            print("Missing 'Repository' section in config file. See config.ini.sample for reference")
            sys.exit(1)

        txupdate(repodir=config.get('Repository', 'vatsinator'),
                 author=(config.get('Repository', 'author_name'), config.get('Repository', 'author_email')),
                 txbranch=config.get('Translations', 'txbranch')
        )


if __name__ == "__main__":
    main()

