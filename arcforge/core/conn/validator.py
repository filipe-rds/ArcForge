from functools import wraps
from .response import *

class Validator:
    """
    Decorator para interceptar os tipos dos parâmetros de uma requisição de forma genérica.
    Padrão INTERCEPTOR
    Exemplo de uso: @Validator(id=int, nome=str, ativo=bool)
    """
    def __init__(self, **expected_types):
        self.expected_types = expected_types

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            errors = {}

            # Valida os parâmetros passados na requisição
            for param, expected_type in self.expected_types.items():
                if param in kwargs:
                    try:
                        # Tenta converter para o tipo esperado, caso não consiga, lança exceção
                        converted_value = expected_type(kwargs[param])
                        kwargs[param] = converted_value
                    except (ValueError, TypeError):
                        # lanca erro 500 se der errd
                        errors[param] = f"Parâmetro '{param}' deve ser do tipo {expected_type.__name__}"
            if errors:
                # Se houver erros de tipo, retorna erro 500
                return Response(
                    HttpStatus.INTERNAL_SERVER_ERROR,  # Código 500 (Internal Server Error)
                    {"error": "Erro interno", "detalhes": errors}
                )

            return func(*args, **kwargs)

        return wrapper
