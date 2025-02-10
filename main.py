from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.server import WebServer
from controladorTeste import *


if __name__ == "__main__":
    RouteHandler.add_route("/","pages/index.html")
    RouteHandler.add_route("/about","pages/about.html")
    RouteHandler.add_route("/data","data/info.json")
    RouteHandler.add_route("/data","data/info.json")
    #Funcionando
    RouteHandler.add_route("/clientes",json_response=clientes())
    # Precisa implementar alguma forma de passar o id para o controlador// Não está funcionando
    RouteHandler.add_route("/clientes/{id}", json_response=clientes())
    WebServer.start(port=9090)