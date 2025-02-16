from arcforge.core.model.model import *
from arcforge.core.conn.controller import *
from colorama import Fore, Style, init
import random
from http.cookies import SimpleCookie

# Inicializa o colorama
init(autoreset=True)

# Inicializa a conexão com o banco
db = DatabaseConnection()

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
    db.create_table(Cliente)
    db.create_table(Pedido)

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
        cliente = db.save(Cliente(**data))
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
            pedido = db.save(Pedido(descricao=descricao, cliente=cliente))
            print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido}")

# Função para excluir todas as tabelas (importante excluir primeiro a tabela com relacionamentos)
def delete_all():
    db.delete_table(Pedido)
    db.delete_table(Cliente)
    print(f"{Fore.RED}Todas as tabelas foram excluídas.")

# Controlador para Cliente
class ClienteController(Controller):
    @RequestHandler.route("/clientes", "GET")
    def get_clientes(handler):
        clientes = db.find_all(Cliente)
        if clientes:
            # Serializa cada pedido incluindo o cliente completo
            serialized_clientes = [ClienteListDTO(cliente).to_dict() for cliente in clientes]
            return Response(HttpStatus.OK, serialized_clientes)
        return Response(HttpStatus.NOT_FOUND, {"error": "Nenhum cliente encontrado"})

    @RequestHandler.route("/clientes/{id}", "GET")
    def get_cliente(handler, id):
        cliente = db.read(Cliente, id)
        if cliente:
            return Response(HttpStatus.OK, cliente)
        return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado"})

    @RequestHandler.route("/clientes", "POST")
    def create_cliente(handler, novoCliente):  # O body já chega pronto como dicionário
        cliente = Cliente(**novoCliente)
        db.save(cliente)
        print(f"{Fore.GREEN}Cliente inserido via API: {Style.BRIGHT}{cliente}")
        return Response(HttpStatus.CREATED, cliente)

    @RequestHandler.route("/clientes/{id}", "PUT")
    def update_cliente(handler, body, id):
        cliente = db.read(Cliente, id)
        if not cliente:
            return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado"})
        for key, value in body.items():
            setattr(cliente, key, value)
        db.update(cliente)
        return Response(HttpStatus.OK, cliente)

# Controlador para Pedido
class PedidoController(Controller):
    @RequestHandler.route("/pedidos", "GET")
    def get_pedidos(handler):
        pedidos = db.find_all(Pedido)
        if pedidos:
            # Serializa cada pedido incluindo o cliente completo
            serialized_pedidos = [PedidoListDTO(pedido).to_dict() for pedido in pedidos]
            return Response(HttpStatus.OK, serialized_pedidos)
        return Response(HttpStatus.NOT_FOUND, {"error": "Nenhum pedido encontrado"})

    @RequestHandler.route("/pedidos/{id}", "GET")
    def get_pedido(handler, id):
        pedido = db.read(Pedido, id)
        if pedido:
            return Response(HttpStatus.OK, pedido)
        return Response(HttpStatus.NOT_FOUND, {"error": "Pedido não encontrado"})

    @RequestHandler.route("/pedidos", "POST")
    def create_pedido(handler, novoPedido):
        # Supondo que novoPedido seja um dicionário com 'descricao' e 'cliente_id'
        cliente = db.read(Cliente, novoPedido.get("cliente_id"))
        if not cliente:
            return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado para o pedido"})
        pedido = Pedido(descricao=novoPedido.get("descricao"), cliente=cliente)
        db.save(pedido)
        print(f"{Fore.GREEN}Pedido inserido via API: {Style.BRIGHT}{pedido}")
        return Response(HttpStatus.CREATED, pedido)

    @RequestHandler.route("/pedidos/{id}", "PUT")
    def update_pedido(handler, body, id):
        pedido = db.read(Pedido, id)
        if not pedido:
            return Response(HttpStatus.NOT_FOUND, {"error": "Pedido não encontrado"})
        for key, value in body.items():
            if key == "cliente_id":  # Atualiza o relacionamento se necessário
                cliente = db.read(Cliente, value)
                if not cliente:
                    return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado para o pedido"})
                setattr(pedido, "cliente", cliente)
            else:
                setattr(pedido, key, value)
        db.update(pedido)
        return Response(HttpStatus.OK, pedido)
    
class AuthController(Controller):
    @RequestHandler.route("/login", "POST")
    def login(handler, body):
        handler.init_session()  # Garante que a sessão seja iniciada
        print("1")
        # Verifica se o campo "email" foi enviado
        email = body.get("email")
        if not email:
            return Response(HttpStatus.BAD_REQUEST, {"error": "O campo 'email' é obrigatório"})
        print(2)
        # Consulta o cliente pelo e-mail
        cliente = db.query(Cliente, order_by="id", email=email)
        if not cliente:
            return Response(HttpStatus.UNAUTHORIZED, {"error": "E-mail não encontrado"})
        print(3)
        # Retorna os dados do cliente autenticado
        cliente_dto = ClienteListDTO(cliente)
        cliente_novo = Cliente(**cliente_dto.to_dict())
        print(4)
        # Armazena o cliente na sessão
        handler.set_session("cliente", cliente_novo)
        print(5)
        # Retorna uma resposta de sucesso
        return Response(HttpStatus.OK, {"message": "Login bem-sucedido", "cliente": cliente_novo.to_dict()})
    
    @RequestHandler.route("/session", "GET")
    def check_session(handler):
        handler.init_session()  # Garante que a sessão esteja iniciada
        session_data = handler.get_session("cliente", default="Não encontrado")  # Usando get_session para acessar o valor

        if not isinstance(session_data, dict):
            session_data = str(session_data)

        return Response(HttpStatus.OK, {"message": "Sessão ativa", "session_data": session_data})

    @RequestHandler.route("/logout", "POST")
    def logout(handler):
        # Inicia ou recupera a sessão
        handler.init_session()  # Garante que a sessão seja iniciada

        # Invalida a sessão removendo o cookie
        cookie = SimpleCookie()
        cookie["session_id"] = ""
        cookie["session_id"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        
        # Remove os dados da sessão utilizando o método 'set_session'
        if handler.session_id:
            handler.set_session("cliente", None)  # Exemplo de remoção de dados da sessão, se necessário

        handler.send_header("Set-Cookie", cookie.output(header="", sep=""))

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