from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse

class cidadeHdlr(BaseHTTPRequestHandler):

    def __init__( self, request, client_address, server ):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)
        self.cidade = server.cidade
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        #message_parts = [
        #':',
        #'client_address=%s (%s)' % (self.client_address,
        #                            self.address_string()),
        #'command=%s' % self.command,
        #'path=%s' % self.path,
        #'real path=%s' % parsed_path.path,
        #'query=%s' % parsed_path.query,
        #'request_version=%s' % self.request_version,
        #'',
        #'SERVER VALUES:',
        #'server_version=%s' % self.server_version,
        #'sys_version=%s' % self.sys_version,
        #'protocol_version=%s' % self.protocol_version,
        #'',
        #'HEADERS RECEIVED:',
        #]
        #for name, value in sorted(self.headers.items()):
        #    message_parts.append('%s=%s' % (name, value.rstrip()))

        # message = '\r\n'.join(message_parts)

        # trata mensagem , recebendo o HASH do PREDIO
        # e devolvendo o relatorio sobre a situacao atual dos elementos
        # do predio,
        #   * Quantas entraram
        #   * quantas no saguao,
        #   * quantas sairam
        #
        # no conjunto elevador,
        #   o status do elevador,
        #     * qual andar
        #     * quantas pessoas,
        #     * destinos selecionados
        # no conjunto de andares,.
        #  o status do andar,
        #     * Quantas pessoas trabalhando
        #     * Quantas esperando para subir
        #     * Quantas esperando para descer


        P = self.cidade.getPredio( 'qPredio' , None )
        if P is None:
            self.send_response(404)
            msg = ''
        else:
            self.send_response(200)
            # Result as JSON
            msg = P.statusJSON()
        self.end_headers()
        self.wfile.write(msg)
        return

    def listaPredios(self):
        for K,P in self.cidade.predios.items():
            pass
        pass
    
    def statusPredio(self,hashPredio):
        P = self.cidade.getPredio( 'qPredio' , None )
        if P is None:
            self.send_response(404)
            msg = ''
        else:
            self.send_response(200)
            # Result as JSON
            msg = P.statusJSON()
        pass



class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class serveStatus:
    def __init__(self, cidade, host='', port=9080):
        self.server = ThreadedHTTPServer((host, port), GetHandler , )
        self.server = startLocalServer.ThreadedHTTPServer((host,port), startLocalServer.cidadeHdlr)
        self.server.cidade = cidade
        server_thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        server_thread = start()
        


