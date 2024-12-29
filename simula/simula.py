

import concurrent.futures
import logging
import queue
import random
import threading
from queue import Queue, Full, Empty
import time

from enum import Enum

from  nomesX import Nomes

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
    CIDADE = 0,
    BAIRRO = 1,
    PREDIO = 2,
    ANDAR  = 3,
    PRACA  = 4,
    RUA    = 5,
    PESSOA = 6,
    CASA   = 7,
    REMOTO = 999

class eDIRECAO(Enum):
    PARADO = 0,
    SUBIR = 1,
    DESCER = 2

    __strsX__ = ["PARADO", "SUBIR", "DESCER" ]
    
    def  __str__(self):
        return __strsX__[self] 

class cPosicaoXY:
    def __init__(self, *args):
        if len(args) < 2 :
            self.xlen = random.randrange(0,10)
            self.ylen = random.randrange(0,10)
        else:
            (xlen, ylen) = args
            self.xlen = xlen
            self.ylen = ylen

    @property        
    def get(self):
        return (self.xlen, self.ylen)
        
    def distancia(self, x,y):
        # Retorna a distancia polar equivalente entre os pontos A,B 
        return sqr( (self.xlen - x)**2 + (self.ylen - y)**2 )

    def __str__(self):
        return '{} : {}'.format(self.xlen, self.ylen)
    


class eBOTAO(Enum):
    DESLIGADO = 0,
    LIGADO = 1

    def  __str__(self):
        if self == eBOTAO.LIGADO:
            return "LIGADO"
        else:
            return "DESLIGADO" 
    

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
        return "estado: {} ".format( str(self.__estado__) )


 

class cIdentidade(cPosicaoXY):
    
    def __init__( self, nome, tipo, posicao=0, cdCidade = 0, cdBairro = 0 , nivel = 0 ):
        if posicao is type(None):
            posicao = ( random.randrange(0,40),random.randrange(0,40) )
        super().__init__( posicao )
        self.nome = nome
        self.tipo = tipo
        self.cdCidade = cdCidade
        self.cdBairro = cdBairro
        self.nivel = nivel
     
    def  __str__(self):
        return "Identidade: cdCidade : {}; cdBairro {}; xy {} , nv {}".format(
                self.cdCidade,
                self.cdBairro,
                self.get,
                self.nivel
             )

    def getCdCidade(self):
        return self.cdCidade

    def getCdBairro(self):
        return self.cdBairro
    
    def getNivel(self):
        return self.nivel
     


class cDestino( cIdentidade ) :

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tempoInterTransito = 0
        self.penalidadeTransitoNivel = 0
        self.penalidadeTransitoExtraBairro = 0
        self.penalidadeTransitoIntraBairro = 0
        self.penalidadeTransitoCidade = 0
        self.posicaoGeo   = 0

    def chegou(self, Trgt ):
        return  self.cdCidade == Trgt.cdCidade and
                self.cdBairro == Trgt.cdBairro and
                self.cdPredio == Trgt.cdPredio and
                self.nivel    == Trgt.nivel

    def  __str__(self):
        return "{} :: {}\n".format( self.nome, super().__str__()  )


