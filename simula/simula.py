 

import concurrent.futures
import logging
import queue
import random
import threading
import copy
from queue import Queue, Full, Empty
import time
import json

from enum import Enum

from  nomesX import Nomes
import  udpdiscovery as uD

class listEx(list):
    
    # Funcao acessoria para uma lista
    def algumChamando(self):
        logging.log(8,"verificando" )
        for n in self:
            logging.log(8, "{}:{}".format(type(n),n) )
            if n.ligado:
                return True
        return False


# Intervalo de tempo entre os movimentos do elevador.,
TMOVIMENTOELEVADOR = 4.0
# Intervalo de tempo entre a saida do elevador e a ocupacao .,
TMOVIMENTOENTRAANDAR = 3.0
# Tempo que PESSOA fica em algum lugar.,
TMINTRABALHO = 1
TMAXTRABALHO = 10

# Numero maximo de pessoas no elevador
CAPACIDADE_ELEVADOR = 12

Cadastros = Nomes()



class eTIPOS(Enum):
    CIDADE = 0
    BAIRRO = 1
    PREDIO = 2
    ANDAR  = 3
    PRACA  = 4
    RUA    = 5
    PESSOA = 6
    CASA   = 7
    ELEVADOR = 8
    REMOTO = 999

    __strsX__ = [
        'CIDADE',
        'BAIRRO',
        'PREDIO',
        'ANDAR',
        'PRACA',
        'RUA',
        'PESSOA',
        'CASA',
        'ELEVADOR',
        'REMOTO'
    ]
    def  __str__(self):
        return self.__strsX__[self.value] + ";" + str(self.value)

    

class eDIRECAO(Enum):
    PARADO = 0,
    SUBIR = 1,
    DESCER = 2

    __strsX__ = ["PARADO", "SUBIR", "DESCER" ]
    
    def  __str__(self):
        return __strsX__[self] 

class cPosicaoXYZ:
    def __init__(self, x = random.randrange(0,10), y = random.randrange(0,10), z = 0 ):
        logging.info("xyz -> {}, {}, {}".format( x,y,z ) )
        self.xlen = x
        self.ylen = y
        self.zlen = z

    @property        
    def posicao(self):
        return (self.xlen, self.ylen, self.zlen)
    
    def cheguei(self,x,y,z,/ ):
        logging.log(25,"Cheguei!! {}".format( (x,y,z) ) )
        self.xlen = x
        self.ylen = y
        self.zlen = z
    
    def distancia(self, x,y):
        # Retorna a distancia polar equivalente entre os pontos A,B (desconsidera nivel, .)
        return sqr( (self.xlen - x)**2 + (self.ylen - y)**2 )

    @property
    def nivel(self):
        return self.zlen

    @nivel.setter
    def nivel(self, Z):
        self.zlen = Z

    def __eq__(self, other):
        if other is None:
            return False
        logging.log(22,"{} __eq__ {} ".format( [self.xlen,self.ylen] , [other.xlen,other.ylen] ) )
        return self.xlen == other.xlen and self.ylen == other.ylen
        # estamos na mesma identidade,        

    def __ne__(self, other):
        if other is None:
            return False
        logging.log(22,"{} __ne__ {} ".format((self.xlen,self.ylen) ,(other.xlen,other.ylen)) )
        return self.xlen != other.xlen or self.ylen != other.ylen

    def mesmoNivel(self, other):
        if other is None:
            return False
        return self.zlen == other.zlen
        
    def __str__(self):
        return 'x {} : y {} : nivel {}'.format(self.xlen, self.ylen, self.zlen)
    


class eBOTAO(Enum):
    DESLIGADO = 0,
    LIGADO = 1

    def  __str__(self):
        if self == eBOTAO.LIGADO:
            return "L"
        else:
            return "D" 
    

class BOTAO:
    def __init__(self):
        self.__estado__ = eBOTAO.DESLIGADO
        
    def ativar(self):
        self.__estado__ = eBOTAO.LIGADO
        
    def desativar(self):
        self.__estado__ = eBOTAO.DESLIGADO

    @property 
    def estado(self):
        return self.__estado__

    @property 
    def ligado(self):
        return self.__estado__ == eBOTAO.LIGADO

    def  __str__(self):
        return "{}".format( str(self.__estado__) )


