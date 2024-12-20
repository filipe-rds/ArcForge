import psycopg
from psycopg import sql
from datetime import datetime
from arcforge.core.db.config import *
from arcforge.core.model.model import *


class DatabaseConnection:
    """Gerencia a conexão com o banco de dados e a criação de tabelas."""
    _instance = None  # Atributo estático para armazenar a única instância

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._conexao = None
            self.set_conexao()
            self._initialized = True  # Evita reinicialização na mesma instância

    def set_conexao(self):
        """Estabelece uma conexão com o banco de dados, se ainda não estiver conectada."""
        if self._conexao is None:
            self._conexao = psycopg.connect(
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
        except psycopg.Error as e:
            print(f"Erro ao criar a tabela {base_model._table_name}: {e}")



    def save(self, model_instance):
            
            classe = model_instance.__class__

            # Validação de tipos
            try:
                self.validationType(classe, model_instance)
            except (TypeError) as e:
                raise TypeError(f"Erro ao validar data para o campo': {str(e)}")

            
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
            except psycopg.Error as e:
                self._conexao.rollback()
                print(f"Erro ao salvar a instância {model_instance._table_name}: {e}")

    def update(self, model_instance):
        """Função auxiliar para realizar a atualização de um registro no banco de dados."""

        classe = model_instance.__class__

        # Validação de tipos
        try:
            self.validationType(classe, model_instance)
        except (TypeError) as e:
            raise TypeError(f"Erro ao validar data para o campo': {str(e)}")

        model_id = model_instance.id
        # print(model_instance.id)
        if isinstance(model_id, Field):
            model_id = getattr(model_instance, 'id_field', None)

        # print(model_id)
        if not model_id:
            raise ValueError("Não é possível realizar o UPDATE sem um ID válido.")

        fields = []
        values = []
        set_clause = []

        # Extrai os atributos e valores do modelo
        for attr, value in model_instance.__dict__.items():
            if isinstance(value, Field) or attr == "id":
                continue

            fields.append(attr)
            values.append(value)
            set_clause.append(sql.SQL("{} = {}").format(
                sql.Identifier(attr), sql.Placeholder()
            ))

        query = sql.SQL("""
            UPDATE {table}
            SET {set_clause}
            WHERE id = {id}
        """).format(
            table=sql.Identifier(model_instance._table_name),
            set_clause=sql.SQL(", ").join(set_clause),
            id=sql.Placeholder()
        )

        values.append(model_id)

        # # Imprimir a query formatada com valores reais
        # query_string = query.as_string(self._conexao)
        # print("Query com placeholders:", query_string)  # Exibe query com placeholders
        #
        # # Substituir placeholders manualmente para ver a consulta com valores reais
        # final_query = query_string % tuple(values)
        # print("Query final com valores reais:", final_query)

        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, values)
                self._conexao.commit()
                return model_instance
        except psycopg.Error as e:
            self._conexao.rollback()
            print(f"Erro ao atualizar a instância {model_instance._table_name}: {e}")
            return None

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
                    
        except psycopg.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None


    def query(self, base_model, **filters):
        """
        Executa uma consulta no banco de dados com base nos filtros e inferindo os joins automaticamente.
        Inclui depuração para cada etapa da construção da consulta.
        """
        try:
            # Construção da consulta base
            base_query = sql.SQL("SELECT {base_table}.* FROM {base_table}").format(
                base_table=sql.Identifier(base_model._table_name)
            )
            # print(f"Base Query: {base_query.as_string(self._conexao)}")  # Passo 1: Exibir base da query

            # Inferir joins com base nos relacionamentos do modelo
            join_clauses = []
            relationships = base_model._relationships if hasattr(base_model, "_relationships") else []

            # Mapear tabelas já incluídas para evitar joins duplicados
            joined_tables = {base_model._table_name: True}

            for rel in relationships:
                ref_table = rel["ref_table"]
                base_column = rel["field_name"]
                ref_field = "id"  # Campo padrão de referência é "id"

                # Adicionar cláusula de JOIN
                if ref_table not in joined_tables:
                    join_clause = sql.SQL(
                        " JOIN {ref_table} ON {base_table}.{base_column} = {ref_table}.{ref_field}"
                    ).format(
                        ref_table=sql.Identifier(ref_table),
                        base_table=sql.Identifier(base_model._table_name),
                        base_column=sql.Identifier(base_column),
                        ref_field=sql.Identifier(ref_field)
                    )
                    join_clauses.append(join_clause)
                    joined_tables[ref_table] = True
                    # print(f"Adicionando JOIN: {join_clause.as_string(self._conexao)}")

            # Adicionar filtros
            filter_clauses = []
            filter_values = []

            for column, value in filters.items():
                # Suporte a tabela_coluna => converte para tabela.coluna
                if "_" in column and "." not in column:
                    table, column_name = column.split("_", 1)
                    column = f"{table}.{column_name}"

                if "." in column:
                    # Filtro em uma tabela relacionada (tabela.coluna)
                    table, column_name = column.split(".")
                    filter_clauses.append(sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(table),
                        column=sql.Identifier(column_name)
                    ))
                else:
                    # Filtro na tabela principal
                    filter_clauses.append(sql.SQL("{table}.{column} = %s").format(
                        table=sql.Identifier(base_model._table_name),
                        column=sql.Identifier(column)
                    ))
                filter_values.append(value)
                # print(f"Adicionando Filtro: {column} = {value}")

            # Adicionar cláusula WHERE se houver filtros
            if filter_clauses:
                where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(filter_clauses)
            else:
                where_clause = sql.SQL("")
            # print(f"WHERE Clause: {where_clause.as_string(self._conexao)}")

            # Construção final da consulta
            full_query = base_query + sql.SQL(" ").join(join_clauses) + where_clause
            # print(f"Query com Placeholders: {full_query.as_string(self._conexao)}")

            # Substituir placeholders pelos valores reais
            final_query = full_query.as_string(self._conexao) % tuple(filter_values)
            # print(f"Query Final com Valores Reais: {final_query}")

            # Executar a consulta
            with self._conexao.cursor() as cursor:
                cursor.execute(full_query, filter_values)
                return self.transformarArrayEmObjetos(base_model,cursor.fetchall())

        except psycopg.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None

    # Função que vai instanciar 1 ou mais objetos
    # O ID sempre tem que ser o primeiro atributo
    def transformarArrayEmObjetos(self, model, listaDeRetornos):
        listaDeObjetos = []
        # Percorrer cada retorno da lista
        for retorno in listaDeRetornos:
            id = retorno[0]
            resultado = self.buscarPeloId(model,id)
            objetoGerado = self.transformarArrayEmUmObjeto(model,resultado)
            listaDeObjetos.append(objetoGerado)
        return listaDeObjetos
    
    # Retorna um array com os registros da consulta pelo ID

    def buscarPeloId(self, model, id):
        """Busca uma instância pelo ID."""
        query = f"SELECT * FROM {model._table_name} WHERE id = %s;"
        params = [id]
        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, params)
                objeto = cursor.fetchall()
                    
        except psycopg.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None

        return objeto

    def buscaObjeto(self, model, id):
        """Busca uma instância pelo ID."""
        query = f"SELECT * FROM {model._table_name} WHERE id = %s;"
        params = [id]
        try:
            with self._conexao.cursor() as cursor:
                cursor.execute(query, params)
                objeto = cursor.fetchall()

        except psycopg.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return None

        return self.transformarArrayEmUmObjeto(model, objeto)

    # Uso interno do framework

    def transformarArrayEmUmObjeto(self, model, listaDeRetorno):
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
            atributos_validos = atributos[3:]
            tamanho_valido = min(len(atributos_validos), len(retorno))
            for i, atributo in enumerate(atributos_validos[:tamanho_valido]):
                # print(f"Atributo: {atributo}, Valor: {retorno[i]}")
                setattr(objeto, atributo, retorno[i])  # Atribui o valor ao atributo do objeto

        # Retornando a única instância criada
        return objeto


    def validationType(self, model, modelInstance):

        attributes_values = {}
        atributes_values_classe = {}


        for key, value in model.__dict__.items():  # Itera corretamente sobre o dicionário
            if isinstance(value, Field):  # Verifica se o atributo é uma instância de Field
                atributes_values_classe[key] = value.field_type
            elif isinstance(value, Relationship):
                 atributes_values_classe[key] = None
        for key, value in modelInstance.__dict__.items():
                attributes_values[key] = value

        for key, value in attributes_values.items():
                
            if not atributes_values_classe[key] is None:
                fieldInstance = value
                fieldClass = atributes_values_classe[key]

                # Verifica o tipo do campo
                if fieldClass.casefold() == "VARCHAR".casefold() or fieldClass.casefold() == "CHAR".casefold():
                    if not isinstance(fieldInstance, str):
                        raise TypeError(f"O '{key}: {value}' deveria ser uma string, mas é {type(fieldInstance).__name__}.")
                elif fieldClass.casefold() == "INTEGER".casefold():
                    if not isinstance(fieldInstance, int):
                        raise TypeError(f"O '{key}: {value}' deveria ser um inteiro, mas é {type(fieldInstance).__name__}.")
                elif fieldClass.casefold() == "REAL".casefold():
                    if not isinstance(fieldInstance, float):
                        raise TypeError(f"O '{key}: {value}' deveria ser um float, mas é {type(fieldInstance).__name__}.")
                elif fieldClass.casefold() == "BOOLEAN".casefold():
                    if not isinstance(fieldInstance, bool):
                        raise TypeError(f"O '{key}: {value}' deveria ser um booleano, mas é {type(fieldInstance).__name__}.")
                elif fieldClass.casefold() == "DATE".casefold():
                    try:
                        datetime.strptime(fieldInstance, "%Y-%m-%d")
                    except (TypeError):
                            raise TypeError(f"O '{key}: {value}' deveria estar no formato 'YYYY-MM-DD', mas é '{type(fieldInstance).__name__}'.")
                    # else:
                    #     raise ValueError(f"Tipo de campo '{value.field_type}' não suportado para o atributo '{key}'.")
                #else:
                    #raise ValueError(f"O atributo '{key}' não é um campo válido.")
            # except Exception as e:
            #     print(f"Erro na validação: {e}")

