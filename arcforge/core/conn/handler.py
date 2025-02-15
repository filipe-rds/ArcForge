import logging
import json
import re
from functools import wraps
from http.server import BaseHTTPRequestHandler
from arcforge.core.conn.response import Response

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RouteHandler(BaseHTTPRequestHandler):
    """
    Manipulador de rotas HTTP com suporte a decorators para mapeamento de métodos HTTP.
    """
    routes = []  # Lista de rotas registradas

    @classmethod
    def route(cls, path: str, method: str):
        """
        Decorador para registrar rotas HTTP específicas por método.

        :param path: Caminho da URL (ex.: "/usuarios/{id}").
        :param method: Método HTTP associado (ex.: "GET").
        """
        def decorator(func):
            @wraps(func)
            def wrapped(handler, *args, **kwargs):
                return func(handler, *args, **kwargs)

            pattern = cls._path_to_regex(path)
            params = cls._extract_params(path)

            cls.routes.append({
                "path": path,
                "pattern": re.compile(f"^{pattern}$"),
                "params": params,
                "methods": {method.upper(): wrapped},  # Ajustado para associar corretamente
                "func": wrapped
            })

            return wrapped
        return decorator

    @staticmethod
    def _path_to_regex(path: str) -> str:
        """Converte uma rota com parâmetros (ex.: "/usuarios/{id}") em uma regex."""
        return re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)

    @staticmethod
    def _extract_params(path: str) -> list:
        """Extrai os parâmetros definidos entre chaves na rota."""
        return re.findall(r"{(\w+)}", path)

    def do_GET(self):
        self._execute_route("GET")

    def do_POST(self):
        self._execute_route("POST")

    def do_PUT(self):
        self._execute_route("PUT")

    def do_DELETE(self):
        self._execute_route("DELETE")

    def _execute_route(self, method):
        """Executa a função associada à rota e ao método HTTP."""
        for route in self.routes:
            match = route["pattern"].match(self.path)
            if match and method in route["methods"]:
                func = route["methods"][method]
                try:
                    if method in ["POST", "PUT"]:
                        body = self._parse_body()  # Agora sempre processamos o body automaticamente
                        response = func(self, body, **match.groupdict())
                    else:
                        response = func(self, **match.groupdict())

                    if isinstance(response, Response):  # Garante que a resposta seja enviada corretamente
                        self._serve_json(response)
                    return
                except Exception as e:
                    self._internal_server_error(f"Erro ao executar a rota: {e}")
                    return
        self._not_found()

    def _parse_body(self):
        """Lê e interpreta o corpo da requisição como JSON e retorna um dicionário."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode('utf-8')
            try:
                return json.loads(raw_body)  # Agora retorna um dicionário pronto para ser usado
            except json.JSONDecodeError:
                return {}  # Retorna um dicionário vazio caso o JSON seja inválido
        return {}

    def _serve_json(self, response: Response):
        """Envia uma resposta HTTP formatada em JSON."""
        self.send_response(response.status)

        # Escrevendo os headers corretamente
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()

        if response.body:  # Verifica se há corpo na resposta
            if isinstance(response.body, str):
                # Se o body já for uma string JSON, converte para bytes diretamente
                self.wfile.write(response.body.encode("utf-8"))
            else:
                # Se for um dicionário/lista, serializa corretamente
                self.wfile.write(json.dumps(response.body, ensure_ascii=False).encode("utf-8"))



    def _not_found(self):
        """Retorna um erro 404 para rotas não encontradas."""
        self._serve_json(Response(404, {"error": "Rota não encontrada"}))

    def _internal_server_error(self, error_message: str):
        """Retorna um erro 500 para exceções internas."""
        self._serve_json(Response(500, {"error": "Erro interno do servidor", "details": error_message}))