class cIdentidade(cPosicaoXYZ):
    
    def __init__( self, nome, tipo, cd=0 , **kwargs ):
        if 'posicao' not in kwargs:
            kwargs['posicao'] = ( random.randrange(0,40),random.randrange(0,40), 0 )
        super().__init__( *kwargs['posicao'] )
        self.nome = nome
        self.tipo = tipo
        self.__codigo = cd
     
    def  __str__(self):
        return "Identidade: Nome: {}; Tp {}; cd:{}; xy {}".format(
                self.nome,
                self.tipo,
                self.__codigo,
                self.posicao
             )

    @property
    def codigo(self):
        return self.__codigo
    

class cDestino( cIdentidade ) :

    def __init__(self, *args, **kwargs):
        
        super().__init__( *args, **kwargs)
        self.tempoInterTransito = kwargs.get('tempoInterTransito' , 0)
        self.penalidadeTransitoNivel = kwargs.get('penalidadeTransitoNivel' , 0)
        self.penalidadeTransitoExtra = kwargs.get('penalidadeTransitoExtra' , 0)
        self.posicaoGeo = kwargs.get('posicaoGeo' , 0)
        self.__Nnivel = kwargs.get('numNiveis' , None)

    def chegou(self, Trgt ):
        return self == Trgt and self.mesmoNivel(Trgt)

    @property
    def multiplosAndares(self):
        return self.__Nnivel is not None
        
    @property
    def niveis(self):
        return self.__Nnivel
    
    @niveis.setter
    def niveis(self, nivel):
        raise NotImplementedError
     
    def  __str__(self):
        return "{} :: Destino NNivel {}, Nivel {} \n".format(
                            super().__str__(),
                            self.__Nnivel,
                            self.nivel
                        )


class cPessoa( cIdentidade ):

    def __init__( self, pid, nome, dfltCasa , dfltDest ,**kwargs ):
        super().__init__( nome , eTIPOS.PESSOA , pid , posicao=dfltCasa.posicao , **kwargs )
        self.predioCasa = dfltCasa
        self.predioDestino = dfltDest
        self.emTransito = False
        self.meuDestino = dfltCasa   # Um destino 
        self.pxDtny = []         # Minha agenda ...  
        logging.debug("Iniciando pessoa {}".format(nome))
        self.ipxGenDstny = self.pxGenDstny()

    def pxGenDstny(self):
        while True:
            logging.log(25, "GenDestny, {}".format(str(self)))
            if self == self.predioCasa:
                # veja quanto tempo dorme, e produz nova agenda.
                #
                logging.log(22, "Estou em casa !!!")
                pass
            try:
                # se estiver no mesmo nivel, ., entao esta no mesmo destino,
                # senao tem que ir para a para o saguao .,
                X0 = self.peekPxDsty()
                logging.debug("Verificando proximo destino {}".format(X0))
                if self != X0 and not self.nivel != 0:
                    # Vair para o saguao .,
                    # o destino que preciso ... esta no nivel 0 ,
                    # nivel = 0                    
                    X = X0.saguao()
                    logging.debug("Nao estamos no mesmo Predio.. so entra ou sai pelo saguao!!!" )
                else:
                    X = self.pxDtny.pop(0)
                    logging.debug("retirei o X da fila")
                logging.info("Indo para {}".format(X))
                yield X
            except IndexError:
                # Acabou a agenda. .. voltarpara casa
                logging.info("Voltando para casa")
                yield self.predioCasa

    def peekPxDsty(self):
        try:
            logging.log(25,"peekPxDsty: {}".format(self.pxDtny[0]) )
            return self.pxDtny[0]
        except IndexError:
            logging.log(25,"peekPxDsty IndexError, voltando pra casa" )
            return self.predioCasa
            # raise IndexError

    def proximoDestino(self):
        #
        logging.info("Calculando proximo destino: {}".format(self.peekPxDsty()) )
        if self == self.peekPxDsty() or self.meuDestino.nivel == 0:
            # estamos no mesmo predio, apenas mudamos de andar.,
            # ou ja estamos no saguao .,. podemos ir a qualquer lugar
            logging.info("Gerando novo Destino ==> {}".format( self.pxDtny[0] ) )
            return next(self.ipxGenDstny)
        else:
            logging.info("Saindo para o saguao : {}".format(self.meuDestino) )
            self.meuDestino.nivel = 0 
            # vai para o terreo/saguao
            return self.meuDestino
            
    
    def vouSair( self ):
        logging.info("{} Vou sair para {}".format(self, self.meuDestino ) )
        self.lugar.sair(self)

    def programaSaida(self, lugar):
        # Entrei em algum lugar,
        # preparo a saida em tempo futuro .,
        #
        self.lugar = lugar
        # Tempo que fico aqui.,
        if self.nivel == 0:
            logging.info("Cheguei no saguao, proximo destino...  " )
            self.meuDestino = self.proximoDestino()
            self.vouSair()
        else:
            TTrabalho = random.randrange( TMINTRABALHO, TMAXTRABALHO )
            logging.info("{} Cheguei onde queria, fico aqui por {} tempo".format(self,TTrabalho) )
            self.meuDestino = self.proximoDestino()
            self.tMovimento = threading.Timer( TTrabalho , self.vouSair ).start()        

    @property
    def p_id(self):
        return self.codigo

    def agenda(self, destinos ):
        self.pxDtny = [ *destinos ]
        self.meuDestino = self.proximoDestino()
        logging.info("prox Destino da agenda: {}".format(self.meuDestino) )
        #

        self.meuDestino.entra(self)
        # 
    

    def  __str__(self):
        return " cPessoa :: {} >> {}\n".format( self.nome,super().__str__() )

