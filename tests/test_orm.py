from arcforge.core.model import *
from arcforge.core.db import *
from colorama import Fore, init

# Inicializando o colorama
init(autoreset=True)

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

# Daos
class DaoPedido(DAO):
    _model = Pedido

class DaoCliente(DAO):
    _model = Cliente

# Função para configurar o banco
def setup_database():
    dao_cliente = DaoCliente()
    dao_pedido = DaoPedido()

    dao_cliente.create_table()
    dao_pedido.create_table()

# Função para inserir clientes
def insert_clientes():
    dao_cliente = DaoCliente()
    clientes = [
        Cliente(nome="João Silva", email="joao@email.com"),
        Cliente(nome="Maria Souza", email="maria@email.com"),
        Cliente(nome="Pedro Oliveira", email="pedro@email.com"),
        Cliente(nome="Ana Costa", email="ana@email.com"),
        Cliente(nome="Carlos Pereira", email="carlos@email.com")
    ]

    for cliente in clientes:
        dao_cliente.save(cliente)
        print(Fore.GREEN + f"Cliente inserido: {cliente.nome} - {cliente.email}")

    return clientes

# Função para buscar todos os clientes
def find_all_clientes():
    dao_cliente = DaoCliente()
    clientes = dao_cliente.find_all()
    print(Fore.CYAN + "\nClientes cadastrados:")
    for cliente in clientes:
        print(f"ID: {cliente.id} | Nome: {cliente.nome} | Email: {cliente.email}")
    return clientes

# Função para inserir pedidos com distribuição variada
def insert_pedidos(clientes):
    dao_pedido = DaoPedido()
    pedidos = []
    produtos = [
        "Smartphone Samsung Galaxy S22",
        "Notebook Dell Inspiron 15",
        "Monitor LG Ultrawide 29'",
        "Fone de Ouvido Bluetooth JBL",
        "Teclado Mecânico RGB Logitech",
        "Mouse Gamer Razer",
        "Cadeira Gamer ThunderX3",
        "Headset HyperX Cloud",
        "Tablet iPad Pro 12.9'",
        "Smart TV Samsung 55'",
        "Câmera Sony Alpha A7 III",
        "Console PlayStation 5"
    ]

    # Distribuição de pedidos:
    # - Cliente 1: 3 pedidos
    # - Cliente 2: 2 pedidos
    # - Cliente 3: 2 pedidos
    # - Cliente 4: 1 pedido
    # - Cliente 5: 1 pedido

    # 3 pedidos para o primeiro cliente (João)
    for i in range(3):
        pedido = Pedido(descricao=f"Compra de {produtos[i]}", cliente=clientes[0])
        dao_pedido.save(pedido)
        pedidos.append(pedido)
        print(Fore.GREEN + f"Pedido inserido: {pedido.descricao} para {clientes[0].nome}")

    # 2 pedidos para o segundo cliente (Maria)
    for i in range(3, 5):
        pedido = Pedido(descricao=f"Compra de {produtos[i]}", cliente=clientes[1])
        dao_pedido.save(pedido)
        pedidos.append(pedido)
        print(Fore.GREEN + f"Pedido inserido: {pedido.descricao} para {clientes[1].nome}")

    # 2 pedidos para o terceiro cliente (Pedro)
    for i in range(5, 7):
        pedido = Pedido(descricao=f"Compra de {produtos[i]}", cliente=clientes[2])
        dao_pedido.save(pedido)
        pedidos.append(pedido)
        print(Fore.GREEN + f"Pedido inserido: {pedido.descricao} para {clientes[2].nome}")

    # 1 pedido para o quarto cliente (Ana)
    pedido = Pedido(descricao=f"Compra de {produtos[7]}", cliente=clientes[3])
    dao_pedido.save(pedido)
    pedidos.append(pedido)
    print(Fore.GREEN + f"Pedido inserido: {pedido.descricao} para {clientes[3].nome}")

    # 1 pedido para o quinto cliente (Carlos)
    pedido = Pedido(descricao=f"Compra de {produtos[8]}", cliente=clientes[4])
    dao_pedido.save(pedido)
    pedidos.append(pedido)
    print(Fore.GREEN + f"Pedido inserido: {pedido.descricao} para {clientes[4].nome}")

    return pedidos


def find_all_pedidos():
    """Lista todos os pedidos com seus respectivos clientes."""
    dao_pedido = DaoPedido()
    dao_cliente = DaoCliente()

    pedidos = dao_pedido.find_all()

    print(f"\n{Fore.BLUE}Lista de Pedidos e seus Clientes:")
    print(f"{'ID':<3} | {'Descrição':<40} | {'Cliente':<20} | {'Email'}")
    print("-" * 80)

    for pedido in pedidos:
        cliente = dao_cliente.read(pedido.cliente.id)  # Obtendo o cliente pelo ID
        print(f"{pedido.id:<3} | {pedido.descricao:<40} | {cliente.nome:<20} | {cliente.email}")

# Função para atualizar um pedido
def update_pedido(pedido):
    dao_pedido = DaoPedido()
    pedido.descricao = "Compra de Notebook Gamer ASUS ROG"
    dao_pedido.update(pedido)
    pedido_atualizado = dao_pedido.read(pedido.id)
    print(Fore.YELLOW + f"Pedido atualizado: {pedido_atualizado.descricao}")

