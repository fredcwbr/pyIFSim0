import queue
from queue import Empty as qEmpty
import threading
from threading import Thread
from time import sleep
import ifaddr
import ipaddress
import io
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, AI_NUMERICHOST,AI_PASSIVE, gethostbyname, gethostname

MAGIC = "bla bla bla "
PORT = 9093
placas = ifaddr.get_adapters()

R = []
with io.StringIO() as S:
    for A in placas:
        print("Placa " + A.nice_name, file=S)
        for ip in A.ips:
            print("   %s/%s :: %s\n" % (ip.ip, ip.network_prefix, 'v4' if ip.is_IPv4 else 'v6'), file=S)
            if ip.is_IPv4:
                ipx  = ipaddress.IPv4Interface( ( ip.ip, ip.network_prefix) ) 
                R.append( ipx )
            #else:
            #    R = ipaddress.IPv6Interface( ( ip.ip, ip.network_prefix) )
    MSG = S.getvalue()


def cnxoes( ):
    cx = [] 
    for I  in R:
        # B = I.network.broadcast_address
        print( I , format(I),  format(I.ip) )
        s = socket(AF_INET, SOCK_DGRAM) # create UDP socket
        s.bind((str(I.ip) , 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
        cx.append(s)
    return cx
    

def sender( port ):
    cntSeq = 1
    continua = True
    skts = cnxoes()
    # Be careful if you have multiple network interfaces or IPs

    while continua:
        data = MAGIC+ ' seq : {} \n'.format(cntSeq) + MSG
        cntSeq = cntSeq + 1
        for s in skts:
            s.sendto(data.encode('utf-8'), ('<broadcast>', PORT))
        print( "sent service announcement {}\n".format(R)  )
        sleep(5)


def receiver( port ):
    continua = True
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', port ))

    while continua:
        data, addr = s.recvfrom(1024) #wait for a packet
        if data.startswith(MAGIC.encode('utf-8')):
            print(  "got service announcement from: {}\n".format(addr), data[len(MAGIC):].decode('utf-8') )


if __name__ == '__main__':
    #for I in [ 1 ]:
    tr = threading.Thread(
        target=receiver,
        args=( PORT , ),
        daemon=True
    )
    tr.start()

    ts = threading.Thread(
        target=sender,
        args=( PORT , ),
        daemon=True
    )
    ts.start()
        
    sleep(15)
    print( "Terminando ..." ) 
    receiver.continua  = False
    sender.continua  = False