class cEstadoElevador(Enum): 
        PARADO = 0,
        SAINDOENTRANDO = 1,
        SUBINDO = 2,
        DESCENDO = 3,
        MANUTENCAO = 4,
        CONGELADO = 5,
        TESTE = 6,
        SERVICO = 7,
        VAZIO = 8,
        BOMBEIRO = 99

    
class cElevador():
    # Fila neste Elevador.
    # transicao,direcao --> Estado atual, Proximo estado
    #
    # PROXIMADIRECAO = se DIRECAO = SUBINDO e NIVEL < NIVELMAXIMO ==> SUBINDO else DESCENDO
    #                  else NIVEL > NIVELMINIMO ==> DESCENDO else SUBINDO
    # 
    # TEMPODEMOVIMENTAR_EVENTO , DIRECAO
    #   se PARADO e DIRECAO-ANTERIOR entao DIRECAO <= PROXIMADIRECAO
    #   se (SUBINDO ou DESCENDO) e (ANDARSELECIONADO ou ANDARCHAMANDO) e MESMADIRECAO  entao SAINDOENTRANDO
    #   se SAINDOENTRANDO e FILAENTRANDO = 0 E FILASAINDO = 0 entao DIRECAO <= PROXIMADIRECAO
    #   se FILASAINDO = 0 e ANDARCHAMANDO = 0 entao ESTADO = PARADO
    #
    #
    #
    def __init__(self,  numero, predio,*args ,capElev=CAPACIDADE_ELEVADOR,**kwargs):
        # super().__init__( *args,**kwargs)
        self.dirAnterior = self.PARADO
        self.estado = self.PARADO
        self.nivel = 0
        self.predio = predio
        self.numeroDoElevador = numero
        # pessoas neste elevador
        self.filaNoElevador = [ Queue(maxsize=capElev) for N in range(0,self.predio.niveis) ]
        #cBotao
        self.noPainelIndicador = listEx( BOTAO() for B in range( 0, self.predio.niveis ) )
        #
        self._thr = threading.Thread( target=self.run, daemon=True )
        self._thr.start()

    def run(self):
        while True:
            logging.debug("cElevador .. run  .. ")
            time.sleep( TMOVIMENTOELEVADOR )
            self.movimento()

    def descarrega(self):
        # Se houverem pessoas para esse andar, .
        while( True ):
            logging.debug("Descarregando")
            try:
                self.noPainelIndicador[self.nivel].desativar()
                #  **** TODO ****
                #  Tratar a fila dentro do elevador , por andar.,
                #
                P = self.filaNoElevador[self.nivel].get(block=False) 
                self.predio.andares[self.nivel].entra( P )
                logging.info("Entrou {} no andar {}".format(P,self.nivel) )
            except Full:
                logging.error("Andar {} esta lotado, incapaz de deixar gente",self.nivel)
                # Devolve o sujeito para o elevador.,
                self.filaNoElevador[self.nivel].put_nowait(P)
                break
            except Empty:
                # Acabaram-se os individuos a sair
                logging.error("Elevador descarregou todos deste andar")
                break

    def carrega(self):
        # Se houverem pessoas para sair desse andar, .
        while( True ):
            logging.debug("Carregando")
            try:                
                P = self.predio.andares[self.nivel].filaSaindo.get(block=False)
                self.filaNoElevador[P.meuDestino.nivel].put( P, block=False )
                self.noPainelIndicador[P.meuDestino.nivel].ativar()
                logging.debug("Entrou {} no elevador {} no andar {} para andar {}".format(P,self.numeroDoElevador,self.nivel,P.meuDestino) )
            except Full:
                logging.error("Elevador {} no andar {} esta lotado, incapaz de carregar mais gente",self.numeroDoElevador, self.nivel)
                # Devolve o sujeito para o andar. nao tem como entrar no elevador.,
                self.predio.andares[self.nivel].filaSaindo.put_nowait(P)
                break
            except Empty:
                # Acabaram-se os individuos do andar
                logging.error("Nao tem mais gente para movimentar")
                break
        if self.predio.andares[self.nivel].filaSaindo.empty():
           self.predio.andares[self.nivel].chamar(False)
       
    def PARADO(self):
        # Carrega pessoas da fila desse nivel
        if self.noPainelIndicador.algumChamando() or self.predio.andares.algumChamando():
            self.dirAnterior = self.PARADO
            self.estado = self.SAINDOENTRANDO

    def SUBINDO(self):
        # Altera o nivel no evento
        self.nivel = self.nivel + 1
        if self.nivel < len(self.noPainelIndicador):
            # e verifica se precisa alterar o estado
            if self.noPainelIndicador[self.nivel].ligado or self.predio.andares[self.nivel].ligado:
                   self.dirAnterior = self.SUBINDO
                   self.estado = self.SAINDOENTRANDO
        elif self.nivel >= self.predio.niveis:
            self.estado = self.DESCENDO
        
    def DESCENDO(self):
        # Altera no nivel no evento .,
        # e verifica se precisa alterar o estado
        self.nivel = self.nivel - 1
        if self.nivel < 0 :
            self.nivel = 0
        # e verifica se precisa alterar o estado
        if self.noPainelIndicador[self.nivel].ligado or self.predio.andares[self.nivel].ligado:
               self.dirAnterior = self.DESCENDO
               self.estado = self.SAINDOENTRANDO
        elif self.nivel <= 0:
                self.estado = self.SAINDOENTRANDO
        
    def SAINDOENTRANDO(self):
        # Descarrega pessoas desse elevador nesse nivel,
        # e carrega pessoas da fila desse nivel ate o limite do elevador
        self.descarrega()
        self.carrega()
        self.estado = self.subiroudescer()

    def subiroudescer(self):
        # Verifica a proxima direcao deste elevador.,
        # Se estava parado no 0 --> subir
        # No topo --> descer
        # Em qualqer outro lugar, verifica qual o maior numero de pessoas para o destino,
        # e comeca por la.,
        # e se nao tiver ninguem., fica para
        #
        X = self.dirAnterior
        if self.nivel == 0:
            if self.predio.andares.algumChamando() or self.noPainelIndicador.algumChamando():
                X = self.SUBINDO
            else:
                X = self.PARADO
        elif self.estado == self.PARADO:
            # Verifica se precisamos ir a algum lugar
            cnt = 0
            for N in self.filaNoElevador:
                if N.qsize() > cnt:
                    cnt = N.qsize()
       
            if cnt == 0:
                # Ninguem no elevador
                X = self.PARADO
            elif cnt > self.nivel:
                # mais gente para subir
                X = self.SUBINDO
            else:
                X = self.DESCENDO
            logging.info("Dentro do elevador : {}".format(cnt) )

        return X
    
    def movimento(self):
        # Executa este FSM
        logging.info("Executando movimento {}".format(self) )        
        self.estado()

    def estado(self):
        f = [ x.qsize() for x in self.filaNoElevador ]
        tt = 0
        tt = tt + [ Q for Q in f ]
        return {
             "totalpsg" : tt,
             "passageiros": f,
             "seletores": [ R for R in range( len( self.noPainelIndicador ) ) if self.noPainelIndicador[R].ligado() ],
             "status": self.estado.__name__,
             "andar" : self.nivel
             }
        
        
      
    def  __str__(self):
        return 'cElevador Num {} : Ocupantes {}\n\tPainelIndicador {}\n\tEstado: {}\n\tNivel {}\n\tPredio :{}\n '.format(
                self.numeroDoElevador,
                [ x.qsize() for x in self.filaNoElevador ],
                [ "A{} : {}".format(R, self.noPainelIndicador[R] ) for R in range( len( self.noPainelIndicador ) ) ],
                self.estado.__name__,
                self.nivel,
                self.predio.nome
                )


