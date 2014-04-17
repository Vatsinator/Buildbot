#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
from ConfigParser import ConfigParser
from txutils import txupdate

def readConfig(file = 'config.ini'):
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
  
  config = readConfig(args.configFile)
  
  if args.command == 'txupdate':
    txupdate(config.get('Repository', 'vatsinator'))
  

if __name__ == "__main__":
  main()
  