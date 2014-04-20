#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from ConfigParser import ConfigParser

from txutils import txupdate


def read_config(file='config.ini'):
    if not os.path.isfile(file):
        print("Config file missing")
        sys.exit(1)
    
    config = ConfigParser()
    config.read(file)
    return config


def main():
    '''
    Parse command line options, read config and run desired action.
    '''
    description = "Vatsinator Buildbot automates server-side actions."
    
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('command', choices=['txupdate'],
                        help='command to be run', metavar='command')
    parser.add_argument('--config', '-c', dest='configFile', default='config.ini',
                        help='config file location (default: config.ini)',
                        metavar='config_file')
    
    args = parser.parse_args()
    
    config = read_config(args.configFile)
    
    if args.command == 'txupdate':
        if not config.has_section('Repository'):
            print("Missing 'Repository' section in config file. See config.ini.sample for reference")
            sys.exit(1)
        
        txupdate(repodir=config.get('Repository', 'vatsinator'),
                 i18ndir=config.get('Translations', 'i18ndir'),
                 txbranch=config.get('Translations', 'txbranch'),
                 txgencmd=config.get('Translations', 'txgencmd')
                 )


if __name__ == "__main__":
  main()
  
