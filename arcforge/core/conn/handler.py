import logging
import json
import re
import http.cookies
import uuid
from functools import wraps
from http.server import BaseHTTPRequestHandler
from arcforge.core.conn import session
from arcforge.core.conn.request import Request
from arcforge.core.conn.response import Response, HttpStatus
from http.cookies import SimpleCookie

from arcforge.core.conn.router import Router
from arcforge.core.conn.session import Session


# -----------------------------------------------------------------------------
# Design Pattern: Decorator
# Permite estender a funcionalidade do mapeamento de métodos HTTP de forma
# modular, associando rotas a funções através de decorators.
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RequestHandler(BaseHTTPRequestHandler):
    """
    Manipulador de requisições HTTP, responsável por delegar chamadas ao Router
    e gerenciar sessões corretamente.
    """
    def __init__(self, *args, **kwargs):
        self.session = None
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._execute_route("GET")

    def do_POST(self):
        self._execute_route("POST")

    def do_PUT(self):
        self._execute_route("PUT")

    def do_DELETE(self):
        self._execute_route("DELETE")

    def _execute_route(self, method):
        request = Request(self)
        self.session = Session(request)
        
        # Adicione o acesso à sessão no objeto request
        request.session = self.session
        
        match, route, params = Router.match(request.path, method)
        if match:
            try:
                response = route(request, **params)
                if isinstance(response, Response):
                    # Adicionar cookies da sessão à resposta
                    if not response.cookies:
                        response.cookies = {}
                    response.cookies.update(self.session.get_cookies())
                    self._serve_json(response)
                    return
                return
            except Exception as e:
                self._internal_server_error(f"Erro ao executar a rota: {e}")
                return
        self._not_found()

    def _serve_json(self, response: Response):
        self.send_response(response.status)
        
        # Escrevendo os headers corretamente
        for key, value in response.headers.items():
            self.send_header(key, value)
        
        # Adicionando cookies da sessão ao cabeçalho
        cookies = self.session.get_cookies()
        for key, value in cookies.items():
            self.send_header("Set-Cookie", f"{key}={value}; Path=/; HttpOnly")
        
        self.end_headers()

        if response.body:
            self.wfile.write(response.body.encode("utf-8"))

    def _not_found(self):
        """Retorna um erro 404 para rotas não encontradas."""
        self._serve_json(Response(HttpStatus.NOT_FOUND, {"error": "Rota não encontrada"}))

    def _internal_server_error(self, error_message: str):
        """Retorna um erro 500 para exceções internas."""
        self._serve_json(Response(HttpStatus.INTERNAL_SERVER_ERROR, {"error": "Erro interno do servidor", "details": error_message}))
