from arcforge.core.model.model import *
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

db = DatabaseConnection()

# Modelos
@Model.Table("tb_cliente")
class Cliente(Model):
    id = IntegerField(primary_key=True)
    nome = CharField(max_length=100)
    email = CharField(max_length=100)

@Model.Table("tb_pedido")
class Pedido(Model):
    id = IntegerField(primary_key=True)
    descricao = CharField(max_length=200)
    cliente = ManyToOne(Cliente, on_delete="CASCADE")

def setup_database():
    """Cria as tabelas necessárias para os testes."""
    db.create_table(Cliente)
    db.create_table(Pedido)

def test_insert_clientes():
    cliente1 = db.save(Cliente(nome="João Silva", email="joao@email.com"))
    cliente2 = db.save(Cliente(nome="Maria Souza", email="maria@email.com"))
    print(f"{Fore.GREEN}Cliente inserido: {Style.BRIGHT}{cliente1}")
    print(f"{Fore.GREEN}Cliente inserido: {Style.BRIGHT}{cliente2}")
    return cliente1, cliente2

def test_insert_pedidos(cliente1, cliente2):
    pedido1 = db.save(Pedido(descricao="Compra de livros", cliente=cliente1))
    pedido2 = db.save(Pedido(descricao="Compra de eletrônicos", cliente=cliente2))
    print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido1}")
    print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido2}")
    return pedido1

def test_update_pedido(pedido1):
    pedido1.descricao = "Compra de materiais escolares"
    db.update(pedido1)
    pedido_atualizado = db.read(Pedido, pedido1.id)
    print(f"{Fore.GREEN}Pedido atualizado: {Style.BRIGHT}{pedido_atualizado}")

def test_query_pedidos():
    result = db.query(Pedido)
    #result = db.query(Pedido, cliente_nome="João Silva")
    print(f"\n{Fore.GREEN}Resultado da consulta:")
    for pedido in result:
        print(f"{pedido.id:<3} | {pedido.descricao:<25} | {pedido.cliente}")

def test_delete_pedido(pedido1):
    db.delete(pedido1)
    pedido_deletado = db.read(Pedido, pedido1.id)
    assert pedido_deletado is None, "O pedido deveria ter sido removido do banco."
    print(f"{Fore.RED}Pedido deletado: {Style.BRIGHT}{pedido1.id}")

# Executando os testes
if __name__ == "__main__":
    setup_database()
    cliente1, cliente2 = test_insert_clientes()
    pedido1 = test_insert_pedidos(cliente1, cliente2)
    test_update_pedido(pedido1)
    test_query_pedidos()
    test_delete_pedido(pedido1)