#!/usr/bin/env python3

from pprint import pprint
import logging

from cassiopeia import riotapi

import chat

riotapi.set_region("EUW")
riotapi.set_api_key("__apikey__")
logging.basicConfig(level=logging.WARN, format='%(levelname)-8s %(message)s')


def main():
	c = chat.Monitor(chat.Regions.EUW, "__username__", "__password__")
	c.process(block=True)

if __name__ == '__main__':
	main()
