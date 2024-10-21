import logging
import threading
import time
import random


guardaProduz = threading.Semaphore(0)
guardaConsome = threading.Semaphore(1)

contadorCompartilhado = 0

def thread_produz(name):
    global contadorCompartilhado
    logging.info("Thread Produz %s: iniciando", name)
    for II in range(1, 15 ):
        guardaConsome.acquire()
        logging.info( "Dentro da thread Produz {} :: interacao {}".format(name, II) )
        contadorCompartilhado = contadorCompartilhado  + 1
        guardaProduz.release()
    logging.info("Thread Produz %s: terminando", name)


def thread_consome(name):
    global contadorCompartilhado
    
    logging.info("Thread consome : iniciando")
    for II in range(1, 15 ):
        logging.info( " Dentro da thread consome {} :: .. Aguardando ... ".format(name) )
        guardaProduz.acquire()
        logging.info("Consumindo >> {}".format(contadorCompartilhado) )
        time.sleep(0.025)
        guardaConsome.release()
    logging.info("Thread consome : terminando")



if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : antes de criar ")
    p =  threading.Thread(target=thread_produz, args=("Produz",))
    c =  threading.Thread(target=thread_consome, daemon=True, args=("Consome",))
    
    p.start()
    c.start()
        
    logging.info("Main    : espera acabar a thread")
    p.join()
    
    logging.info("Main    : kboooooooo\n")
