from http.server import HTTPServer
# from conn.handler import BaseHandler,RouteHandler
from arcforge.core.conn.handler import BaseHandler, RouteHandler


class WebServer:
    
    @staticmethod
    def start(port=9090):
        host = "localhost"
        server_address = (host, port)

        httpd = HTTPServer(server_address, RouteHandler)
        print(f" Servidor rodando em http://{host}:{port}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
            httpd.server_close()