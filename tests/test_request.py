from arcforge.core.model.model import *
from arcforge.core.conn.controller import *

# Inicializa a conexão com o banco
db = DatabaseConnection()

@Model.Table("tb_cliente")
class Cliente(Model):
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

# Configuração do banco
def setup_database():
    db.create_table(Cliente)
    db.save(Cliente(nome="João Silva", email="joao@email.com"))
    db.save(Cliente(nome="Maria Souza", email="maria@email.com"))

# Controlador para Cliente
class ClienteController(Controller):
    @RequestHandler.route("/clientes", "GET")
    def get_clientes(handler):
        clientes = db.find_all(Cliente)
        if clientes:
            return Response(HttpStatus.OK, clientes)  # Usando HttpStatus.OK
        return Response(HttpStatus.NOT_FOUND, {"error": "Nenhum cliente encontrado"})  # Usando HttpStatus.NOT_FOUND

    @RequestHandler.route("/clientes/{id}", "GET")
    def get_cliente(handler, id):
        cliente = db.read(Cliente, id)
        if cliente:
            return Response(HttpStatus.OK, cliente)  # Usando HttpStatus.OK
        return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado"})  # Usando HttpStatus.NOT_FOUND

    @RequestHandler.route("/clientes", "POST")
    def create_cliente(handler, novoCliente):  # O `body` já chega pronto como dicionário
        cliente = Cliente(**novoCliente)  # Constrói diretamente
        db.save(cliente)
        return Response(HttpStatus.CREATED, cliente)  # Usando HttpStatus.CREATED

    @RequestHandler.route("/clientes/{id}", "PUT")
    def update_cliente(handler, body, id):  # Agora também aceita updates diretos
        cliente = db.read(Cliente, id)
        if not cliente:
            return Response(HttpStatus.NOT_FOUND, {"error": "Cliente não encontrado"})  # Usando HttpStatus.NOT_FOUND

        for key, value in body.items():
            setattr(cliente, key, value)  # Atualiza dinamicamente os atributos
        db.update(cliente)
        return Response(HttpStatus.OK, cliente)  # Usando HttpStatus.OK


if __name__ == "__main__":
    setup_database()
    ClienteController()  # Instancia o controlador para registrar as rotas automaticamente
    WebServer(port=8080)