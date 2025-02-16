from arcforge.core.conn.handler import *
from arcforge.core.conn.response import *
from arcforge.core.conn.server import *

from arcforge.core.conn.handler import __all__ as handler_all
from arcforge.core.conn.response import __all__ as response_all
from arcforge.core.conn.server import __all__ as server_all


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
        Registra automaticamente os métodos do controlador decorados com @RequestHandler.route.
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_route_info"):
                path, method = attr._route_info
                RequestHandler.add_route(path, {method: attr})

__all__ = ["Controller"] + handler_all + response_all + server_all