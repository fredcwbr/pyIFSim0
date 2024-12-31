import tkinter as tk
import random
import os
import sys
import time
import queue
from queue import Empty as qEmpty
import threading
from threading import Thread



class tk_pessoa():
    pass

class tk_andar():
    pass


class tk_btx(tk.Button):
    
    def __init__(self,parent,*args,**kwargs):
        prms = {k:v for k,v in kwargs.items() if k not in ['andar','elevador']  }
        super().__init__(parent,*args, command=self.mostra, **prms)
        self.idx = random.randrange(25663)
        self.text = self.idx
        self.andar = kwargs['andar']
        self.elevador = kwargs['elevador']

    def mostra(self):
        print("self.idx :{}".format(self.idx) )
        

class tk_predio(tk.Frame):
    def __init__(self,parent, elevadores,andares,*args,**kwargs):
        super().__init__(parent)
        #
        self.slot =  [  [ [] for B in range(andares) ] for A in range(elevadores) ]
        self.elevadores = elevadores
        #
        l_inicial = 3
        l0 = tk.Label( parent ,
                       text = kwargs.get("NomePredio", "Predio :: XYZ" )
                    )
        l0.grid( row=0, column=0, columnspan= elevadores )
                       
        for E in range(elevadores):
            for A in range(andares):
                L = tk.Label( parent,
                              text = "Andar {}".format(A) if A > 0 else "Saguao"
                            )
                X = tk_btx(parent,
                           height=1,
                           width=5,
                           relief=tk.SUNKEN,
                           bg = 'gray92' if E % 2 == 0 else 'gray90',
                           pady=2,
                           padx=2,
                           andar = A,
                           elevador = E
                    )
                L.grid(row=l_inicial+andares-A,column=0,pady=3)
                X.grid(row=l_inicial+andares-A,column=E+1,pady=2)
                self.slot[E][A].append( X )
        print( self.slot )

        
    def exercitaElevador(self,mainWin, fila):
        self.fila = fila
        self.mainWin = mainWin
        #
        while( True ):
            # Para cada Elevador,
            for N in range( len(self.slot) ):
                Mx = random.randrange( len(self.slot[ N ]) )
                # Indicadores do painel
                for MN in range(len(self.slot[ N ])):
                    for E in self.slot[ N ][MN]:
                        # Atualiza o elevador neste momento., 
                        # Cria uma thread para esse exercicio
                        MSG =  " " if MN != Mx else "Mx"
                        self.fila.put( ( E , MSG ) )
                print( "Enviados: {} msgs".format(self.fila.qsize() ) )
                self.mainWin.event_generate('<<atuElevador>>')
                time.sleep(1)
            # Espera ate a proxima interacao ,
            # << Atualiza o estado do painel monitor.
            time.sleep(1)
            
def processaElevador(mqueue , evento):
    # ** Levar em consideracao que
    # pode nao ter nada na fila.( ainda )
    #
    # print("ProcessaElevador executado")
    try:
        while True:
            x,msg = mqueue.get(block=False)
            print( x, msg ) 
            x.configure(text=msg)
    except qEmpty:
        pass
    # atualizar a tela.,
    


class interfacePredio:
    def __init__( self, mqElevador, elevadores, andares ):
        self.window = tk.Tk()
        pnl1 = tk.Frame(self.window)
        pnl1.grid(row=1,column=2,padx=2,pady=2)
        P = tk_predio(pnl1, elevadores ,andares)
        P.grid(row=1,column=3,pady=2,padx=2)
        # VEvent --> 
        self.window.bind('<<atuElevador>>', lambda e: processaElevador(mqElevador,e) )
        t = threading.Thread(target=P.exercitaElevador, args=(self.window, mqElevador,),daemon=True)
        t.start()
        self.window.mainloop()

if __name__ == '__main__':

    elev = 1
    andares = 5

    for I in [ 1 ]:
        mqElevador = queue.Queue()
        t = threading.Thread(
            target=interfacePredio,
            args=(mqElevador, elev+I , andares + I ),
            daemon=True
        )
        t.start()

        
    
    
