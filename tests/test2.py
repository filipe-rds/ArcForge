import psycopg2

try:
    connection = psycopg2.connect(
        host="localhost",
        dbname="test",
        user="postgres",
        password="ifpb",
        port=5432
    )
    print("Conexão bem-sucedida!")
    connection.close()
except Exception as e:
    print(f"Erro ao conectar ao PostgreSQL: {e}")
