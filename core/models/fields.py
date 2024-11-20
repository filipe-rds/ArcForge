import re
from datetime import datetime


class Field:
    """Classe base para todos os tipos de campo"""

    def __init__(self, field_type, **kwargs):
        self.field_type = field_type
        self.options = kwargs  # Usado para campos que necessitam de parâmetros adicionais

    def validate(self, value):
        """Método de validação genérico"""
        raise NotImplementedError("O método 'validate' precisa ser implementado para cada campo")


class Integer(Field):
    def __init__(self, **kwargs):
        super().__init__('INTEGER', **kwargs)

    def validate(self, value):
        """Valida se o valor é um inteiro"""
        if not isinstance(value, int):
            raise ValueError(f"O valor {value} não é um número inteiro.")
        return True


class String(Field):
    def __init__(self, max_length=None, **kwargs):
        super().__init__('VARCHAR', **kwargs)
        self.max_length = max_length  # Parâmetro opcional de tamanho máximo

    def validate(self, value):
        """Valida se o valor é uma string e não excede o tamanho máximo"""
        if not isinstance(value, str):
            raise ValueError(f"O valor {value} não é uma string.")
        if self.max_length and len(value) > self.max_length:
            raise ValueError(f"A string {value} excede o tamanho máximo de {self.max_length}.")
        return True


class Boolean(Field):
    def __init__(self, **kwargs):
        super().__init__('BOOLEAN', **kwargs)

    def validate(self, value):
        """Valida se o valor é um booleano"""
        if not isinstance(value, bool):
            raise ValueError(f"O valor {value} não é um booleano.")
        return True


class ForeignKey(Field):
    def __init__(self, ref_table, ref_column, **kwargs):
        super().__init__('INTEGER', **kwargs)  # Usando 'INTEGER' para FK por padrão
        self.ref_table = ref_table
        self.ref_column = ref_column

    def validate(self, value):
        """Valida se o valor é um inteiro válido para a chave estrangeira"""
        if not isinstance(value, int):
            raise ValueError(f"O valor {value} não é um inteiro válido para a chave estrangeira.")
        return True


class Float(Field):
    def __init__(self, **kwargs):
        super().__init__('REAL', **kwargs)

    def validate(self, value):
        """Valida se o valor é um número flutuante"""
        if not isinstance(value, float):
            raise ValueError(f"O valor {value} não é um número flutuante.")
        return True


class Date(Field):
    def __init__(self, **kwargs):
        super().__init__('DATE', **kwargs)

    def validate(self, value):
        """Valida se o valor é uma data válida"""
        if isinstance(value, datetime):
            return True
        try:
            # Verifica se a string pode ser convertida para uma data
            datetime.strptime(value, "%Y-%m-%d")
            return True
        except ValueError:
            raise ValueError(f"O valor {value} não é uma data válida. O formato esperado é YYYY-MM-DD.")


class DateTime(Field):
    def __init__(self, **kwargs):
        super().__init__('TIMESTAMP', **kwargs)

    def validate(self, value):
        """Valida se o valor é um datetime válido"""
        if isinstance(value, datetime):
            return True
        try:
            # Verifica se a string pode ser convertida para um datetime
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            raise ValueError(f"O valor {value} não é um datetime válido. O formato esperado é YYYY-MM-DD HH:MM:SS.")


class Text(Field):
    def __init__(self, **kwargs):
        super().__init__('TEXT', **kwargs)

    def validate(self, value):
        """Valida se o valor é uma string"""
        if not isinstance(value, str):
            raise ValueError(f"O valor {value} não é uma string.")
        return True


class Decimal(Field):
    def __init__(self, precision=10, scale=2, **kwargs):
        super().__init__('DECIMAL', **kwargs)
        self.precision = precision  # Precisão do número decimal
        self.scale = scale  # Escala do número decimal

    def validate(self, value):
        """Valida se o valor é decimal e atende à precisão e escala definidas"""
        if not isinstance(value, (float, int)):
            raise ValueError(f"O valor {value} não é um número decimal.")

        # Valida a precisão e escala (exemplo básico de validação)
        value_str = str(value)
        if '.' in value_str:
            decimal_part = value_str.split('.')[1]
            if len(decimal_part) > self.scale:
                raise ValueError(f"O valor {value} excede a escala de {self.scale} casas decimais.")
        if len(value_str.split('.')[0]) > self.precision:
            raise ValueError(f"O valor {value} excede a precisão de {self.precision} dígitos.")
        return True


class PrimaryKey(Integer):
    """Representa uma chave primária"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # Herda de Integer, que é o tipo padrão para PK
        self.primary_key = True  # Indica que é uma chave primária

    def validate(self, value):
        """Validar chave primária"""
        # A validação de chave primária pode ser mais relacionada ao banco de dados,
        # mas podemos verificar se o valor é um inteiro e não nulo.
        if value is None:
            raise ValueError("A chave primária não pode ser None.")
        return super().validate(value)


class Unique(String):
    """Representa um campo com restrição UNIQUE"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unique = True  # Restrições de unicidade

    def validate(self, value):
        """Valida o campo único"""
        # A validação de unicidade pode ser realizada diretamente no banco de dados
        # Aqui, fazemos uma verificação genérica
        if value is None:
            raise ValueError("O valor único não pode ser None.")
        return super().validate(value)
