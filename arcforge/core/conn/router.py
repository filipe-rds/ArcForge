import re


class Router:
    """
    Classe responsável por gerenciar o mapeamento de rotas para os métodos HTTP correspondentes.
    """
    routes = []

    @classmethod
    def route(cls, path: str, method: str):
        """Decorator para adicionar uma rota ao roteador."""
        def wrapper(func):
            pattern = cls._path_to_regex(path)
            compiled_pattern = re.compile(f"^{pattern}$")

            # Verifica se a rota já existe
            for route in cls.routes:
                if route["path"] == path:
                    # Atualiza ou adiciona o método à rota existente
                    route["methods"][method.upper()] = func
                    return func

            # Se não existir, cria uma nova rota
            cls.routes.append({
                "path": path,
                "pattern": compiled_pattern,
                "methods": {method.upper(): func},
            })
            return func
        return wrapper

    @classmethod 
    def match(cls, path, method): 
        """Procura uma rota correspondente ao caminho e método da requisição.""" 
        for route in cls.routes: 
            match = route["pattern"].match(path) 
            if match and method in route["methods"]: 
                return True, route["methods"][method], match.groupdict() 
        return False, None, {}

    @staticmethod
    def _path_to_regex(path: str) -> str:
        """Converte uma rota com parâmetros (ex.: "/usuarios/{id}") em uma regex."""
        return re.sub(r"{(\w+)}", r"(?P<\1>[^/]+)", path)

