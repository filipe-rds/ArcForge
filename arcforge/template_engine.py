from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from .factory_template_engine import TemplateEngineFactory
import os

class TemplateEngine:
    """
    Classe responsável por gerenciar a renderização de templates com Jinja2.
    Sempre busca os templates na pasta fixa 'templates' dentro do projeto.
    """
    def __init__(self):
        # Obtém o diretório raiz do projeto e fixa o caminho dos templates
        project_root = os.path.dirname(os.path.abspath(__file__))  # Caminho do arquivo atual
        self.template_dir = os.path.join(project_root, "templates")  # templates dentro do projeto
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def render_template(self, template_name, **context):
        """
        Renderiza um template HTML com as variáveis fornecidas.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(context)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_name}' não encontrado em '{self.template_dir}'")
        except Exception as e:
            raise RuntimeError(f"Erro ao renderizar template '{template_name}': {e}")


factory = TemplateEngineFactory() 
template_engine = factory.create_template_engine()  # Criando uma instância global do TemplateEngine