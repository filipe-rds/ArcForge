import os

# Padrão usado: Factory

class TemplateEngineFactory:
    """
    Classe responsável por criar e retornar instâncias do TemplateEngine.
    """
    def __init__(self, template_dir=None):
        # Define o template_dir padrão se não for fornecido
        self.template_dir = template_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    def create_template_engine(self):
        """
        Cria uma instância do TemplateEngine.
        """
        # Importando o TemplateEngine apenas no momento da criação
        from .template_engine import TemplateEngine # Feito dessa forma pra evitar importaç~ao circular
        return TemplateEngine()
