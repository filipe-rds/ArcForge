from arcforge.core.model.model import *
# from arcforge.core.conn.controller import *
from colorama import Fore, Style, init
import random
from arcforge.core.db import *
from arcforge.core.conn import *
from arcforge import template_engine



# Inicializa o colorama
init(autoreset=True)

# Inicializa a conexão com o banco
dao = DAO()
query = Query()

# Modelo Cliente
@Model.Table("tb_cliente")
class Cliente(Model):
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

# Modelo Pedido com relacionamento para Cliente
@Model.Table("tb_pedido")
class Pedido(Model):
    id = IntegerField(primary_key=True)
    descricao = CharField(max_length=200)
    cliente = ManyToOne(Cliente, on_delete="CASCADE")


class ClienteListDTO(ModelDTO):
    def __init__(self, cliente):
        self.id = cliente.id
        self.nome = cliente.nome
        self.email = cliente.email

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email
        }

class PedidoListDTO(ModelDTO):
    def __init__(self, pedido):
        self.id = pedido.id
        self.descricao = pedido.descricao
        self.cliente = ClienteListDTO(pedido.cliente) if pedido.cliente else None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "descricao": self.descricao,
            "cliente": self.cliente.to_dict() if self.cliente else None
        }

# Configuração do banco e inserção de dados
def setup_database():
    # Cria as tabelas
    dao.create_table(Cliente)
    dao.create_table(Pedido)

    # Inserindo vários clientes
    clientes_data = [
        {"nome": "João Silva", "email": "joao@email.com"},
        {"nome": "Maria Souza", "email": "maria@email.com"},
        {"nome": "Carlos Pereira", "email": "carlos@email.com"},
        {"nome": "Ana Costa", "email": "ana@email.com"},
        {"nome": "Pedro Oliveira", "email": "pedro@email.com"},
        {"nome": "Roberta Lima", "email": "roberta@email.com"},
        {"nome": "Ricardo Alves", "email": "ricardo@email.com"},
        {"nome": "Fernanda Souza", "email": "fernanda@email.com"},
        {"nome": "Marcos Paulo", "email": "marcos@email.com"},
        {"nome": "Juliana Santos", "email": "juliana@email.com"}
    ]
    clientes = []
    for data in clientes_data:
        cliente = dao.save(Cliente(**data))
        clientes.append(cliente)
        print(f"{Fore.GREEN}Cliente inserido: {Style.BRIGHT}{cliente}")

    # Lista de produtos eletrônicos para simular pedidos
    produtos = [
        "Smartphone Samsung Galaxy S22",
        "Notebook Dell Inspiron 15",
        "Monitor LG Ultrawide",
        "Fone de Ouvido Bluetooth JBL",
        "SSD NVMe 1TB Kingston",
        "Mouse Gamer Razer",
        "Teclado Mecânico Logitech",
        "Smartwatch Apple Watch Series 8",
        "Câmera Canon EOS Rebel T7",
        "Caixa de Som Bose"
    ]

    # Para cada cliente, cria 2 pedidos com produtos aleatórios
    for cliente in clientes:
        for _ in range(2):
            produto = random.choice(produtos)
            descricao = f"Compra de {produto} para {cliente.nome}"
            pedido = dao.save(Pedido(descricao=descricao, cliente=cliente))
            print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido}")

# Função para excluir todas as tabelas (importante excluir primeiro a tabela com relacionamentos)
def delete_all():
    dao.delete_table(Pedido)
    dao.delete_table(Cliente)
    print(f"{Fore.RED}Todas as tabelas foram excluídas.")


class ClienteController(Controller):

    @Router.route("/clientes", "GET")
    def get_clientes(request: Request):
        """Retorna todos os clientes cadastrados em um template HTML"""
        clientes = dao.find_all(Cliente)
        if clientes:
            rendered_html = template_engine.render_template("clientes.html", clientes=clientes)
            return HtmlResponse(HttpStatus.OK, rendered_html)

        return HtmlResponse(HttpStatus.NOT_FOUND, "<h1>Nenhum cliente encontrado</h1>")

class AuthController(Controller):
    @Router.route("/login", "GET")
    def login_page(request: Request):
        """Retorna a página de login."""
        return HtmlResponse(HttpStatus.OK, template_engine.render_template("login.html"))

    @Router.route("/login", "POST")
    def login(request: Request):
        """Processa o login e armazena na sessão."""
        
        
        print(request.form)
        print(request.body)
        nome = request.form.get("nome")
        email = request.form.get("email")

        print(f"nome: {nome} email: {email}")

        if not nome or not email:
            return HtmlResponse(HttpStatus.BAD_REQUEST, "<h1>Nome e email são obrigatórios!</h1>")

        usuario = query.execute(Cliente, nome=nome, email=email)
        

        if not usuario:
            return HtmlResponse(
                HttpStatus.UNAUTHORIZED, 
                "<h1>Usuário não encontrado!</h1><a href='/login'>Tentar novamente</a>"
            )

        # Armazena na sessão corretamente usando set()
        request.session.set("user", {"id": usuario.id, "nome": usuario.nome, "email": usuario.email})

        return RedirectResponse("/dashboard")


    @Router.route("/dashboard", "GET")
    def dashboard(request: Request):
        """Mostra a página do usuário logado."""
        user = request.session.get("user")  # Obtém a sessão corretamente

        if not user:
            return RedirectResponse("/login")

        return HtmlResponse(HttpStatus.OK, template_engine.render_template("dashboard.html", user=user))


if __name__ == "__main__":
    setup_database()
    # Instancia os controladores para registrar as rotas automaticamente
    ClienteController()
    AuthController()
   
    # Inicializa e executa o servidor
    server = WebServer(port=8080)
    try:
        server.start()  # O servidor ficará ativo até ser interrompido
    except KeyboardInterrupt:
        logging.info("Servidor interrompido via KeyboardInterrupt")
    finally:
        logging.info("Servidor encerrado. Excluindo todas as tabelas...")
        delete_all()