class FrameworkError(Exception):
    """
    Exceção personalizada para erros relacionados ao framework.
    """

    def __init__(self, mensagem, codigo_erro=None):
        super().__init__(mensagem)
        self.codigo_erro = codigo_erro

    def __str__(self):
        if self.codigo_erro:
            return f"[ Erro {self.codigo_erro}]: {super().__str__()}"
        else:
            return super().__str__()

