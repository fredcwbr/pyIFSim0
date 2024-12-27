

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

        self.nxtProps()


    @classmethod
    def xPessoa(self):
        while(1):        
            yield self.PN[random.randrange(0,len(self.PN))].strip()+" "+self.SN[random.randrange(0,len(self.SN))].strip()

    @classmethod
    def Pessoa(cls):
        return next(cls.iPessoa)

    @classmethod
    def xPrenome(self):
        while(1):        
            yield self.PN[random.randrange(0,len(self.PN))].strip()

    @classmethod
    def Prenome(self):
        return next(self.iPrenome)
            
    @classmethod
    def xSobrenome(self):
        while(1):
            yield self.SN[random.randrange(0,len(self.SN))].strip()

    @classmethod
    def Sobrenome(self):
        return next(self.iSobrenome)
    
    @classmethod
    def xCidades(self):
        while(1):
            cd = random.randrange(0,len(self.CDs))
            yield (cd, self.CDs[cd].strip() )
            
    @classmethod
    def NovaCidade(self):
        return next(self.iCidades)

    @classmethod
    def xGetNovoCdCidades(self):
        while(1):
            yield random.randrange(0,len(self.CDs))

    @property
    def NomeCidade(self,cdCidade):
        return self.__class__.CDs[cdCidade]


    @classmethod
    def xBairros(self):
        while(1):
            cd = random.randrange(0,len(self.BRs))
            yield (cd, self.BRs[cd].strip() )

    @classmethod
    def Bairros(self):
        return next(self.iBairros)

    @classmethod
    def NovoBairro(self):
        return self.Bairros()

    @classmethod
    def xgetNovoCdBairro(self):
        while(1):
            yield random.randrange(0,len(self.BRs))

    @classmethod
    def getNovoCdBairro(self):
        return next(self.igetNovoCdBairro())

    @property
    def NomeBairro(self,cdBR):
        return self.__class__.BRs[cdBR]





    @classmethod
    def nxtProps(cls):
        cls.iPessoa = cls.xPessoa()
        cls.iPrenome = cls.xPrenome()
        cls.iSobrenome = cls.xSobrenome()
        cls.iCidades = cls.xCidades()
        cls.iBairros = cls.xBairros()
        cls.igetNovoCdBairro = cls.xgetNovoCdBairro()
   