class cAndar(cDestino):
    
    def __init__( self, numero, predio , *args, **kwargs ):
        self.predio = predio
        if "posicao" not in kwargs:
            (xW,yW,zW) = self.predio.posicao
        else:
            (xW,yW,zW) = kwargs["posicao"]
        kwargs["posicao"] = (xW,yW,numero)
        super().__init__( "E{}".format(numero),
                          eTIPOS.ELEVADOR ,
                          "E{}".format(numero),
                           **kwargs
                        )
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        logging.debug("Andar sendo criado")
        self._lock = threading.Lock()
        self.subir = BOTAO()
        self.descer = BOTAO()

        self.filaEntrando = Queue()
        #cPessoa
        self.filaSaindo = Queue()
        #cPessoa
        self.noAndarOcupado =  {}
        self._thr = threading.Thread(target=self.run, daemon=True  )
        self._thr.start()

    def saguao(self):
        return self.predio

    def estado(self):
        return {
             "totalSaindo" : self.filaSaindo .qsize(),
             "totalTrabalhando" : len(self.noAndarOcupado)
             }


    ##    def __eq__(self, other):
    ##        return self.__codigo == other.__codigo
    ##            # estamos na mesma identidade,        
    ##
    ##    def __ne__(self, other):        
    ##        return self.__codigo == other.__codigo
    ##        
        

    def entra(self,P):
        if  P.meuDestino == self:
            logging.info("{} Entrando no nivel destino {}".format(P, self.nivel) )
            self.filaEntrando.put( P )
        else:
            logging.info("{} Aguardando saida para destino {}".format(P, P.meuDestino,self.filaSaindo.qsize() ) )
            self.filaSaindo.put( P )
            if P.meuDestino > self.nivel:
                self.subir.ativar()
            else:
                self.descer.ativar()
        logging.info("{} Entrando no andar {} para nivel {} , FIn {} ; FOut {}; UP{} , DW{}".format(
                P.nome,
                self.nivel,
                P.meuDestino.nivel,
                self.filaEntrando.qsize(),
                self.filaSaindo.qsize(),
                self.subir.ligado,
                self.descer.ligado
                )
            ) 
        
    def chamar(self,T):
        self.subir.desativar()
        self.descer.desativar()

    @property
    def ligado(self):
        return self.subir.ligado or self.descer.ligado

    def run(self):
        while True:
            logging.debug("cAndar .. run  .. ")
            time.sleep( TMOVIMENTOENTRAANDAR )
            self.movimento()

    def sair(self,P):
        logging.info("indo para o elevador")
        with self._lock:
            P = self.noAndarOcupado.pop(P.p_id)
        self.filaSaindo.put(P)
        if P.meuDestino.nivel > self.nivel:
            logging.log(25,"Ativando Subir")
            self.subir.ativar()
        else:
            logging.log(25, "Ativando Descer")
            self.descer.ativar()
            
    def movimento(self):
        # Pega as pessoas que entraram , e da o que fazer,
        # Cada pessoa faz o que quer de acordo com o proprio tempo,
        # passa a funcao de saida para a pessoa poder ir embora
        # quando quiser.,
        #
        logging.log(15,"Movimento no Andar {} , Ocp {}, qIn {}, qOut {}, UP {}, DW {}".format(
                self.nivel,
                len(self.noAndarOcupado),
                self.filaEntrando.qsize(),
                self.filaSaindo.qsize(),
                self.subir.ligado,
                self.descer.ligado
            ) )
        try:
            P = self.filaEntrando.get(block=False)
            # Trata a entrada no predio.,
            P.cheguei(*self.posicao)
            logging.log(20,"Verificando se cheguei onde queria ?? nivel {} == nivel {}".format(
                    P.meuDestino.nivel,
                    self.nivel )
                )
            if P.meuDestino.nivel == self.nivel:
                # se for destino == 0 e nao tenho mais nada para fazer aqui., ... é pra sair.,
                #if P.meuDestino == 0 :
                #   # **** TODO **** ...
                #   P.
                #   #  Trocar de predio ...
                #   pass
                # cheguei onde queria.,
                logging.log(22,"Cheguei onde queria :: nivel {}".format(self.nivel))
                with self._lock:
                    self.noAndarOcupado[P.p_id] = P
                    logging.log(18,"Estou ocupado ")
                # vou embora daqui a pouco .,
                logging.log(20,"Preparando a agenda para o proximo ")
                P.programaSaida( self )
                
        except Empty:
            #
            logging.log(25,"Ninguem entrando")
        except Exception as e :
            logging.log(25,"Todo mundo ocupado aqui {}".format(e) )
      
