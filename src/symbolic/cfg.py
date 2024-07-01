class Node:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.next = None

    def add_statement(self, statement: str) -> None:
        self.statements.append(statement)

    def codegen(self) -> list[str]:
        stmts = self.statements.copy()
        if self.next:
            stmts += self.next.codegen()

        return stmts

class ConditionalNode:
    def __init__(self, test: str, consequent: Node, alternate: Node) -> None:
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    def codegen(self) -> str:
        # only need to handle if statements for this simple case
        consequent = self.consequent.codegen()
        alternate = self.alternate.codegen()
        return [
            f'if ({self.test}) {{',
            *['\t' + line for line in consequent],
            '} else {',
            *['\t' + line for line in alternate],
            '}'
        ]