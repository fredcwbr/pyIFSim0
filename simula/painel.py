import tkinter as tk
import random
import logging
import os
import sys
import time
import queue
from queue import Empty as qEmpty
import threading
from threading import Thread




class tk_btx():
    # Uma coluna de elevadores
    # com tratamento adequado de mensagens para que apenas 1
    # esteja com Valor
    #
    def __init__(self,idElevador,coluna,andares=1,parent=None,*args,**kwargs):
        self.andares = andares
        self.idElevador = idElevador
        self.parent = parent
        self.mainWin = parent
        self.linha = [ None for A in range(self.andares) ]
        self.botao = None
        self.coluna = coluna
        self.fila = kwargs.get('fila',queue.Queue())

    def novoBotao(self, andar, *args, mainWin=None, parent=None, **kwargs):
        # Devolve um novo botao tkButton apropriado
        # computando o andar de acordo com a solicitacao
        # prms = {k:v for k,v in kwargs.items() if k not in ['andar','andares','elevador']  }
        if mainWin is not None:
            self.mainWin = mainWin
        if parent is None:
           parent = self.parent
        self.botao = tk.Button( parent, *args, command=self.detalhes, **kwargs )
        self.linha[andar] = self.botao
        
        return self.botao

    def reHabilita(self):
        for I in self.linha:
            I['state'] = 'active'

    def detalhes(self):
        for I in self.linha:
            I['state'] = 'disabled'

        new = tk.Toplevel(self.mainWin)
        lbl = tk.Label(new,text="Detalhes")
        lbl.pack()
        
        new.protocol("WM_DELETE_WINDOW", lambda: self.reHabilita() or new.destroy() )

    def noAndar(self,andar,MSG):
        # tratar a mensagem no andar certo,
        #
        for B in range(len(self.linha)):
            if self.linha[B] is None:
                continue
            self.fila.put( ( self.linha[B] , MSG if B == andar else "" ) )

        logging.debug( "Enviados: {} msgs".format( self.fila.qsize() ) )
        self.mainWin.event_generate('<<atuElevador>>')
        
        

class tk_predio(tk.Frame):
    def __init__(self,parent, nElevadores, andares,*args,**kwargs):
        super().__init__(parent)
        #
        self.fila = kwargs.get('fila',queue.Queue())
        self.andares = andares
        self.elevadores = [ tk_btx( random.randrange(2545357),
                               N,
                               andares=andares,
                               parent=parent,
                               fila=self.fila
                            ) for  N in range(nElevadores) ]
        #
        l_inicial = 3
        l0 = tk.Label( parent ,
                       text = kwargs.get("NomePredio", "Predio :: XYZ" )
                    )
        l0.grid( row=0, column=0, columnspan= nElevadores )
        
        # Monta o painel de visualizacao                        
        for E in self.elevadores:
            for A in range(andares):
                L = tk.Label( parent,
                              text = "Andar {}".format(A) if A > 0 else "Saguao"
                            )
                # Botoes para representacao 
                X = E.novoBotao(A,
                                height=1,
                                width=5,
                                relief=tk.SUNKEN,
                                pady=2,
                                padx=2,
                                bg = 'gray92' if E.coluna % 2 == 0 else 'gray90'
                        )
                L.grid(row=l_inicial+andares-A,column=0,pady=3)
                X.grid(row=l_inicial+andares-A,column=E.coluna+1,pady=2)


        
    def exercitaElevador(self):
        #
        while( True ):
            # Para cada Elevador,
            for N in self.elevadores:
                Mx = random.randrange(self.andares)
                # Indicadores do painel
                N.noAndar( Mx , "M??xx" )
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
    def __init__( self, elevadores, andares ):
        self.window = tk.Tk()
        pnl1 = tk.Frame(self.window)
        pnl1.grid(row=1,column=2,padx=2,pady=2)
        P = tk_predio(pnl1, elevadores ,andares, mainWin=self.window)
        P.grid(row=1,column=3,pady=2,padx=2)
        # VEvent --> 
        self.window.bind('<<atuElevador>>', lambda e: processaElevador(P.fila, e) )
        t = threading.Thread(target=P.exercitaElevador, args=(),daemon=True)
        t.start()
        self.window.mainloop()
        

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.ERROR,
                        datefmt="%H:%M:%S")

    elev = 1
    andares = 5

    for I in [ 1 ]:
        t = threading.Thread(
            target=interfacePredio,
            args=( elev+I , andares + I ),
            daemon=True
        )
        t.start()

        
    
    
