import logging
import threading
import time
import random

def thread_function(name):
    logging.info("Thread %s: iniciando", name)
    for II in range(1, 5 ):
        logging.info( " Dentro da thread {} :: interacao {}".format(name, II) )
        time.sleep(random.randint(1 , 5))
    logging.info("Thread %s: terminando", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : antes de criar ")
    ths = []
    for N in range( 1, 15):
        x = threading.Thread(target=thread_function, args=(N,))
        logging.info("Main    : antes de executar a thread")
        x.start()
        ths.append(x)
        
    logging.info("Main    : espera acabar a thread")
    for X in ths:
        X.join()
    logging.info("Main    : kboooooooo\n")
