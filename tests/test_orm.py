from arcforge.core.model import *
from arcforge.core.db import *
from colorama import Fore, Style, init

# Inicializando o colorama
init(autoreset=True)

dao = DAO()
query = Query()

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
    dao.create_table(Cliente)
    dao.create_table(Pedido)

def test_insert_clientes():
    """Insere múltiplos clientes na base de dados."""
    clientes_data = [
        {"nome": "João Silva", "email": "joao@email.com"},
        {"nome": "Maria Souza", "email": "maria@email.com"},
        {"nome": "Pedro Oliveira", "email": "pedro@email.com"},
        {"nome": "Ana Costa", "email": "ana@email.com"},
        {"nome": "Carlos Pereira", "email": "carlos@email.com"}
    ]
    clientes = []
    for data in clientes_data:
        cliente = dao.save(Cliente(**data))
        clientes.append(cliente)
        print(f"{Fore.GREEN}Cliente inserido: {Style.BRIGHT}{cliente}")
    return clientes

def test_insert_pedidos(clientes):
    """Insere pedidos de itens eletrônicos para cada cliente."""
    produtos = [
        "Smartphone Samsung Galaxy S22",
        "Notebook Dell Inspiron 15",
        "Monitor LG Ultrawide 29'",
        "Fone de Ouvido Bluetooth JBL",
        "Teclado Mecânico RGB Logitech",
        "Mouse Gamer Razer DeathAdder",
        "SSD NVMe 1TB Kingston",
        "Caixa de Som Bluetooth Bose",
        "Smartwatch Apple Watch Series 8",
        "Câmera Canon EOS Rebel T7"
    ]

    pedidos = []
    for i, cliente in enumerate(clientes):
        produto1 = produtos[i % len(produtos)]
        produto2 = produtos[(i + 1) % len(produtos)]

        pedido1 = dao.save(Pedido(descricao=f"Compra de {produto1}", cliente=cliente))
        pedido2 = dao.save(Pedido(descricao=f"Compra de {produto2}", cliente=cliente))

        pedidos.extend([pedido1, pedido2])
        print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido1}")
        print(f"{Fore.GREEN}Pedido inserido: {Style.BRIGHT}{pedido2}")

    return pedidos

def test_update_pedido(pedido):
    """Atualiza a descrição de um pedido específico."""
    pedido.descricao = "Compra de Notebook Gamer ASUS ROG"
    dao.update(pedido)
    pedido_atualizado = dao.read(Pedido, pedido.id)
    print(f"{Fore.GREEN}Pedido atualizado: {Style.BRIGHT}{pedido_atualizado}")

def test_query_pedidos():
    """Consulta e exibe todos os pedidos registrados."""
    result = query.execute(Pedido, order_by="id")
    print(f"\n{Fore.GREEN}Todos os pedidos registrados:")
    colunas = ['ID ','Descrição','Cliente Vinculado']
    print(f"{colunas[0]:<3} | {colunas[1]:<40} | {colunas[2]}\n")
    for pedido in result:
        print(f"{pedido.id:<3} | {pedido.descricao:<40} | {pedido.cliente}")

def test_delete_pedido(pedido):
    """Deleta um pedido específico e verifica a exclusão."""
    dao.delete(pedido)
    pedido_deletado = dao.read(Pedido, pedido.id)
    assert pedido_deletado is None, "O pedido deveria ter sido removido do banco."
    print(f"{Fore.RED}Pedido deletado: {Style.BRIGHT}{pedido.id}")

def delete_all():
    """Exclui todas as tabelas utilizadas para os testes."""
    dao.delete_table(Pedido)  # Excluímos primeiro a tabela com chaves estrangeiras
    dao.delete_table(Cliente)

# Executando os testes
if __name__ == "__main__":
    setup_database()
    clientes = test_insert_clientes()
    pedidos = test_insert_pedidos(clientes)
    test_update_pedido(pedidos[0])
    test_delete_pedido(pedidos[1])
    test_query_pedidos()
    delete_all()