class cPessoa( cIdentidade ):

    def __init__( self, pid, nome, dfltCasa , dfltDest ,**kwargs ):
        super().__init__( nome , eTIPOS.PESSOA ,**kwargs )
        self.predioCasa = dfltCasa
        self.predioDestino = dfltDest
        self.emTransito = False
        self.p_id = pid
        self.meuDestino = 0
        logging.debug("Iniciando pessoa {}".format(nome))

    def vouSair( self ):
        self.meuDestino = proximoDestino()
        logging.info("{} Vou sair para {}".format(self, self.meuDestino ) )
        self.lugar.sair(self)

    def programaSaida(self, lugar):
        # Entrei em algum lugar,
        # preparo a saida em tempo futuro .,
        #
        self.lugar = lugar
        # Tempo que fico aqui.,
        TTrabalho = random.randrange( TMINTRABALHO, TMAXTRABALHO )
        logging.info("{} Cheguei onde queria, fico aqui por {} tempo".format(self,TTrabalho) )
        self.tMovimento = threading.Timer( TTrabalho , self.vouSair ).start()        

    @property
    def p_id(self):
        return self.__p_id

    @p_id.setter
    def p_id(self, val):
        self.__p_id = val

    def destino(self, predio, nivel):
        self.meuDestino = nivel
        predio.entra(self)
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
        # super().__init__(self,*args,**kwargs)
        self.dirAnterior = self.PARADO
        self.estado = self.PARADO
        self.nivel = 0
        self.predio = predio
        self.numeroDoElevador = numero
        # pessoas neste elevador
        self.filaNoElevador = [ Queue(maxsize=capElev) for N in range(0,len(self.predio.niveis)) ]
        #cBotao
        self.noPainelIndicador = [ BOTAO() for B in range(len(predio.niveis) ) ]
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
            logging.info("Descarregando")
            try:
                self.noPainelIndicador[self.nivel].desativar()
                #  **** TODO ****
                #  Tratar a fila dentro do elevador , por andar.,
                #
                P = self.filaNoElevador[self.nivel].get(block=False) 
                self.predio.niveis[self.nivel].entra( P )
                logging.info("Entrou {} no andar {}".format(P,self.nivel) )
            except Full:
                logging.info("Andar {} esta lotado, incapaz de deixar gente",self.nivel)
                # Devolve o sujeito para o elevador.,
                self.filaNoElevador[self.nivel].put_nowait(P)
                break
            except Empty:
                # Acabaram-se os individuos a sair
                logging.info("Elevador descarregou todos deste andar")
                break

    def carrega(self):
        # Se houverem pessoas para sair desse andar, .
        while( True ):
            logging.info("Carregando")
            try:                
                P = self.predio.niveis[self.nivel].filaSaindo.get(block=False)
                self.filaNoElevador[P.meuDestino].put( P, block=False )
                self.noPainelIndicador[P.meuDestino].ativar()
                logging.info("Entrou {} no elevador {} no andar {}".format(P,self.numeroDoElevador,self.nivel) )
            except Full:
                logging.info("Elevador {} no andar {} esta lotado, incapaz de carregar mais gente",self.numeroDoElevador, self.nivel)
                # Devolve o sujeito para o andar. nao tem como entrar no elevador.,
                self.predio.nivel[self.nivel].filaSaindo.put_nowait(P)
                break
            except Empty:
                # Acabaram-se os individuos do andar
                logging.info("Nao tem mais gente para movimentar")
                break
        if self.predio.niveis[self.nivel].filaSaindo.empty():
           self.predio.niveis[self.nivel].chamando = False 
       
    def PARADO(self):
        # Carrega pessoas da fila desse nivel
        if self.noPainelIndicador[self.nivel].ligado or self.predio.niveis[self.nivel].ligado:
               self.dirAnterior = self.PARADO
               self.estado = self.SAINDOENTRANDO

    def SUBINDO(self):
        # Altera o nivel no evento
        self.nivel = self.nivel + 1
        # e verifica se precisa alterar o estado
        if self.noPainelIndicador[self.nivel].ligado or self.predio.niveis[self.nivel].ligado:
               self.estado = self.SAINDOENTRANDO
        elif self.nivel < len(self.predio.niveis)-1:
            self.estado = self.DESCENDO
        
    def DESCENDO(self):
        # Altera no nivel no evento .,
        # e verifica se precisa alterar o estado 
        self.nivel = self.nivel - 1
        # e verifica se precisa alterar o estado
        if self.noPainelIndicador[self.nivel].ligado or self.predio.niveis[self.nivel].ligado:
               self.estado = self.SAINDOENTRANDO
        elif self.dirAnterior == self.DESCENDO:
            if self.nivel <= 0:
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
        if self.nivel == 0:
            X = self.SUBINDO
        elif self.nivel == len(self.predio.niveis)-1:
            X = self.DESCENDO
        else:
            cnt = 0
            for N in self.filaNoElevador:
                if N.qsize > cnt:
                    cnt = N.qsize
            if cnt == 0:
                # o elevador esta vazio
                X = self.PARADO
            elif cnt > self.nivel:
                # mais gente para subir
                X = self.SUBINDO
            else:
                X = self.DESCENDO
        return X
    
    def movimento(self):
        # Executa este FSM
        logging.info("Executando movimento {}".format(self) )
        self.estado()
      
    def  __str__(self):
        return 'cElevador Num {}\n\tPainelIndicador {}\n\tEstado: {}\n\tNivel {}\n\tPredio :{}\n '.format(
                self.numeroDoElevador,
                [ "A{} : {}".format(R, self.noPainelIndicador[R] ) for R in range(len(self.noPainelIndicador)) ],
                self.estado,
                self.nivel,
                self.predio.nome
                )