# Função para deletar um pedido
def delete_pedido(pedido):
    dao_pedido = DaoPedido()
    dao_pedido.delete(pedido.id)
    pedido_deletado = dao_pedido.read(pedido.id)
    print(Fore.RED + f"Pedido deletado? {'Sim' if pedido_deletado is None else 'Não'}")


# Consultas
def consultar_clientes_com_multiplos_pedidos():
    """Consulta clientes com mais de 1 pedido usando QueryBuilder"""
    print(Fore.MAGENTA + "\n[QUERY BUILDER] Clientes com mais de 1 pedido:")

    # Usando JOIN e SELECT para trazer os dados necessários em uma única consulta
    resultados = (
        QueryBuilder(Pedido)
        .join(Cliente)  # Adiciona um JOIN com a tabela de clientes
        .group_by('tb_cliente.id', 'tb_cliente.nome')  # Agrupamento incluindo o nome
        .annotate(
            cliente_id="tb_cliente.id",
            cliente_nome="tb_cliente.nome",
            total_pedidos=Count('*')
        )
        .having(total_pedidos__gt=1)                # Filtro por clientes com mais de 1 pedido
        .order_by('total_pedidos DESC')             # Ordenação decrescente
        .execute()
    )

    print(f"{'ID Cliente':<12} | {'Nome Cliente':<25} | {'Total Pedidos':<14}")
    print("-" * 55)

    # Agora você pode percorrer os resultados diretamente
    for resultado in resultados:
        print(f"{resultado.cliente_id:<12} | {resultado.cliente_nome:<25} | {resultado.total_pedidos:<14}")
    return resultados

def consultar_todos_clientes_com_contagem_pedidos():
    """Consulta todos os clientes com contagem de pedidos"""
    print(Fore.CYAN + "\n[QUERY BUILDER] Todos os clientes com contagem de pedidos:")

    resultados = (
        QueryBuilder(Pedido)
        .join(Cliente)
        .group_by('tb_cliente.id', 'tb_cliente.nome', 'tb_cliente.email')
        .annotate(
            cliente_id="tb_cliente.id",
            cliente_nome="tb_cliente.nome",
            cliente_email="tb_cliente.email",
            total_pedidos=Count('*')
        )
        .order_by('total_pedidos DESC')
        .execute()
    )

    print(f"{'ID Cliente':<12} | {'Nome Cliente':<25} | {'Email':<25} | {'Total Pedidos':<14}")
    print("-" * 80)

    for resultado in resultados:
        print(f"{resultado.cliente_id:<12} | {resultado.cliente_nome:<25} | {resultado.cliente_email:<25} | {resultado.total_pedidos:<14}")
    return resultados

def consultar_pedidos_por_cliente_sql(cliente_id: int):
    """Consulta usando execute_sql: Pedidos de um cliente específico com JOIN manual"""
    print(Fore.MAGENTA + f"\n[QUERY BUILDER - PURO SQL] Pedidos do cliente ID {cliente_id}:")
    sql_query = """
        SELECT p.id, p.descricao, c.nome 
        FROM tb_pedido p
        JOIN tb_cliente c ON p.cliente_id = c.id
        WHERE p.cliente_id = %s
    """
    resultados_sql = QueryBuilder(Pedido).execute_sql(sql_query, [cliente_id])
    print(f"{'ID':<5} | {'Descrição':<40} | {'Cliente'}")
    print("-" * 60)
    for item in resultados_sql:
        print(f"{item[0]:<5} | {item[1]:<40} | {item[2]}")
    return resultados_sql

# Função para deletar todas as tabelas
def delete_all():
    dao_pedido = DaoPedido()
    dao_cliente = DaoCliente()

    dao_pedido.delete_table()
    dao_cliente.delete_table()
    print(Fore.RED + "Todas as tabelas foram removidas do banco de dados.")

# Função principal
def executar_testes():
    print(Fore.YELLOW + "Configurando o banco de dados...")
    setup_database()

    print(Fore.YELLOW + "Inserindo clientes...")
    clientes = insert_clientes()

    print(Fore.YELLOW + "Listando todos os clientes...")
    find_all_clientes()

    print(Fore.YELLOW + "Inserindo pedidos com distribuição variada...")
    pedidos = insert_pedidos(clientes)

    print(Fore.YELLOW + "Listando todos os pedidos...")
    find_all_pedidos()

    print(Fore.YELLOW + "\nExecutando consultas avançadas:")

    # Consulta de todos os clientes com contagem de pedidos
    consultar_todos_clientes_com_contagem_pedidos()

    # Consulta de clientes com múltiplos pedidos
    consultar_clientes_com_multiplos_pedidos()

    # Consulta detalhada de pedidos para um cliente específico
    if clientes:
        consultar_pedidos_por_cliente_sql(clientes[0].id)

    print(Fore.YELLOW + "Atualizando um pedido...")
    if pedidos:
        update_pedido(pedidos[0])

    print(Fore.YELLOW + "Deletando um pedido...")
    if len(pedidos) > 1:
        delete_pedido(pedidos[1])

    print(Fore.YELLOW + "Listando pedidos após modificações...")
    find_all_pedidos()

    print(Fore.YELLOW + "Finalizando testes e removendo tabelas...")
    delete_all()

if __name__ == "__main__":
    executar_testes()