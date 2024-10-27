



def nomesPessoas():
    with open("nomesPessoa.txt", "r") as xnome:
        for N in xnome.readlines():
            yield N.strip()

