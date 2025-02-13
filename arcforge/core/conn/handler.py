from http.server import BaseHTTPRequestHandler
from abc import ABC, abstractmethod
import json
import os
import re


class BaseHandler(BaseHTTPRequestHandler, ABC):

    @abstractmethod
    def do_GET(self):
        pass

    @abstractmethod
    def do_POST(self):
        pass

class MyRequestHandler(BaseHandler):
   
    def do_GET(self):
        try:
            with open("index.html", "r", encoding="utf-8") as file:
                html_content = file.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Arquivo index.html nao encontrado")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode("utf-8")

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        response = f"Dados recebidos: {post_data}"
        self.wfile.write(response.encode("utf-8"))


class RouteHandler(BaseHandler):
  
    # Mapeamento de rotas GET (equivalente ao @GetMapping)
    routes = []

    @classmethod
    def add_route(cls, path, methods=None):
        """
        Registra uma rota com funções específicas para diferentes métodos HTTP.

        :param path: Caminho da URL (ex: "/sobre").
        :param methods: Dicionário com funções para cada método HTTP (ex: {"GET": func_get, "POST": func_post}).
        """
        if methods is None:
            methods = {}
        
        pattern = cls._path_to_regex(path)
        params = cls._extract_params(path)

        cls.routes.append({
            "path": path,
            "pattern": re.compile(f"^{pattern}$"),
            "params": params,
            "methods": {method.upper(): func for method, func in methods.items() if callable(func)}
        })
                
    
    @staticmethod
    def _path_to_regex(path):
        """
        Converte uma rota com variáveis de caminho (ex: "/usuarios/{id}") em uma regex (ex: "/usuarios/(?P<id>[^/]+)").
        """
        return re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)

    @staticmethod
    def _extract_params(path):
        """
        Extrai os parâmetros definidos entre chaves em uma rota (ex: "/usuarios/{id}").
        
        :param path: Caminho da rota.
        :return: Lista com os nomes dos parâmetros (ex: ["id"]).
        """
        return re.findall(r"{(\w+)}", path)

       

    def do_GET(self):
        """Lida com requisições GET e executa a função associada à rota."""
        self._execute_route("GET")

    def do_POST(self):
        """Lida com requisições POST e executa a função associada à rota."""
        self._execute_route("POST")

    def do_PUT(self):
        """Lida com requisições PUT e executa a função associada à rota."""
        self._execute_route("PUT")

    def do_DELETE(self):
        """Lida com requisições DELETE e executa a função associada à rota."""
        self._execute_route("DELETE")

    def _execute_route(self, method):
        """Executa a função associada à rota e ao método HTTP."""
        for route in self.routes:
            match = route["pattern"].match(self.path)
            if match:
                if method in route["methods"]:
                    func = route["methods"][method]
                    try:
                        # Extrai variáveis de caminho e passa para a função
                        func(self, **match.groupdict())
                        return
                    except Exception as e:
                        self._internal_server_error(f"Erro ao executar a rota: {e}")
        self._not_found()
        # if self.path in self.routes and method in self.routes[self.path]:
        #     try:
        #         func = self.routes[self.path][method]
        #         result = func(self)  # Chama a função associada à rota
        #         self._serve_json(result)
        #     except Exception as e:
        #         self._internal_server_error(f"Erro ao executar a rota: {e}")
        # else:
        #     self._not_found()

    def _serve_json(self, data):
        """Serializa e envia os dados como JSON."""
        try:
            json_content = json.dumps(data, default=self._custom_serializer, indent=4, ensure_ascii=False)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json_content.encode("utf-8"))
        except Exception as e:
            self._internal_server_error(f"Erro ao processar JSON: {e}")

    def _custom_serializer(self, obj):
        """Serializador personalizado para objetos complexos."""
        if hasattr(obj, "__dict__"):
            return obj.__dict__  
        raise TypeError(f"Tipo não serializável: {type(obj)}")

    def _not_found(self):
        """Retorna erro 404 quando a rota não é encontrada."""
        self.send_response(404)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        error_message = {"error": "Rota não encontrada", "status": 404}
        self.wfile.write(json.dumps(error_message).encode("utf-8"))

    def _internal_server_error(self, error_message):
        """Retorna erro 500 em caso de falha interna."""
        self.send_response(500)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        error_message = {"error": "Erro interno do servidor", "details": error_message}
        self.wfile.write(json.dumps(error_message, indent=4).encode("utf-8"))

    # @classmethod
    # def add_route(cls, path, file_path=None, json_response=None):
    #     """
    #     Registra uma rota, podendo ser uma página HTML ou um JSON carregado de um arquivo.

    #     :param path: Caminho da URL (ex: "/sobre")
    #     :param file_path: Caminho do arquivo HTML (ex: "paginas/sobre.html") ou JSON (ex: "dados/info.json")
    #     :param json_response: Dicionário JSON (opcional, caso não queira carregar de um arquivo)

    #     """
    #     if file_path:
    #         ext = os.path.splitext(file_path)[-1]  # Obtém a extensão do arquivo

    #         if ext == ".html":  # Se for um HTML
    #             cls.routes[path] = {"html": file_path}
    #         elif ext == ".json":  # Se for um JSON
    #             try:
    #                 with open(file_path, "r", encoding="utf-8") as f:
    #                     data = json.load(f)  # Carrega o JSON do arquivo
    #                 cls.routes[path] = {"json": data}
    #             except Exception as e:
    #                 raise ValueError(f"Erro ao carregar JSON: {e}")
    #         else:
    #             raise ValueError("O arquivo deve ser .html ou .json")
        
    #     elif json_response and isinstance(json_response, dict):  # Se JSON for passado diretamente
    #         cls.routes[path] = {"json": json_response}
        
    #     else:
    #         raise ValueError("É necessário fornecer um arquivo HTML, JSON ou um dicionário JSON válido!")


    # def do_GET(self):
    #     """Lida com requisições GET e responde com HTML ou JSON, dependendo da rota."""
    #     if self.path in self.routes:
    #         route = self.routes[self.path]

    #         if "html" in route:
    #             self._serve_html(route["html"])
    #         elif "json" in route:
    #             self._serve_json(route["json"])
    #     else:
    #         self._not_found()

    # def do_POST(self):
    #     """Lida com requisições POST e retorna os dados enviados."""
    #     content_length = int(self.headers.get('Content-Length', 0))
    #     post_data = self.rfile.read(content_length).decode("utf-8")

    #     response_data = {
    #         "message": "Dados recebidos com sucesso",
    #         "data": post_data
    #     }
    #     self._serve_json(response_data)

    # def _serve_html(self, file_path):
    #     # if not os.path.exists(file_path):
    #     #     self._not_found()
    #     #     return

    #     try:
    #         with open(file_path, "r", encoding="utf-8") as file:
    #             html_content = file.read()

    #         self.send_response(200)
    #         self.send_header("Content-type", "text/html")
    #         self.end_headers()
    #         self.wfile.write(html_content.encode("utf-8"))

    #     except Exception as e:
    #         self._internal_server_error(str(e))

    # def _serve_json(self, data):
    #     try:
    #         #print(data)
    #         json_content = json.dumps(data, indent=4, ensure_ascii=False)  # Formata o JSON
    #         self.send_response(200)
    #         self.send_header("Content-type", "application/json; charset=utf-8")
    #         self.end_headers()
    #         self.wfile.write(json_content.encode("utf-8"))

    #     except Exception as e:
    #         self.send_response(500)
    #         self.send_header("Content-type", "application/json; charset=utf-8")
    #         self.end_headers()
    #         error_message = json.dumps({"error": "Erro ao processar JSON", "detalhes": str(e)})
    #         self.wfile.write(error_message.encode("utf-8"))



