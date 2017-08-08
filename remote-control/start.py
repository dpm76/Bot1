'''
Created on 06/07/2017

@author: david
'''
from controller import Controller

def main():
    '''
    Executes the process logic
    '''
    controller = Controller()    
    
    try:
        controller.start("192.168.1.130", False)
    except Exception as e:        
        print(e)
    finally:
        controller.stop()
        

if __name__ == '__main__':
    main()