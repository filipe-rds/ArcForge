import copy
from arcforge.core.db.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


# Padrão utilzado: Prototype
# A classe DBConfigPrototype define um protótipo de configuração de banco de dadoos, 
# permitindo a criação de clones com valores padrão.
# -----------------------------------------------------------------------------

import copy

class DBConfigPrototype:
    def __init__(self):
        # Inicializando com valores None
        self.name = None
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    def clone(self, **overrides):
        # Cria uma cópia do protótipo base e substitui os valores desejados, se houver
        new_config = copy.deepcopy(self)
        for key, value in overrides.items():
            setattr(new_config, key, value)
        
        # Validação: se algum campo necessário estiver None, levanta um erro
        if not new_config.name or not new_config.user or not new_config.password:
            raise ValueError("Faltando valores obrigatórios para a configuração do banco de dados.")
        return new_config

# Criando o protótipo base
default_config = DBConfigPrototype()