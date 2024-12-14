import psycopg2
from psycopg2 import sql
from arcforge.core.db.config import *
from arcforge.core.model.model import *


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados e a criação de tabelas."""
    def __init__(self):
        self._conexao = None
        self.set_conexao()

    def set_conexao(self):
        """Estabelece uma conexão com o banco de dados, se ainda não estiver conectada."""
        if self._conexao is None:
            self._conexao = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )

    def get_conexao(self):
        """Retorna a conexão ativa com o banco de dados."""
        self.set_conexao()
        return self._conexao

    def create_table(self, base_model):
        """Cria a tabela no banco de dados com base no modelo fornecido."""

        fields = base_model._generate_fields()
        try:
            create_table_query = sql.SQL("""
                CREATE TABLE IF NOT EXISTS {table} (
                    {fields}
                );
            """).format(
                table=sql.Identifier(base_model._table_name),
                fields=sql.SQL(fields)
            )

            with self._conexao.cursor() as cursor:
                cursor.execute(create_table_query)
                self._conexao.commit()

            # Configurar relacionamentos Many-to-Many
            #base_model._create_relationships()
        except psycopg2.Error as e:
            print(f"Erro ao criar a tabela {base_model._table_name}: {e}")



    def save(self, model_instance):
            """Salva ou atualiza a instância no banco de dados."""
            fields = []
            values = []
            placeholders = []

            # Extrai os atributos e valores do modelo
            for attr, value in model_instance.__dict__.items():
                if attr in model_instance.__class__.__dict__:
                    fields.append(attr)
                    values.append(value)
                    placeholders.append(sql.Placeholder())
            
             # Tratar relacionamentos
            unique_field = None  # Para identificar um campo único, se existir
            processed_fields = set(fields)
            for rel in model_instance.__class__._relationships:
                if rel['field_name'] not in processed_fields:
                    rel_value = getattr(model_instance, rel['field_name'], None)
                    if rel_value is not None:
                        fields.append(rel['field_name'])
                        values.append(rel_value)
                        placeholders.append(sql.Placeholder())
                        # Se o relacionamento for One-to-One, definimos o campo como único
                        if rel.get("unique", False):
                            unique_field = rel['field_name']

            # Se não houver unique_field, evite usar ON CONFLICT
            conflict_clause = sql.SQL("") if unique_field is None else sql.SQL("ON CONFLICT ({unique_field}) DO NOTHING").format(
                unique_field=sql.Identifier(unique_field)
            )

            query = sql.SQL("""
                INSERT INTO {table} ({fields})
                VALUES ({placeholders})
                {conflict_clause}
                RETURNING id;
            """).format(
                table=sql.Identifier(model_instance._table_name),
                fields=sql.SQL(", ").join(map(sql.Identifier, fields)),
                placeholders=sql.SQL(", ").join(placeholders),
                conflict_clause=conflict_clause,
            )

            try:
                with self._conexao.cursor() as cursor:
                    cursor.execute(query, values)
                    self._conexao.commit()
                    model_instance.id = cursor.fetchone()[0]
                    print(f"Instância de {model_instance.__class__.__name__} salva com sucesso.")
            except psycopg2.Error as e:
                self._conexao.rollback()
                print(f"Erro ao salvar a instância {model_instance._table_name}: {e}")

   # Função que não vai instanciar objetos
   # Função mais livre para realizar diversos tipos de consulta
    def query_sql(self, query, params): 
        """Executa uma consulta no banco de dados."""
        #self.set_conexao()
        query = sql.SQL(query)
        #.format(table=sql.Identifier(model._table_name))
        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, params)
                listaDeRetornos = cursor.fetchall()
                return listaDeRetornos
                #return self.transformarArrayEmObjetos(model,listaDeRetornos)
                    
        except psycopg2.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None


    # Função mais restrita para realizar consultas
    # Sempre retorna todos os campos da tabela
    def query(self, table_name: Model, filters=None, joins=None):
        """
        Executa uma consulta no banco de dados com base em filtros e joins.
        
        :param table_name: Nome da tabela base para a consulta.
        :param filters: Dicionário de filtros, onde a chave é a coluna e o valor é o valor a ser filtrado.
        :param joins: Lista de tuplas para joins no formato:
                    [("tabela_join", "coluna_base", "coluna_join")]
        :return: Lista de resultados ou None em caso de erro.
        """
        try:
            # Construção da consulta base
            base_query = sql.SQL("SELECT {table}.* FROM {table}").format(
                fields=sql.SQL("*"),  # Aqui você pode escolher os campos que deseja selecionar
                table=sql.Identifier(table_name._table_name)
            )
            
            # Adicionar joins se existirem
            if joins:
                join_clauses = []
                for join_table, base_column, join_column in joins:
                    join_clause = sql.SQL(
                        " JOIN {join_table} ON {base_table}.{base_column} = {join_table}.{join_column}"
                    ).format(
                        join_table=sql.Identifier(join_table),
                        base_table=sql.Identifier(table_name._table_name),  # Correção: a tabela base é usada corretamente
                        base_column=sql.Identifier(base_column),
                        join_column=sql.Identifier(join_column),
                    )
                    join_clauses.append(join_clause)
                
                base_query += sql.SQL(" ").join(join_clauses)

            # Adicionar filtros se existirem
            if filters:
                filter_clauses = []
                filter_values = []
                for column, value in filters.items():
                    # Aqui, separa a tabela e a coluna para aplicar corretamente
                    table, column_name = column.split(".")  # Separar tabela e coluna no filtro
                    filter_clauses.append(sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(table),
                        column=sql.Identifier(column_name)
                    ))
                    filter_values.append(value)
                
                # Adiciona a cláusula WHERE
                where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(filter_clauses)
                base_query += where_clause
            else:
                filter_values = []

            # Executar a consulta
            with self._conexao.cursor() as cursor:
                # Aqui, o psycopg2 já lida com a interpolação de valores
                cursor.execute(base_query, filter_values)
                return cursor.fetchall()
        
        except psycopg2.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None






    # Função que vai instanciar 1 ou mais objetos
    # O ID sempre tem que ser o primeiro atributo
    def transformarArrayEmObjetos(self, model: Model, listaDeRetornos):
        listaDeObjetos = []
        # Percorrer cada retorno da lista
        for retorno in listaDeRetornos:
            id = retorno[0]
            resultado = self.buscarPeloId(model,id)
            objetoGerado = self.transformarArrayEmUmObjeto(model,resultado)
            listaDeObjetos.append(objetoGerado)
        return listaDeObjetos
    
    # Retorna um array com os registros da consulta pelo ID

    def buscarPeloId(self, model: Model, id):
        """Busca uma instância pelo ID."""
        query = f"SELECT * FROM {model._table_name} WHERE id = %s;"
        params = [id]
        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, params)
                objeto = cursor.fetchall()
                    
        except psycopg2.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None

        return objeto

    # Uso interno do framework

    def transformarArrayEmUmObjeto(self, model: Model, listaDeRetorno):
        # Criando uma única instância de model
        classe = model  
        objeto = model()
        
        # Verificando se a lista de retornos não está vazia
        if listaDeRetorno:
            # Pegando o primeiro retorno
            retorno = listaDeRetorno[0]
            
            # Obtendo os atributos da instância
            atributos = list(vars(classe).keys())
            
            # Atribuindo os valores aos atributos
            for i, atributo in enumerate(atributos[2:-1], start=0):  # Ignorando os dois primeiros atributos
                setattr(objeto, atributo, retorno[i])
        
        # Retornando a única instância criada
        return objeto
    
    # def buscaPorColuna(self, model: Model, coluna, valor):
    #     """Busca uma instância pelo valor de uma coluna."""
    #     query = f"SELECT * FROM {model._table_name} WHERE {coluna} = %s;"
    #     params = [valor]
    #     try:
    #         with self._conexao.cursor() as cursor:
    #             cursor.execute(query, params)
    #             return cursor.fetchall()
    #     except psycopg2.Error as e:
    #         print(f"Erro ao executar a consulta: {e}")
    #         return None












    