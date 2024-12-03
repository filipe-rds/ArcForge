import psycopg2
from config import *
from model import BaseModel, Field, ForeignKey, OneToOne, ManyToOne, OneToMany, ManyToMany




# Função para configurar o banco de dados e as tabelas para os testes
def setup_database():
    conn = base_model.get_connection()
    cursor = conn.cursor()

    # Criar tabelas de exemplo
    class Customer(BaseModel):
        _table_name = "customers"
        id = Field("SERIAL", primary_key=True)
        name = Field("VARCHAR(100)")

    class Order(BaseModel):
        _table_name = "orders"
        id = Field("SERIAL", primary_key=True)
        customer_id = ForeignKey(Customer)
        product_name = Field("VARCHAR(100)")
        quantity = Field("INTEGER")

    # Criar as tabelas
    Customer.create_table()
    Order.create_table()

    # Fechar a conexão
    cursor.close()
    conn.close()


# Função para limpar as tabelas após os testes
def cleanup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Limpar as tabelas
    cursor.execute("DROP TABLE IF EXISTS orders, customers CASCADE;")
    conn.commit()

    cursor.close()
    conn.close()


# Função para testar a criação da tabela 'customers'
def test_create_customer_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'customers';")
    result = cursor.fetchone()
    assert result is not None, "Tabela 'customers' não foi criada."

    cursor.close()
    conn.close()


# Função para testar a criação da tabela 'orders'
def test_create_order_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'orders';")
    result = cursor.fetchone()
    assert result is not None, "Tabela 'orders' não foi criada."

    cursor.close()
    conn.close()


# Função para testar a inserção de um novo cliente
def test_add_customer():
    conn = get_connection()
    cursor = conn.cursor()

    customer = Customer(name="John Doe")
    customer.save()

    cursor.execute("SELECT * FROM customers WHERE name = 'John Doe';")
    result = cursor.fetchone()
    assert result is not None, "Cliente não foi adicionado corretamente."

    cursor.close()
    conn.close()


# Função para testar a inserção de um novo pedido
def test_add_order():
    conn = get_connection()
    cursor = conn.cursor()

    customer = Customer(name="Jane Doe")
    customer.save()

    order = Order(customer_id=1, product_name="Product A", quantity=2)
    order.save()

    cursor.execute("SELECT * FROM orders WHERE product_name = 'Product A';")
    result = cursor.fetchone()
    assert result is not None, "Pedido não foi adicionado corretamente."

    cursor.close()
    conn.close()


# Função para testar o relacionamento entre Customer e Order (OneToMany)
def test_customer_relationship():
    conn = get_connection()
    cursor = conn.cursor()

    customer = Customer(name="Bob Smith")
    customer.save()

    order1 = Order(customer_id=1, product_name="Product B", quantity=1)
    order1.save()
    order2 = Order(customer_id=1, product_name="Product C", quantity=5)
    order2.save()

    cursor.execute("SELECT * FROM orders WHERE customer_id = 1;")
    result = cursor.fetchall()
    assert len(result) == 2, "O relacionamento OneToMany não foi estabelecido corretamente."

    cursor.close()
    conn.close()


# Função para testar a exclusão de um cliente e o comportamento ON DELETE CASCADE
def test_delete_customer_with_orders():
    conn = get_connection()
    cursor = conn.cursor()

    customer = Customer(name="Carlos")
    customer.save()

    order1 = Order(customer_id=1, product_name="Product D", quantity=3)
    order1.save()
    order2 = Order(customer_id=1, product_name="Product E", quantity=4)
    order2.save()

    # Deletar cliente
    cursor.execute("DELETE FROM customers WHERE id = 1;")
    conn.commit()

    cursor.execute("SELECT * FROM orders WHERE customer_id = 1;")
    result = cursor.fetchall()
    assert len(result) == 0, "A exclusão do cliente não apagou os pedidos (ON DELETE CASCADE)."

    cursor.close()
    conn.close()


# Função para testar o relacionamento Many-to-Many
def test_add_many_to_many_relationship():
    conn = get_connection()
    cursor = conn.cursor()

    class Category(BaseModel):
        _table_name = "categories"
        id = Field("SERIAL", primary_key=True)
        name = Field("VARCHAR(100)")

    # Relacionamento Many-to-Many entre Customer e Category
    class CustomerCategory(BaseModel):
        _table_name = "customer_category"
        customer_id = ForeignKey(Customer)
        category_id = ForeignKey(Category)

    Category.create_table()
    CustomerCategory.create_table()

    customer = Customer(name="Alice")
    customer.save()

    category = Category(name="Technology")
    category.save()

    # Criar o relacionamento Many-to-Many
    customer_category = CustomerCategory(customer_id=1, category_id=1)
    customer_category.save()

    cursor.execute("SELECT * FROM customer_category WHERE customer_id = 1 AND category_id = 1;")
    result = cursor.fetchone()
    assert result is not None, "Relacionamento Many-to-Many não foi estabelecido corretamente."

    cursor.close()
    conn.close()


# Função principal para rodar os testes
def run_tests():
    setup_database()

    try:
        test_create_customer_table()
        test_create_order_table()
        test_add_customer()
        test_add_order()
        test_customer_relationship()
        test_delete_customer_with_orders()
        test_add_many_to_many_relationship()
        print("Todos os testes passaram com sucesso!")
    except AssertionError as e:
        print(f"Erro nos testes: {e}")
    finally:
        cleanup_database()


if __name__ == "__main__":
    run_tests()
