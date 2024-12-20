import psycopg

try:
    connection = psycopg.connect(
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