class cPredio( cDestino ):
 
    def __init__( self, *args, **kwargs):
        nElevadores = kwargs.get('nElevadores',1)
        (nome, tipo, cd, nAndares ) = args
        # Niveis::  Saguao + andares.
        self.nAndares = nAndares
        super().__init__( nome, tipo, cd, numNiveis=nAndares+1, **kwargs )
        self.aguardaElevador = []
        self._lock = threading.Lock()
        # inicializa o predio com seus andares,
        #
        self.elevadores =  listEx( [ cElevador( N , self ) for N in range(nElevadores) ] )
        self.andares    = listEx( cAndar(A, self ) for A in range( self.niveis )  )

        logging.debug( "{} Elevadores >> \n".format( super().__str__() ) )
        for C in self.elevadores:
            logging.debug( C )

    def estado(self):
        # inventario no predio
        #
        dAnd = { "andares" : {} }
        for I in self.andares:
            dAnd['andares'][I.nivel] = I.estado()
        dElv = { "elevadores": {} }
        for I in self.elevadores:
            dElv['elevadores'][I.numeroDoElevador] = I.estado()

        P = { str(self.codigo) : { **dAnd, **dElv, 'predio' : {'tipo' : str(self.tipo) , 'nome' : self.nome } } }
        
        return( P )
            
    @property
    def maxAndares(self):
        return self.nAndares
    
    def entra(self,P):
            logging.info("predio {} Entrando {} para nivel {}".format(self, P,P.meuDestino) ) 
            self.andares[0].entra( P )
            #