class cAndar():
    
    def __init__( self, numero , *args, **kwargs ):
        # super().__init__(self, *args, **kwargs )
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        logging.debug("Andar sendo criado")
        self._lock = threading.Lock()
        self.nivel = numero
        self.subir = BOTAO()
        self.descer = BOTAO()

        self.filaEntrando = Queue()
        #cPessoa
        self.filaSaindo = Queue()
        #cPessoa
        self.noAndarOcupado =  {}
        self._thr = threading.Thread(target=self.run, daemon=True  )
        self._thr.start()
        

    def entra(self,P):
        if  P.meuDestino == self.nivel:
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
                P,
                self.nivel,
                P.meuDestino,
                self.filaEntrando.qsize(),
                self.filaSaindo.qsize(),
                self.subir.ligado,
                self.descer.ligado
                )
            ) 
        

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
        if P.meuDestino > self.nivel:
            self.subir.ativar()
        else:
            self.descer.ativar()
            
    def movimento(self):
        # Pega as pessoas que entraram , e da o que fazer,
        # Cada pessoa faz o que quer de acordo com o proprio tempo,
        # passa a funcao de saida para a pessoa poder ir embora
        # quando quiser.,
        #
        logging.info("Movimento no Andar {} , Ocp {}, qIn {}, qOut {}, UP {}, DW {}".format(
                self.nivel,
                len(self.noAndarOcupado),
                self.filaEntrando.qsize(),
                self.filaSaindo.qsize(),
                self.subir.ligado,
                self.descer.ligado
            ) )
        try:
            P = self.filaEntrando.get(block=False)
            if P.meuDestino == self.nivel:
                # se for destino == 0 ... é pra sair.,
                if P.meuDestino == 0:
                   # **** TODO **** ...
                   #  Trocar de predio ...
                   pass
                # cheguei onde queria.,
                with self._lock:
                    self.noAndarOcupado[P.p_id] = P
                # vou embora daqui a pouco ., 
                P.programaSaida( self )
                
        except Empty:
            #
            logging.info("Ninguem entrando")
        # except :
        #    logging.info("Todo mundo ocupado aqui ")
            

class cPredio( cDestino ):
 
    def __init__( self, *args, nElevadores = 1 , Teste=False , **kwargs):
        (nome, tipo, andares) = args 
        super().__init__( nome, tipo, **kwargs )
        self.aguardaElevador = []
        self._lock = threading.Lock()
        # inicializa o predio com seus andares,
        #
        if not Teste:
            self.elevadores =  [ cElevador( N , self ) for N in range(nElevadores) ]
            self.niveis = [ cAndar(A, self.elevadores ) for A in range( andares ) ]

        # logging.info( "{} Elevadores >> \n".format( super().__str__() ) )
        #for C in self.elevadores:
        #    logging.info( C )

    def entra(self,P):
            logging.info("predio Entrando {} para nivel {}".format(P,P.meuDestino) ) 
            self.niveis[0].entra( P )        


class cBairro(cDestino):

    def __init__(self, cdCidade):
        (cdBairro, nomeBairro) = Nomes.NovoBairro()
        super().__init__( nomeBairro, eTIPOS.BAIRRO, cPosicaoXY(), cdCidade=cdCidade, cdBairro=cdBairro  )
        self.Predios = []
        

    def novoPredio(self, andares = 6):
        elev = (andares % 4) + 2
        self.Predios.append( cPredio( Nomes.Prenome() , eTIPOS.PREDIO , andares, cdCidade = 0, cdBairro = 0 , nivel = 0 , 
                                      nElevadores = elev) )
    
    def incluiPredio(self, predio):
        self.Predios.append(predio )
        

def testeMundoVirtual():
    
    pessoasX = []
    # Gera mundo virtual .,
    NBAIRROSX = 1
    (cdCidade, nmCidade) = Nomes.NovaCidade()
    logging.info("Cidade {} :: {}".format(cdCidade,nmCidade) )
    #
    bairros = [  cBairro(cdCidade) for N in range( NBAIRROSX )  ]
    for B in bairros:
        for P in [1]: # range ( random.randrange( 3, 10 ) ):
             B.novoPredio()
    
        for px in [1]: # range( 1, 20 ):
            pid,N = Cadastros.Pessoa()
            s =  cPessoa( pid,N , cDestino("casa",eTIPOS.CASA) , cDestino("casa",eTIPOS.CASA), cdCidade=cdCidade )
            pid,N = Cadastros.Pessoa()
            pessoasX.append( cPessoa(  pid,N, cDestino("casa",eTIPOS.CASA) , cDestino("casa",eTIPOS.CASA) , cdBairro=B.cdBairro, cdCidade=cdCidade )  )

        # logging.info( "Pessoas: {} :: {}".format( len(pessoasX) , [ str(P) for P in pessoasX ] ) )
                    
    
    #for px in range(1,10):
    #    bairros[random.randrange(0,len(bairros))].incluiPredio( cPredio( "Predio {}".format(px) , eTIPOS.PREDIO , int(random.random() * 10) ) ) 



def testeElevador():
    
    #
    cp = cPredio( Nomes.Prenome() ,
              eTIPOS.PREDIO ,
              1,
              cdCidade = 0,
              cdBairro = 0 ,
              nivel = 0 ,
              nElevadores = 1 ,
              Teste=True
              )
    cp.niveis= [cAndar(0), cAndar(1)]
    cp.elevadores = [ cElevador( 1 , cp ) ]
    pid,N = Cadastros.Pessoa()
    s =  cPessoa( pid,N , cDestino("casa",eTIPOS.CASA) , cDestino("casa",eTIPOS.CASA), cdCidade=0 )
    # Entra sempre no nivel 0.,
    # sai pelo nivel 0
    #
    s.destino( cp, len(cp.niveis) -1 )
    
    time.sleep(10)


if __name__ == "__main__":    
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")


    testeElevador()
    # time.sleep(20)
    
