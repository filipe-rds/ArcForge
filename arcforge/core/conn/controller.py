from arcforge.core.conn.handler import RouteHandler
from arcforge.core.conn.response import Response

class Controller:
    """
    Classe base para controladores.
    Todos os controladores devem herdar desta classe para registrar rotas.
    """
    def __init_subclass__(cls, **kwargs):
        """
        Ao definir uma subclasse de Controller, garante que todas as rotas decoradas
        dentro da classe sejam registradas automaticamente.
        """
        super().__init_subclass__(**kwargs)
        cls._register_routes()

    @classmethod
    def _register_routes(cls):
        """
        Registra automaticamente os métodos do controlador decorados com @RouteHandler.route.
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                path, method = attr._route_info
                RouteHandler.add_route(path, {method: attr})