class cBairro(cDestino):

    def __init__(self, cdCidade ):
        (cdBairro, nomeBairro) = Nomes.NovoBairro()
        super().__init__( nomeBairro,
                          eTIPOS.BAIRRO,
                          cdBairro,
                          numNiveis = 1,
                          posicao = cPosicaoXYZ()
                           )
        # 
        self.cdCidade=cdCidade  
        self.Predios = []
        

    def novoPredio(self, andares = 6):
        elev = (andares % 4) + 2
        self.Predios.append( cPredio( Nomes.Predio(),
                                      eTIPOS.PREDIO ,
                                      random.randrange(5347587),
                                      andares,
                                      cdBairro = self.codigo,
                                      cdCidade = self.cdCidade
                                      )
                             )
    
    def incluiPredio(self, predio):
        
        self.Predios.append(predio )
        

# class cCidade(cDestino):
    


class MundoVirtual():

    def __init__(self, cidades, bairros, predios, pessoas ):
        self.cidades = cidades
        self.bairros = bairros
        self.predios = predios
        self.pessoas = pessoas

    @classmethod
    def criaPessoas(self,  nPessoas = 1 ):
        pessoas = []
        for X in range(1,nPessoas ):
            pid,N = Cadastros.Pessoa()
            pessoas.append( cPessoa( pid,
                                 N,
                                 cDestino("casa",eTIPOS.CASA) ,
                                 cDestino("casa",eTIPOS.CASA)
                                )
                        )
        return pessoas


    def movePessoasAleatorio(self, nPessoas ):
        pass
    

    @classmethod
    def criaCidades(self, nCidades = 1 , rnd = True ):
        R = random.randrange( 1, nCidades ) if rnd else nCidades
        cidades = [ Nomes.NovaCidade() for N in range(R) ]
        return cidades

    @classmethod        
    def criaBairros(self, cdCidade, nBairros = 10, rnd = True ):
        R = random.randrange( 1, nBairros ) if rnd else nBairros
        bairros = [  cBairro(cdCidade) for N in range( R )  ]
        return bairros

    @classmethod
    def criaPredios(self, cdCidade, cdBairro, nPredios = 10, rnd = True ):
        R = [ random.randrange( 1, nPredios ) if rnd else nPredios ]
        predios = [ cPredio( "Predio {}".format(px) , eTIPOS.PREDIO , int(random.random() * 10) ) ]
          
        return predios
        
        


    


