# Addition, subtraction, multiplication and division of two items
# Token types
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF'
)
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(
            type = self.type,
            value = repr(self.value)
        )
    
    def __repr__(self):
        return self.__str__()
    
class Lexer(object):
    def __init__(self,text):
        self.text = text
        self.pos = 0
        self.current_token = None
        self.current_char = self.text[self.pos]
        # print("init......")

    ##########################################################
    # Lexer code                                             #
    ##########################################################
    def error(self):
        raise Exception('Error parsing input')

    def advance(self):
        """Advance the 'pos' pointer and set the 'current_char' variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
    # Lexical analyzer (also known as scanner or tokenizer)

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())
            
            if self.current_char == "+":
                token = Token(PLUS, self.current_char)
                self.advance()
                return Token(PLUS, '+')
            
            if self.current_char == "-":
                token = Token(MINUS, self.current_char)
                self.advance()
                return Token(MINUS, '-')
            
            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)


###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token token from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def next(self, token_type):
    # compare the current token type with the passed token
    # type and if they match then get the "next" current token
    # and assign the next token to the self.current_token,
    # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """factor : (PLUS | MINUS) factor | INTEGER | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == PLUS:
            self.next(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.next(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.next(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.next(LPAREN)
            node = self.expr()
            self.next(RPAREN)
            return node
        
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.next(MUL)
            elif token.type == DIV:
                self.next(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER | LPAREN expr RPAREN
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.next(PLUS)
            elif token.type == MINUS:
                self.next(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()
    

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        # print(type(node))
        # print(type(node).__name__)
        visitor = getattr(self, method_name, self.generic_visit)
        # print("visitor(node) = " + str(visitor(node)))
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


def main():
    while True:
        try:
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)

if __name__ == '__main__':
    main()