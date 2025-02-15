import json


class Response:
    # Dicionário de mensagens padrão para os códigos de status HTTP
    STATUS_MESSAGES = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
    }

    def __init__(self, status: int, data=None):
        """
        Inicializa a resposta HTTP.

        :param status: Código de status HTTP (ex.: 200, 404, etc.).
        :param data: Dados a serem enviados no body da resposta. Se for um objeto do
                     tipo dict ou list, será serializado para JSON; se for string, será enviado como texto.
        """
        self.status = status
        self.status_message = self.STATUS_MESSAGES.get(status, "Unknown Status")
        self.body = self._serialize(data)
        self.headers = self._build_headers()

    def _serialize(self, data) -> str:
        """
        Serializa os dados para envio no body da resposta.
        Se os dados forem um dict ou list, serializa para JSON.
        Se forem string, retorna sem modificação.
        Se forem de outro tipo, tenta converter para dicionário usando _default_serializer.

        :param data: Dados a serem serializados.
        :return: String a ser enviada como body.
        """
        if data is None:
            return ""
        if isinstance(data, (dict, list)):
            try:
                return json.dumps(data, default=self._default_serializer, indent=4, ensure_ascii=False)
            except Exception as e:
                raise ValueError("Erro ao serializar os dados para JSON.") from e
        if isinstance(data, str):
            return data
        # Para objetos personalizados, tenta converter para dicionário usando _default_serializer
        try:
            return json.dumps(data, default=self._default_serializer, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Erro ao serializar o objeto {type(data).__name__} para JSON.") from e

    def _default_serializer(self, obj):
        """
        Serializador padrão para objetos que não são serializáveis por padrão.

        :param obj: Objeto a ser serializado.
        :return: Representação em dicionário do objeto.
        :raises TypeError: Se o objeto não puder ser serializado.
        """
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise TypeError(f"Objeto do tipo {type(obj).__name__} não é serializável")

    def _build_headers(self) -> dict:
        """
        Constroi o dicionário de headers para a resposta.
        O Content-Type é definido automaticamente conforme o tipo do body:
          - 'application/json' para dados em JSON (quando o body inicia com '{' ou '[')
          - 'text/plain' para texto simples.
        Também é definido o header 'Content-Length' se houver body.

        :return: Dicionário com os headers da resposta.
        """
        headers = {}

        if self.body:
            # Define o Content-Type com base no conteúdo do body
            body_strip = self.body.lstrip()
            if body_strip.startswith("{") or body_strip.startswith("["):
                headers["Content-Type"] = "application/json; charset=utf-8"
            else:
                headers["Content-Type"] = "text/plain; charset=utf-8"
            headers["Content-Length"] = str(len(self.body.encode("utf-8")))
        else:
            # Mesmo sem body, definimos o Content-Type padrão
            headers["Content-Type"] = "text/plain; charset=utf-8"

        return headers

    def to_http_response(self) -> str:
        """
        Constrói a resposta HTTP completa (linha de status, headers e body).

        :return: String formatada como uma resposta HTTP.
        """
        status_line = f"HTTP/1.1 {self.status} {self.status_message}"
        headers_lines = "\r\n".join(f"{key}: {value}" for key, value in self.headers.items())
        return f"{status_line}\r\n{headers_lines}\r\n\r\n{self.body}"


# Exemplo de uso:
if __name__ == "__main__":
    # Exemplo 1: resposta com JSON
    resp_json = Response(200, data={"message": "Hello, World!"})
    print(resp_json.to_http_response())

    # Exemplo 2: resposta com texto simples
    resp_text = Response(404, data="Página não encontrada")
    print(resp_text.to_http_response())
