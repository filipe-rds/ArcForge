from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, Any
from datetime import datetime
# -----------------------------------------------------------------------------
# Design Pattern: Template Method
# A classe Field define a sequência de passos (métodos) para a construção da
# definição SQL e validação de valores, permitindo que as subclasses especializem
# partes específicas do comportamento.
# -----------------------------------------------------------------------------
# Design Pattern: Strategy
# O método validate na classe Field atua como um contexto no padrão Strategy. Ele define a estrutura geral
# da validação, mas permite que as subclasses forneçam implementações específicas para a validação de valores.
# -----------------------------------------------------------------------------
class ValidationError(ValueError):
    """Exceção personalizada para erros de validação de campos."""
    def __init__(self, message: str, field_type: str, value: Any):
        super().__init__(f"{message} [Campo: {field_type}, Valor: {value}]")
        self.field_type = field_type
        self.value = value


class Field(ABC):
    """Classe abstrata base para definição de campos com validação integrada.

    Padrão: Template Method - define métodos comuns e deixa implementações específicas para subclasses.
    """
    def __init__(
            self,
            primary_key: bool = False,
            unique: bool = False,
            nullable: bool = True,
            default: Optional[Union[str, int, float, bool]] = None,
            foreign_key: Optional[Tuple[str, str]] = None
    ):
        if foreign_key and (not isinstance(foreign_key, tuple) or len(foreign_key) != 2):
            raise ValueError("foreign_key deve ser uma tupla (tabela, coluna)")
        self.primary_key = primary_key
        self.unique = unique or primary_key
        self.nullable = nullable if not primary_key else False
        self.default = default
        self.foreign_key = foreign_key

    @property
    @abstractmethod
    def field_type(self) -> str:
        """Tipo do campo (implementado por subclasses)."""
        pass

    @property
    def expected_type(self) -> type:
        """Tipo Python esperado (implementado por subclasses)."""
        return type(None)  # Permite None por padrão

    def _format_default(self) -> str:
        """Formata valores padrão para sintaxe SQL."""
        if self.default is None:
            return ''
        if isinstance(self.default, str) and not self.default.startswith("'"):
            return f"'{self.default}'"
        if isinstance(self.default, bool):
            return 'TRUE' if self.default else 'FALSE'
        return str(self.default)

    def to_sql(self) -> str:
        """Constrói a definição SQL do campo.

        Padrão: Template Method - define a sequência de passos para construir a string SQL.
        """
        parts = [self.field_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if self.unique:
            parts.append("UNIQUE")
        if not self.nullable:
            parts.append("NOT NULL")
        if self.default is not None:
            parts.append(f"DEFAULT {self._format_default()}")
        if self.foreign_key:
            parts.append(f"REFERENCES {self.foreign_key[0]}({self.foreign_key[1]})")
        return ' '.join(parts)

    def validate(self, value: Any) -> None:
        """Valida o valor de acordo com as regras do campo.

        Padrão: Strategy Pattern - permite que subclasses ajustem a validação conforme necessário.
        """
        if value is None:
            if not self.nullable:
                raise ValidationError("Campo não pode ser nulo", self.field_type, value)
            return
        if not isinstance(value, self.expected_type):
            raise ValidationError(
                f"Tipo inválido. Esperado: {self.expected_type.__name__}",
                self.field_type,
                value
            )

    def __str__(self):
        return f"{self.__class__.__name__}({vars(self)})"


# -----------------------------------------------------------------------------
# Implementações concretas dos campos
# Cada campo utiliza o Template Method para especializar o comportamento de validação
# e geração de SQL.
# -----------------------------------------------------------------------------

class IntegerField(Field):
    """Campo para números inteiros."""
    @property
    def field_type(self) -> str:
        # Se for chave primária, utiliza SERIAL para auto-incremento
        return "SERIAL" if self.primary_key else "INTEGER"

    @property
    def expected_type(self) -> type:
        return int



class RealField(Field):
    """Campo para números reais (precisão simples)."""
    @property
    def field_type(self) -> str:
        return "REAL"

    @property
    def expected_type(self) -> type:
        return float


class CharField(Field):
    """Campo para strings com tamanho máximo."""
    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    @property
    def field_type(self) -> str:
        return f"VARCHAR({self.max_length})"

    @property
    def expected_type(self) -> type:
        return str

    def validate(self, value: str) -> None:
        # Chama a validação da superclasse (Template Method)
        super().validate(value)
        if value is not None and len(value) > self.max_length:
            raise ValidationError(
                f"Tamanho máximo excedido ({self.max_length} caracteres)",
                self.field_type,
                value
            )


class DateField(Field):
    """Campo para datas."""

    @property
    def field_type(self) -> str:
        return "DATE"

    @property
    def expected_type(self) -> type:
        return str  # Aceita strings no formato date

    def validate(self, value: str) -> None:
        super().validate(value)

        if not value:
            raise ValidationError("Data não pode ser vazia", self.field_type, value)

        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Data deve estar no formato válido YYYY-MM-DD", self.field_type, value)



class BooleanField(Field):
    """Campo para valores booleanos."""
    @property
    def field_type(self) -> str:
        return "BOOLEAN"

    @property
    def expected_type(self) -> type:
        return bool


__all__ = ["ValidationError", "Field", "IntegerField", "RealField", "CharField","DateField", "BooleanField",]