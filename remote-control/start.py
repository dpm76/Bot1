'''
Created on 06/07/2017

@author: david
'''
from controller import Controller
import argparse
import logging

def main():
    '''
    Executes the process logic
    '''
    APP_VERSION = "1.0.1"
    
    DEFAULT_IP = "192.168.1.130"
    
    logging.basicConfig(level=logging.DEBUG)
    
    parser = argparse.ArgumentParser(prog="Bot1's Remote Controller", description="Bot1 basic controller.")
    parser.add_argument("ip", metavar="ip", nargs="?", default=DEFAULT_IP,
                    help="Bot1's IP (default: {0}).".format(DEFAULT_IP))
    parser.add_argument("--testing", "-t", action="store_true",                   
                    help="Use testing mode")
    parser.add_argument("--local", "-l", action="store_true",                   
                    help="Runs locally (IP value will be ignored)")

    parser.add_argument("--version", action="version", version="%(prog)s v{0}".format(APP_VERSION))

    args = parser.parse_args()    
    
    
    controller = Controller()    
    
    try:
        controller.start(args.ip, args.testing, args.local)
    except Exception as e:        
        print(e)
    finally:
        controller.stop()
        

if __name__ == '__main__':
    main()