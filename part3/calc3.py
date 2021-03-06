
# Token types
INTEGER, PLUS, MINUS, EOF = 'INTEGER', 'PLUS', 'MINUS', 'EOF'

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
    
class Interpreter(object):
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
                token = Token(INTEGER, self.integer())
                return token
            
            if self.current_char == "+":
                token = Token(PLUS, self.current_char)
                self.advance()
                return token
            
            if self.current_char == "-":
                token = Token(MINUS, self.current_char)
                self.advance()
                return token

            self.error()

        return Token(EOF, None)

    ##########################################################
    # Parser / Interpreter code                              #
    ##########################################################

    def next(self, token_type):
    # compare the current token type with the passed token
    # type and if they match then get the "next" current token
    # and assign the next token to the self.current_token,
    # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def get_integer(self):
        """Return an INTEGER token value."""
        token = self.current_token
        self.next(INTEGER)
        return token.value

    # Responsible for discovering and interpreting data structures
    def expr(self):
        self.current_token = self.get_next_token()

        result = self.get_integer()
        # Support multiple additions and subtractions: setp 1 (Loop to get the symbol)
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.next(PLUS)
                result = result + self.get_integer()
            elif token.type == MINUS:
                self.next(MINUS)
                result = result - self.get_integer()
            
        return result

def main():
    while True:
        try:
            text = raw_input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        result = interpreter.expr()
        print(result)

if __name__ == '__main__':
    main()