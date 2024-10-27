
from enum import Enum
import random

import nomesX as nomes



class eBOTAO(Enum):
    DESLIGADO = 0,
    LIGADO = 1

class BOTAO:
    DESLIGADO = eBOTAO.DESLIGADO
    LIGADO = eBOTAO.LIGADO


    def __init__(self):
        self.__estado__ = type(self).DESLIGADO
        
    def ativa(self):
        self.__estado__ = type(self).LIGADO
        
    def desativa(self):
        self.__estado__ = type(self).DESLIGADO

    @property 
    def estado(self):
        return self.__estado__

    def  __str__(self):
        return "estado: {} ".format( self.__estado__ )


class cPosicao:

    def __init__(  self, x = 0 , y = 0 , cdCidade = 0, cdBairro = 0 , nivel = 0 ):
        self.cdCidade = cdCidade
        self.cdBairro = cdBairro
        self.x = x
        self.y = y
        self.nivel = nivel
    
    #@property
    #def cdCidade(self):
    #     # Este código é executado quando alguém for
    #     # ler o valor de self.nome
    #     return self._cdCidade

    ##    @cdCidade.setter
    ##    def cdCidade(self, value):
    ##         # este código é executado sempre que alguém fizer 
    ##         # self.nome = value
    ##         self._cdCidade = value
        
    def distancia(self, x,y):
        # Retorna a distancia polar equivalente entre os pontos A,B 
        return sqr( (self.x - x)**2 + (self.y - y)**2 )

    def  __str__(self):
        return "cdCidade : {}; cdBairro {}; x {} , y {} , nv {}".format(
                self.cdCidade,
                self.cdBairro,
                self.x,
                self.y,
                self.nivel
             )


class cIdentidade(cPosicao):
    
    def __init__( self, nome, x = 0 , y = 0 , cdCidade = 0, cdBairro = 0 , nivel = 0 ):
        super().__init__( x = 0 , y = 0 , cdCidade = 0, cdBairro = 0 , nivel = 0 )
        self.nome = nome
     
    def  __str__(self):
        return "nome: {} :: {}".format( self.nome, super().__str__() )



class cDestino( cIdentidade ) :

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tempoInterTransito = 0
        self.penalidadeTransitoNivel = 0
        self.penalidadeTransitoBairro = 0
        self.penalidadeTransitoCidade = 0
        self.posicaoGeo   = 0

    def  __str__(self):
        return " cDestino :: {}".format( self.nome, super().__str__()  )


class cPessoa( cIdentidade ):


    def __init__( self, nome, dfltCasa , dfltDest ):
        super().__init__( nome )
        self.predioCasa = dfltCasa
        self.predioDestino = dfltDest
        self.emTransito = False
        # print("Iniciando pessoa {}".format(nome))

    def  __str__(self):
        return " cPessoa :: {} >> {}".format( self.nome,super().__str__() )



class cElevador:
    
    def __init__( self, numero, andaresPredio ):
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        self.emTransito = False
        self.qualAndar = 0
        self.numeroDoElevador = numero
        #cPessoa
        self.noAndarParaSair = []
        #cPessoa
        self.noPainelIndicador = list( BOTAO() for B in range(andaresPredio ) )  
        
    def  __str__(self):
        return "cElevador :: {} >> {}".format( self.numeroDoElevador,
                                    [ B.estado for B in self.noPainelIndicador] ) 


class cAndar:
    
    def __init__( self, numero ):
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        self.subir = BOTAO()
        self.descer = BOTAO()

        #cPessoa
        self.noAndarParaSair = []
        #cPessoa
        self.noAndarOcupado = []



class cPredio( cDestino ):
 
    def __init__( self, destino, andares ):
        super().__init__( destino )
        # inicializa o predio com seus andares,
        #
        self.niveis = cAndar( andares )
        self.elevadores =  list( cElevador( N , andares ) for N in range(5) )


        print("Elevadores >> \n")
        for C in self.elevadores:
            print( "{} , {}\n".format( C,  str(C) ) )
        


if __name__ == "__main__":
    pessoasX = []
    predios = []

    
    for px in range(1,10):
        predios.append( cPredio( cDestino("Predio {}".format(px) ) , int(random.random() * 10) ) )

    for P in nomes.nomesPessoas():
        s =  cPessoa(P, cDestino("casa") , cDestino("casa") )
        # print( s )
        pessoasX.append( cPessoa(P, cDestino("casa") , cDestino("casa") )  )

    print( len(pessoasX) , [ str(P) for P in pessoasX ] )

    
