
from enum import Enum

class BOTAO(Enum):
    DESLIGADO,
    LIGADO


class cPosicao:
    self.cidade
    self.bairro
    self.x
    self.y

    def __init__( self, x = 0 , y = 0 ):
        self.x = x
        self.y = y
        
    def distancia(self, x,y):
        # Retorna a distancia polar equivalente entre os pontos A,B 
        return sqr( (self.x - x)**2 + (self.y - y)**2 )

class cDestino( cPosicao ) :
    self.nivel
    self.tempoInterTransito
    self.penalidadeTransitoNivel
    self.penalidadeTransitoBairro
    self.penalidadeTransitoCidade
    self.posicaoGeo  


class cPessoa( cPosicao ):
    self.predioCasa
    self.predioDestino
    self.emTtransito
    




class cAndar:
    self.subir
    self.descer

    #cPessoa
    self.noAndarParaSair = []
    #cPessoa
    self.noAndarOcupado = []
    
    def __init__( self, numero ):
        # define um andar do predio
        # andar pode conter pessoas
        # e tem os botoes de sinalizacao dos elevadores
        #
        self.subir = cBotao(BOTAO.DESLIGADO)
        self.descer = cBotao(BOTAO.DESLIGADO)



class cPredio( cDestino ):
    self.niveis

    def __init__( self, andares ):
        # inicializa o predio com seus andares,
        #
        self.niveis = cAndares( andares )
        
