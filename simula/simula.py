

import concurrent.futures
import logging
import queue
import random
import threading
import time

from enum import Enum

from  nomesX import Nomes

Cadastros = Nomes()


class eDIRECAO(Enum):
    PARADO = 0,
    SUBIR = 1,
    DESCER = 2

    __strsX__ = ["PARADO", "SUBIR", "DESCER" ]
    
    def  __str__(self):
        return __strsX__[self] 


class eBOTAO(Enum):
    DESLIGADO = 0,
    LIGADO = 1

    def  __str__(self):
        if self == eBOTAO.LIGADO:
            return "LIGADO"
        else:
            return "DESLIGADO" 
    

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
        return "estado: {} ".format( str(self.__estado__) )


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
        return "{} :: {}\n".format( self.nome, super().__str__()  )


class cPessoa( cIdentidade ):


    def __init__( self, nome, dfltCasa , dfltDest ):
        super().__init__( nome )
        self.predioCasa = dfltCasa
        self.predioDestino = dfltDest
        self.emTransito = False
        logging.debug("Iniciando pessoa {}".format(nome))

    def  __str__(self):
        return " cPessoa :: {} >> {}\n".format( self.nome,super().__str__() )

class cEstadoElevador(Enum): 
        PARADO = 0,
        SUBINDO = 1,
        DESCENDO = 2,
        MANUTENCAO = 3,
        CONGELADO = 4,
        TESTE = 5
    
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

    def action(self):
        #
        pass
        
    def  __str__(self):
        return  "cElevador :: "+ str(self.numeroDoElevador) + "{}\n".format( [ str(B.estado) for B in self.noPainelIndicador ] ) 


class cAndar:
    
    def __init__( self, numero ):
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        self._lock = threading.Lock()
        self.subir = BOTAO()
        self.descer = BOTAO()

        #cPessoa
        self.noAndarParaSair = {}
        #cPessoa
        self.noAndarOcupado =  {}

    def chegouElevador(self, elev):
        # O elevador chegou,
        #
        encheu = False
        for K in self.noAndarParaSair.keys():
            # veja se essa pessoa esta indo na
            # mesma direcao do elevador.,
            #
            if self.noAndarParaSair[K].SobeOuDesce != elev.direcao:
                # nao é pra mim,
                #
                continue
            else:
                # mesma direcao ., ..
                # tenta entrar se houver espaco
                self._lock.acquire()
                try:
                    elev.entra(self.noAndarParaSair[K])
                    # entrou no elevador, .. contabiliza no andar
                    self.noAndarParaSair.pop(K)
                except ElevadorCheio:
                    # Nao tem mais espaco no Elevador
                    logging.debug(str(elev))
                    encheu = True
                except ElevadorEmManutencao:
                    # Nao tem como entrar, esta em manutencao
                    logging.debug(str(elev))
                finally:
                    self._lock.release()
                # Nao precisamos mais ficar aqui..
                # .. Ate mais, no proximo elevador.
                if encheu:
                    break
        if len(self.noAndarParaSair) == 0:
            if elev.direcao == cEstadoElevador.SUBINDO:
                self.subir.desativa()
            elif elev.direcao == cEstadoElevador.DESCENDO:
                self.descer.desativa()
            
        
    def saiDoElevador(self, pessoas ):    
        # Tira todas as pessoas desse elevador,
        for P in pessoas:
            #
            self._lock.acquire()
            self.noAndarOcupado[ P.chave ] = P
            P.ocupada(self)
            self._lock.release()
            #
            
    def estouSaindo(self,P):
        #
        self._lock.acquire()
        self.noAndarOcupado.pop( [P.chave] )
        self.noAndarParaSair[P.chave] = P
        self._lock.release()

        

class cPredio( cDestino ):
 
    def __init__( self, destino, andares, nElevadores = 5 ):
        super().__init__( destino )
        # inicializa o predio com seus andares,
        #
        self.niveis = cAndar( andares )
        self.elevadores =  list( cElevador( N , andares ) for N in range(nElevadores) )


        logging.info( "{} Elevadores >> \n".format( super().__str__() ) )
        for C in self.elevadores:
            logging.info( C )
        

class cBairro():

    def __init__(self):
        (self.cdBairro, self.nomeBairro) = Nomes.Bairro()
        self.Predios = []
        

    def novoPredio(self, destino, andares ):
        destino.cdBairro = self.cdBairro
        destino.nivel = andares
        elev = (andares % 4) + 2
        self.Predios.append( cPredio( destino, andares,  nElevadores = elev)
        

    def incluiPredio(self, predio):
        self.Predios.append(predio)
        


if __name__ == "__main__":    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    pessoasX = []
    bairro = cBairro()

    
    for px in range(1,10):
        bairro.incluiPredio( cPredio( cDestino("Predio {}".format(px) ) , int(random.random() * 10) ) )

    CP = Cadastros.Pessoa()
    for px in range( 1, 20 ):
        P = next(CP) 
        s =  cPessoa(P, cDestino("casa") , cDestino("casa") )
        pessoasX.append( cPessoa(P, cDestino("casa") , cDestino("casa") )  )

    logging.info( "Pessoas: {} :: {}".format( len(pessoasX) , [ str(P) for P in pessoasX ] )

    
