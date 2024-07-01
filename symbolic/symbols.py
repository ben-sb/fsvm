from typing import Self

class Symbol:
    def __init__(self) -> None:
        pass

    def copy(self) -> Self:
        raise Exception('Symbol is abstract')

class IdentifierSymbol(Symbol):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def copy(self) -> Self:
        return IdentifierSymbol(self.name)

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
class StringSymbol(IdentifierSymbol):
    def __init__(self, name: str, len: int | None) -> None:
        super().__init__(name)
        self.len = len if len is not None else IdentifierSymbol(f'{self.name}_len')

    def copy(self) -> Self:
        return StringSymbol(self.name, self.len)

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return str(self)
    
class UnaryExpressionSymbol(Symbol):
    def __init__(self, operator: str, argument: Symbol | int) -> None:
        super().__init__()
        self.operator = operator
        self.argument = argument

    def copy(self) -> Self:
        arg = self.argument.copy() if isinstance(self.argument, Symbol) else self.argument
        return UnaryExpressionSymbol(self.operator, arg)

    def __str__(self) -> str:
        return f'({self.operator}{str(self.argument)})'
    
    def __repr__(self) -> str:
        return str(self)

class BinaryExpressionSymbol(Symbol):
    def __init__(self, operator: str, left: Symbol | int, right: Symbol | int) -> None:
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right

    def copy(self) -> Self:
        left = self.left.copy() if isinstance(self.left, Symbol) else self.left
        right = self.right.copy() if isinstance(self.right, Symbol) else self.right
        return BinaryExpressionSymbol(self.operator, left, right)

    def __str__(self) -> str:
        return f'({str(self.left)} {self.operator} {str(self.right)})'
    
    def __repr__(self) -> str:
        return str(self)

class MemberExpressionSymbol(Symbol):
    def __init__(self, object: Symbol, property: Symbol | int) -> None:
        super().__init__()
        self.object = object
        self.property = property

    def copy(self) -> Self:
        obj = self.object.copy()
        prop = self.property.copy() if isinstance(self.property, Symbol) else self.property
        return MemberExpressionSymbol(obj, prop)

    def __str__(self) -> str:
        return f'{str(self.object)}[{str(self.property)}]'
    
    def __repr__(self) -> str:
        return str(self)
