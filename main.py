from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.server import WebServer


if __name__ == "__main__":
    RouteHandler.add_route("/","pages/index.html")
    RouteHandler.add_route("/about","pages/about.html")
    RouteHandler.add_route("/data","data/info.json")
    

    WebServer.start(port=9090)