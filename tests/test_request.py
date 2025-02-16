from arcforge.core.model.model import *
from arcforge.core.conn.controller import *
from colorama import Fore, Style, init
import random

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
            return Response(HttpStatus.OK, clientes)
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
            return Response(HttpStatus.OK, pedidos)
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

if __name__ == "__main__":
    setup_database()
    # Instancia os controladores para registrar as rotas automaticamente
    ClienteController()
    PedidoController()

    # Inicializa e executa o servidor
    server = WebServer(port=8080)
    try:
        server.start()  # O servidor ficará ativo até ser interrompido
    except KeyboardInterrupt:
        logging.info("Servidor interrompido via KeyboardInterrupt")
    finally:
        logging.info("Servidor encerrado. Excluindo todas as tabelas...")
        delete_all()