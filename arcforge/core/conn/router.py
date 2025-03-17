class Router:
    """
    Classe responsável por gerenciar o mapeamento de rotas para os métodos HTTP correspondentes.
    """
    routes = []

    @classmethod
    def add_route(cls, path: str, method: str, func):
        """Adiciona uma rota ao roteador."""
        pattern = cls._path_to_regex(path)
        compiled_pattern = re.compile(f"^{pattern}$")
        cls.routes.append({
            "path": path,
            "pattern": compiled_pattern,
            "methods": {method.upper(): func},
        })

    @classmethod
    def match(cls, path, method):
        """Procura uma rota correspondente ao caminho e método da requisição."""
        for route in cls.routes:
            match = route["pattern"].match(path)
            if match and method in route["methods"]:
                return route["methods"][method], match.groupdict()
        return None, {}

    @staticmethod
    def _path_to_regex(path: str) -> str:
        """Converte uma rota com parâmetros (ex.: "/usuarios/{id}") em uma regex."""
        return re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)

