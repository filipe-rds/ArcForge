# ArchForge - Uso de Mapeamentos de Modelos

Este documento explica como utilizar os mapeamentos de modelos no **ArchForge**, incluindo como definir campos, configurar chaves primárias e estrangeiras, aplicar validações, e realizar operações de consulta.

## Definindo um Modelo

Para definir um modelo, você deve criar uma classe que herda de `BaseModel` e usar a anotação `@Table` para associar a classe a uma tabela do banco de dados.

### Exemplo básico de modelo:

```python
from core.models.base_model import BaseModel, Table
from core.models.fields import Integer, String

@Table(name="users")
class User(BaseModel):
    id = Integer()  # Campo de tipo Integer
    name = String(max_length=255)  # Campo de tipo String com limite de caracteres
```

O campo `id` será mapeado para um campo numérico e `name` para uma string com tamanho máximo de 255 caracteres.

## Tipos de Campos

O **ArchForge** fornece diversos tipos de campos para mapeamento de dados. A seguir, estão os tipos de campos suportados:

### 1. `Integer`

Usado para campos que armazenam números inteiros.

```python
id = Integer()
```

### 2. `String`

Usado para campos que armazenam strings. Você pode definir o tamanho máximo da string com o parâmetro `max_length`.

```python
name = String(max_length=255)
```

### 3. `Boolean`

Usado para campos que armazenam valores booleanos.

```python
is_active = Boolean()
```

### 4. `ForeignKey`

Usado para criar relações de chave estrangeira. Você deve especificar a tabela de referência e a coluna de referência.

```python
user_id = ForeignKey(ref_table="users", ref_column="id")
```

### 5. `Float`

Usado para campos que armazenam números flutuantes.

```python
price = Float()
```

### 6. `Date`

Usado para campos que armazenam datas no formato `YYYY-MM-DD`.

```python
birth_date = Date()
```

### 7. `DateTime`

Usado para campos que armazenam datas e horas no formato `YYYY-MM-DD HH:MM:SS`.

```python
created_at = DateTime()
```

### 8. `Text`

Usado para campos que armazenam textos longos.

```python
description = Text()
```

### 9. `Decimal`

Usado para campos que armazenam números decimais com precisão e escala.

```python
price = Decimal(precision=10, scale=2)
```

## Definindo Chaves Primárias e Únicas

### Chave Primária

Você pode definir uma chave primária para um campo usando a classe `PrimaryKey`. Por padrão, a chave primária é um campo do tipo `Integer`.

```python
id = PrimaryKey()
```

### Campo Único

Para garantir que um campo tenha valores únicos, você pode usar a classe `Unique`.

```python
email = Unique()
```

## Exemplos Práticos de Modelos

### Exemplo 1: Modelo de Usuário

```python
from core.models.base_model import BaseModel, Table
from core.models.fields import PrimaryKey, String, Integer

@Table(name="users")
class User(BaseModel):
    id = PrimaryKey()
    name = String(max_length=255)
    age = Integer()
```

Neste exemplo, o campo `id` é uma chave primária, e `name` é um campo de texto limitado a 255 caracteres, enquanto `age` é um campo de inteiro.

### Exemplo 2: Modelo de Post com Chave Estrangeira

```python
from core.models.base_model import BaseModel, Table
from core.models.fields import PrimaryKey, String, ForeignKey, Integer

@Table(name="posts")
class Post(BaseModel):
    id = PrimaryKey()
    title = String(max_length=255)
    user_id = ForeignKey(ref_table="users", ref_column="id")
```

Neste exemplo, `user_id` é uma chave estrangeira que se relaciona com a tabela `users`, referenciando a coluna `id`.

## Validações de Campos

As validações de campos são realizadas automaticamente ao salvar os dados usando o método `save()` do modelo. O framework verificará se os dados atendem aos requisitos definidos para cada campo. Por exemplo:

### Exemplo de validação de tipo:

```python
user = User(name="Alice", age="30")  # A idade está incorreta, pois deve ser um número inteiro
user.save()  # Isso levantará um erro de validação
```

Se um campo `String` for definido com um `max_length`, o framework também irá validar o comprimento da string:

```python
name = String(max_length=10)
user = User(name="A very long name")
user.save()  # Isso levantará um erro de validação, pois o nome excede o limite de 10 caracteres
```

## Operações CRUD

Após definir o modelo e mapeá-lo para a tabela do banco de dados, você pode realizar operações CRUD (Create, Read, Update, Delete).

### Criar um Novo Registro

```python
user = User(name="Alice", age=30)
user.save()  # Salva o novo usuário no banco de dados
```

### Consultar Registros

Os métodos `all`, `find`, e `find_one` podem ser usados para consultar registros no banco de dados.

#### Método `all()`

Este método recupera todos os registros da tabela associada ao modelo.

```python
users = User.all()  # Retorna todos os usuários
for user in users:
    print(user.name, user.age)
```

#### Método `find(**filters)`

Este método permite que você recupere registros filtrados por campos específicos. Os filtros são passados como argumentos nomeados.

```python
users = User.find(name="Alice")  # Retorna usuários com o nome "Alice"
for user in users:
    print(user.name, user.age)
```

#### Método `find_one(**filters)`

Este método recupera um único registro que corresponde aos filtros especificados. Caso nenhum registro seja encontrado, ele retorna `None`.

```python
user = User.find_one(id=1)  # Retorna o usuário com id 1
if user:
    print(user.name, user.age)
else:
    print("Usuário não encontrado.")
```

### Atualizar um Registro

```python
user = User.get(id=1)  # Supondo que o ID 1 exista
user.name = "Bob"
user.save()  # Atualiza o usuário no banco de dados
```

### Deletar um Registro

```python
user = User.get(id=1)  # Supondo que o ID 1 exista
user.delete()  # Deleta o usuário
```

## Conclusão

O **ArchForge** oferece uma maneira simples e eficiente de mapear modelos para tabelas de banco de dados, com suporte a validações, chaves estrangeiras, chaves primárias e outros tipos de campos. Além disso, ele facilita a consulta aos registros usando os métodos `all`, `find`, e `find_one`, permitindo uma interação intuitiva com o banco de dados.

Se precisar de mais detalhes ou exemplos, consulte o código-fonte ou abra uma issue no repositório!
