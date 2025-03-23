from arcforge.core.model.model import *
# from arcforge.core.conn.controller import *
from colorama import Fore, Style, init
import random
from arcforge.core.db import *
from arcforge.core.conn import *
#

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

# Controlador para Cliente
class ClienteController(Controller):
    
   
    @Router.route("/clientes", "GET")
    def get_clientes(request: Request):
        """Retorna todos os clientes cadastrados"""
        clientes = dao.find_all(Cliente)
        if clientes:
            serialized_clientes = [ClienteListDTO(cliente).to_dict() for cliente in clientes]
            return Response(HttpStatus.OK, serialized_clientes)
        return Response(HttpStatus.NOT_FOUND, {"error": "Nenhum cliente encontrado"})

    @Router.route("/clientes/{id}", "GET")
    @Validator(id=int)
    def get_cliente(request: Request, id):
        """Retorna um cliente pelo ID"""
        cliente = dao.read(Cliente, id)
        if cliente:
            return Response(HttpStatus.OK, cliente)
        return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado"})

    @Router.route("/clientes", "POST")
    def create_cliente(request: Request):
        print(request.body)
        """Cria um novo cliente com os dados fornecidos no corpo da requisição"""
        print('PRINT DO REQUEST.BODY')
        novo_cliente_data = request.body  # O body agora está dentro da instância de Request
        cliente = Cliente(**novo_cliente_data)
        dao.save(cliente)
        print(f"{Fore.GREEN}Cliente inserido via API: {Style.BRIGHT}{cliente}")
        return Response(HttpStatus.CREATED, cliente)
    
# Controlador para Pedido
class PedidoController(Controller):
    @Router.route("/pedidos", "GET")
    def get_pedidos(request: Request):
        pedidos = dao.find_all(Pedido)
        if pedidos:
            serialized_pedidos = [PedidoListDTO(pedido).to_dict() for pedido in pedidos]
            return Response(HttpStatus.OK, serialized_pedidos)
        return Response(HttpStatus.NOT_FOUND, {"error": "Nenhum pedido encontrado"})

    @Router.route("/pedidos/{id}", "GET")
    def get_pedido(request: Request, id):
        pedido = dao.read(Pedido, id)
        if pedido:
            return Response(HttpStatus.OK, pedido)
        return Response(HttpStatus.NOT_FOUND, {"error": "Pedido não encontrado"})

    @Router.route("/pedidos", "POST")
    def create_pedido(request: Request):
        cliente = dao.read(Cliente, request.body.get("cliente_id"))
        if not cliente:
            return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado para o pedido"})
        pedido = Pedido(descricao= request.body.get("descricao"), cliente=cliente)
        dao.save(pedido)
        print(f"{Fore.GREEN}Pedido inserido via API: {Style.BRIGHT}{pedido}")
        return Response(HttpStatus.CREATED, pedido)

    
class AuthController(Controller):
    @Router.route("/login", "POST")
    def login(request: Request):
        """Realiza o login do cliente e armazena na sessão"""
        email = request.body.get("email")
        if not email:
            return Response(HttpStatus.BAD_REQUEST, {"error": "O campo 'email' é obrigatório"})
        
        cliente = query.execute(Cliente, order_by="id", email=email)
        if not cliente:
            return Response(HttpStatus.UNAUTHORIZED, {"error": "E-mail não encontrado"})
        
        # Retorna os dados do cliente autenticado
        cliente_dto = ClienteListDTO(cliente)
        
        # Armazena o cliente na sessão
        request.session.set("cliente", cliente_dto.to_dict())
        
        # Retorna uma resposta de sucesso
        return Response(HttpStatus.OK, {"message": "Login bem-sucedido", "cliente": cliente_dto.to_dict()})
    
    @Router.route("/session", "GET")
    def check_session(request: Request):
        cliente_data = request.session.get("cliente", "Não encontrado")
        
        # Verifica se é um tipo serializável para a resposta JSON
        if not isinstance(cliente_data, (dict, list, str, int, float, bool, type(None))):
            cliente_data = str(cliente_data)
        
        return Response(HttpStatus.OK, {
            "message": "Sessão ativa",
            "session_id": request.session.session_id,
            "cliente_data": cliente_data
        })

    @Router.route("/logout", "POST")
    def logout(request: Request):
        # Limpa os dados da sessão
        request.session.delete()
        
        return Response(HttpStatus.OK, {"message": "Logout realizado com sucesso"})

if __name__ == "__main__":
    setup_database()
    # Instancia os controladores para registrar as rotas automaticamente
    ClienteController()
    PedidoController()
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