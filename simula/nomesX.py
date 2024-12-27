

import random

class Nomes:
    PN = []
    SN = []
    CDs = []
    BRs = []

    def __init__(self):
        # Carrega os nomes
        with open("nomesPessoa.txt", "r") as xnome:
            self.__class__.PN = xnome.readlines()
        # Carrega os sobrenomes
        with open("sobreNomesPessoa.txt", "r") as xnome:
            self.__class__.SN = xnome.readlines()
        # Compoe nomes e sobrenomes aleatoriamente
        #
        with open("cidades.csv", "r") as xnome:
            self.__class__.CDs = xnome.readlines()
        #
        with open("bairros.csv", "r") as xnome:
            self.__class__.BRs = xnome.readlines()

    @classmethod
    def Pessoa(self):
        while(1):        
            yield self.PN[random.randrange(0,len(self.PN))].strip()+" "+self.SN[random.randrange(0,len(self.SN))].strip()

    @classmethod
    def prenome(self):
        while(1):        
            yield self.PN[random.randrange(0,len(self.PN))].strip()
            
    @classmethod
    def sobrenome(self):
        while(1):
            yield self.SN[random.randrange(0,len(self.SN))].strip()

    @classmethod
    def Cidades(self):
        while(1):
            cd = random.randrange(0,len(self.CDs))
            yield (cd, self.CDs[cd].strip() )
            
    @classmethod
    def novaCidade(self):
        return next(self.Cidades())

    @classmethod
    def getNovoCdCidades(self):
        while(1):
            yield random.randrange(0,len(self.CDs))

    @property
    def nomeCidade(self,cdCidade):
        return self.__class__.CDs[cdCidade]


    @classmethod
    def Bairros(self):
        while(1):
            cd = random.randrange(0,len(self.BRs))
            yield (cd, self.BRs[cd].strip() )

    @classmethod
    def novoBairro(self):
        return next(self.Bairros())

    @classmethod
    def getNovoCdBairro(self):
        while(1):
            yield random.randrange(0,len(self.BRs))

    @property
    def nomeBairro(self,cdBR):
        return self.__class__.BRs[cdBR]






