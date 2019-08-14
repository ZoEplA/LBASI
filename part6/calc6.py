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

    ##########################################################
    # Parser / Interpreter code                              #
    ##########################################################

class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
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
        """Return an INTEGER token value."""
        token = self.current_token
        if token.type == INTEGER:
            self.next(INTEGER)
            return token.value
        elif token.type == LPAREN:
            self.next(LPAREN)
            result = self.expr()
            self.next(RPAREN)
            return result
        
    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        result = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.next(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.next(DIV)
                result = result // self.factor()

        return result

    # Responsible for discovering and interpreting data structures
    def expr(self):
        """Arithmetic expression parser / interpreter.

        calc>  (14 + 2) * 3 - 6 / 2
        45

        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER
        """
        result = self.factor()
        # Support multiple additions and subtractions: setp 1 (Loop to get the symbol)
        while self.current_token.type in (PLUS, MINUS, MUL, DIV):
            token = self.current_token
            if token.type == PLUS:
                self.next(PLUS)
                result = result + self.term()
            elif token.type == MINUS:
                self.next(MINUS)
                result = result - self.term()
            if token.type == MUL:
                self.next(MUL)
                result = result * self.term()
            elif token.type == DIV:
                self.next(DIV)
                result = result // self.term()
        return result

def main():
    while True:
        try:
            text = raw_input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.expr()
        print(result)

if __name__ == '__main__':
    main()