def testeMundoVirtual():

    NBAIRROSX = 3
    NCIDADES = 1

    # logging.info("Cidade {} :: {}".format(cdCidade,nmCidade) )
    #

    mV = MundoVirtual( MundoVirtual.criaCidades,
                       MundoVirtual.criaBairros,
                       MundoVirtual.criaPredios, 
                       MundoVirtual.criaPessoas )
    

class cP(cDestino):
    def __init__(self,nome,tipo,cd,*args,nivel=0,**kwargs):
        super().__init__(nome,tipo,cd,**kwargs)
        self.__nivel = nivel

    @property
    def nivel(self):
        return self.__nivel

    @nivel.setter
    def nivel(self, nivelx):
        self.__nivel = nivelx

def testeDestino():
    xT0 = cP( "x0", 0, 0  )
    xT2 = copy.deepcopy(xT0)
    xT2.nivel = 22
    xT1 = cP( "x1", 0, 0 ,23 )

    print( xT0.nivel )
    xT0.nivel = 23
    xT2.nivel = 23
    print( xT0.nivel )
    print( xT0.chegou( xT1 ) )
    print( xT0.chegou( xT2 ) )
    
    

def testeElevador():
    
    #
    cp = cPredio( Nomes.Predio() ,
              eTIPOS.PREDIO ,
              random.randrange(2355327),    # Cd Predio . 
              8,
              nElevadores = 2 
              )
    print( json.dumps( cp.estado() ) )
    # cp.niveis= [cAndar(0), cAndar(1)]
    # cp.elevadores = [ cElevador( 1 , cp ) ]
    pid,N = Cadastros.Pessoa()
    s =  cPessoa( pid, N ,  cDestino("casa",eTIPOS.CASA) , cDestino("casa",eTIPOS.CASA), cdCidade=0 )
    # Entra sempre no nivel 0.,
    # sai pelo nivel 0
    #
    # pxDtny
    # entrar em um predio, .. para um andar.,
    #
    s.agenda( [ cp.andares[ random.randrange(1,cp.maxAndares) ] for N in range(4) ] )
    
    time.sleep(10)


if __name__ == "__main__":    
    format = "%(thread)d  %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")

    xuD = uD.udpDiscover( beacon=True , port=9093, ttl=5, bId='UUIDXXX' ) # rcvCallBack = callBackTeste )
    
    # testeDestino()
    testeElevador()
    # testeMundoVirtual()
    # time.sleep(20)
    
