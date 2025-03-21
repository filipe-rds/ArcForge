from jinja2 import Environment, FileSystemLoader
import os

class TemplateEngine:
    """
    Classe responsável por gerenciar a renderização de templates com Jinja2.
    """
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name, **context):
        """
        Renderiza um template HTML com as variáveis fornecidas.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(context)
        except Exception as e:
            return f"Erro ao renderizar template {template_name}: {e}"

# Criando uma instância global do TemplateEngine
template_engine = TemplateEngine()
