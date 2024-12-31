import tkinter as tk
import random
import os
import sys
import time
import queue
import threading
from threading import Thread



window = tk.Tk()


class tk_pessoa():
    pass

class tk_andar():
    pass


class traverse():

    def __init__(self):
        self.coluna = []

    def insere(self, btn ):
        self.coluna.append( btn )

    def trvrse(self):
        for I in range(len(self.coluna)):
            yield (self.coluna[I],'U')
        for I in reversed(range(len(self.coluna))):
            yield (self.coluna[I],'D')
        

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
        self.tvs = []
        self.slot =  [ [] for A in range( andares +1 )  ]
        self.elevadores = elevadores
        #
        l_final = andares + 3
        l0 = tk.Label( parent ,
                       text = kwargs.get("NomePredio", "Predio :: XYZ" )
                    )
        l0.grid( row=0, column=0, columnspan= elevadores )
                       
        for E in range(elevadores):
            self.tvs.append(  traverse() )
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
                self.tvs[E].insere(X)
                L.grid(row=l_final-A,column=0,pady=3)
                X.grid(row=l_final-A,column=E+1,pady=2)
                self.slot[andares-A].append( X )

    
    def exercitaElevador(self,mainWin, fila):
        self.fila = fila
        self.mainWin = mainWin
        self.exercita()

    def exercita(self):
        # Executa a movimentacao
        #
        while( True ):
            for E in range(self.elevadores):
                for I,M in self.tvs[E].trvrse():
                    # Cria uma thread para esse exercicio
                    self.fila.put( (I, "Mx"+M ) )
                    self.mainWin.event_generate('<<atuElevador>>')
                    time.sleep(1)
                # Espera ate a proxima interacao ,
                # << Atualiza o estado do painel monitor.
            time.sleep(1)
            
def processaElevador(mqueue , evento):
    # ** Levar em consideracao que
    # pode nao ter nada na fila.( ainda )
    #
    x,msg = mqueue.get_nowait()
    print("ProcessaElevador executado")
    x.configure(text=msg)
    # atualizar a tela.,
    pass
            

if __name__ == '__main__':

    mqElevador = queue.Queue()
    
    elev = 3
    andares = 5
    
    
    pnl1 = tk.Frame(window)
    pnl1.grid(row=1,column=2,padx=2,pady=2)
    
    P = tk_predio(pnl1, elev,andares)
    P.grid(row=1,column=3,pady=2,padx=2)

    # VEvent --> 
    window.bind('<<atuElevador>>', lambda e: processaElevador(mqElevador,e) )

    t = threading.Thread(target=P.exercitaElevador, args=(window, mqElevador,),daemon=True)
    t.start()
        
    window.mainloop()

    
