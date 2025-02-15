from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.server import WebServer
from controladorTeste import *
from arcforge.core.conn.response import Response


if __name__ == "__main__":
    # RouteHandler.add_route("/","pages/index.html")
    # RouteHandler.add_route("/about","pages/about.html")
    # RouteHandler.add_route("/data","data/info.json")
    # RouteHandler.add_route("/data","data/info.json")
    # #Funcionando
    # RouteHandler.add_route("/clientes",json_response=clientes())
    # # Precisa implementar alguma forma de passar o id para o controlador// Não está funcionando
    # RouteHandler.add_route("/clientes/{id}", json_response=clientes())
    usuarios = [
    {"id": "1", "nome": "Alice", "email": "alice@example.com"},
    {"id": "2", "nome": "Bob", "email": "bob@example.com"},
    {"id": "3", "nome": "Carol", "email": "carol@example.com"}
]

    def handle_get_usuario(handler, id):
        usuario = next((u for u in usuarios if u["id"] == id), None)
        res = Response(status=200,data=usuario)
        if usuario:
            handler._serve_json(res)
        else:
            handler._not_found()

    def add_usuario(handler,novoUsuario):
        usuarios.append(novoUsuario)
        res = Response(status=201,data=novoUsuario)
        if novoUsuario:
            handler._serve_json(res)
        else:
            handler._not_found()
        
        
    def getAllUsuarios(handler):
        res = Response(status=200,data=usuarios)
        if usuarios:
            handler._serve_json(res)
        else:
            handler._not_found()

    # Registro da rota com path variable
    RouteHandler.add_route("/usuarios",methods={"GET": getAllUsuarios})
    RouteHandler.add_route("/usuarios/{id}", methods={"GET": handle_get_usuario})
    RouteHandler.add_route("/a", methods={"POST": add_usuario})
    # print(RouteHandler.routes)

    WebServer.start(port=9090)  