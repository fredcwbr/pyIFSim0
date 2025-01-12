import queue
from queue import Empty as qEmpty
import threading
from threading import Thread
from time import sleep
import ifaddr
import ipaddress
import io
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, AI_NUMERICHOST,AI_PASSIVE, gethostbyname, gethostname
import json

interfacesMaquina = ifaddr.get_adapters()
ips = []
for A in interfacesMaquina:
    for ip in A.ips:
        if ip.is_IPv4:
            ipx  = ipaddress.IPv4Interface( ( ip.ip, ip.network_prefix) ) 
            ips.append( ipx )


class udpDiscover:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        cx = super().__new__(cls,*args, **kwargs)
        if cx._instance is None:
           cx._instance = True
           cx.interfacesMaquina = interfacesMaquina
           cx.ips = ips
           cnxS = [] 
           for I  in cx.ips:
                # B = I.network.broadcast_address
                print( I , format(I),  format(I.ip), I.network.broadcast_address )
                s = socket(AF_INET, SOCK_DGRAM) # create UDP socket
                s.bind((str(I.ip) , 0))
                s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
                cnxS.append((s,I))
           cx.skts = cnxS           
        return cx

    def __init__(self, *args, **kwargs):
        self.cntSeq = 1
        self.sndContinua = True
        self.rcvContinua = True
        self.rcvCallBack = None

    def sender( self, port, MSG ):
        # MSG é um dict que sera enviado como JSON  .,
        # Adiciona sequencia 
        MSG['seq'] = self.cntSeq
        self.cntSeq = self.cntSeq + 1
        for s,ip in self.skts:
            # print( ip.network.broadcast_address )
            #s.sendto(data.encode('utf-8'), ('<broadcast>', PORT))
            s.sendto(json.dumps(MSG).encode('utf-8'), (format(ip.network.broadcast_address), PORT))
        print( "sent service announcement \n"  )
        

    def receiver( self, port ):
        s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
        s.bind(('', port ))

        while self.rcvContinua:
            data, addr = s.recvfrom(4096)
            # *** CHAMA O CALL BACK ***
            if self.rcvCallBack is not None:
                self.rcvCallBack(data,addr )
            else:
                print(  "got service announcement from: {}\n".format(addr), data.decode('utf-8') )

 
    def rcvStart( self , PORT ):
        tr = threading.Thread(
            target=self.receiver,
            args=( PORT , ),
            daemon=True
        )
        tr.start()

    def testeSnd(self):
        while self.sndContinua :
            self.sender( PORT , {'Id': "Msg Teste" } )
            sleep(5)

        
    def sendStart( self, PORT ):
        ts = threading.Thread(
            target=self.testeSnd,
            args=(),
            daemon=True
        )
        ts.start()

    def rcv_stop(self):
        self.receiver.continua = False
        
    def snd_stop(self):
        self.sender.continua = False



def callBackTeste( dados, origem ):

    d = json.loads( dados.decode('utf-8') )
    print( " Callback :: " , d, origem )


if __name__ == '__main__':


    PORT = 9093

    uS = udpDiscover()

        
    uS.rcvStart( PORT )
    uS.rcvCallBack = callBackTeste
    uS.sendStart( PORT )
   
    sleep(15)
    print( "Terminando ..." ) 
    uS.rcvContinua.stop()
    uS.sndContinua = False



