import unittest


class LexerTestCase(unittest.TestCase):
    def makeLexer(self, text):
        from calc16 import Lexer
        lexer = Lexer(text)
        return lexer

    def test_tokens(self):
        from calc16 import TokenType
        records = (
            ('234', TokenType.INTEGER_CONST, 234),
            ('3.14', TokenType.REAL_CONST, 3.14),
            ('*', TokenType.MUL, '*'),
            ('DIV', TokenType.INTEGER_DIV, 'DIV'),
            ('/', TokenType.FLOAT_DIV, '/'),
            ('+', TokenType.PLUS, '+'),
            ('-', TokenType.MINUS, '-'),
            ('(', TokenType.LPAREN, '('),
            (')', TokenType.RPAREN, ')'),
            (':=', TokenType.ASSIGN, ':='),
            ('.', TokenType.DOT, '.'),
            ('number', TokenType.ID, 'number'),
            (';', TokenType.SEMI, ';'),
            ('BEGIN', TokenType.BEGIN, 'BEGIN'),
            ('END', TokenType.END, 'END'),
            ('PROCEDURE', TokenType.PROCEDURE, 'PROCEDURE'),
        )
        for text, tok_type, tok_val in records:
            lexer = self.makeLexer(text)
            token = lexer.get_next_token()
            self.assertEqual(token.type, tok_type)
            self.assertEqual(token.value, tok_val)

    def test_lexer_exception(self):
        from calc16 import LexerError
        lexer = self.makeLexer('<')
        with self.assertRaises(LexerError):
            lexer.get_next_token()


class ParserTestCase(unittest.TestCase):
    def makeParser(self, text):
        from calc16 import Lexer, Parser
        lexer = Lexer(text)
        parser = Parser(lexer)
        return parser

    def test_expression_invalid_syntax_01(self):
        from calc16 import ParserError, ErrorCode
        parser = self.makeParser(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
               a := 10 * ;  {Invalid syntax}
            END.
            """
        )
        with self.assertRaises(ParserError) as cm:
            parser.parse()
        the_exception = cm.exception
        self.assertEqual(the_exception.error_code, ErrorCode.UNEXPECTED_TOKEN)
        self.assertEqual(the_exception.token.value, ';')
        self.assertEqual(the_exception.token.lineno, 6)

    def test_expression_invalid_syntax_02(self):
        from calc16 import ParserError, ErrorCode
        parser = self.makeParser(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
               a := 1 (1 + 2); {Invalid syntax}
            END.
            """
        )
        with self.assertRaises(ParserError) as cm:
            parser.parse()
        the_exception = cm.exception
        self.assertEqual(the_exception.error_code, ErrorCode.UNEXPECTED_TOKEN)
        self.assertEqual(the_exception.token.value, '(')
        self.assertEqual(the_exception.token.lineno, 6)

    def test_maximum_one_VAR_block_is_allowed(self):
        from calc16 import ParserError, ErrorCode
        # zero VARs
        parser = self.makeParser(
            """
            PROGRAM Test;
            BEGIN
            END.
            """
        )
        parser.parse()

        # one VAR
        parser = self.makeParser(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
            END.
            """
        )
        parser.parse()

        parser = self.makeParser(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            VAR
                b : INTEGER;
            BEGIN
               a := 5;
               b := a + 10;
            END.
            """
        )
        with self.assertRaises(ParserError) as cm:
            parser.parse()
        the_exception = cm.exception
        self.assertEqual(the_exception.error_code, ErrorCode.UNEXPECTED_TOKEN)
        self.assertEqual(the_exception.token.value, 'VAR')
        self.assertEqual(the_exception.token.lineno, 5)  # second VAR


class SemanticAnalyzerTestCase(unittest.TestCase):
    def runSemanticAnalyzer(self, text):
        from calc16 import Lexer, Parser, SemanticAnalyzer
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)
        return semantic_analyzer

    def test_semantic_duplicate_id_error(self):
        from calc16 import SemanticError, ErrorCode
        with self.assertRaises(SemanticError) as cm:
            self.runSemanticAnalyzer(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
                a : REAL;  {Duplicate identifier}
            BEGIN
               a := 5;
            END.
            """
            )
        the_exception = cm.exception
        self.assertEqual(the_exception.error_code, ErrorCode.DUPLICATE_ID)
        self.assertEqual(the_exception.token.value, 'a')
        self.assertEqual(the_exception.token.lineno, 5)

    def test_semantic_id_not_found_error(self):
        from calc16 import SemanticError, ErrorCode
        with self.assertRaises(SemanticError) as cm:
            self.runSemanticAnalyzer(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
               a := 5 + b;
            END.
            """
            )
        the_exception = cm.exception
        self.assertEqual(the_exception.error_code, ErrorCode.ID_NOT_FOUND)
        self.assertEqual(the_exception.token.value, 'b')


class InterpreterTestCase(unittest.TestCase):
    def makeInterpreter(self, text):
        from calc16 import Lexer, Parser, SemanticAnalyzer, Interpreter
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.visit(tree)

        interpreter = Interpreter(tree)
        return interpreter

    def test_integer_arithmetic_expressions(self):
        for expr, result in (
            ('3', 3),
            ('2 + 7 * 4', 30),
            ('7 - 8 DIV 4', 5),
            ('14 + 2 * 3 - 6 DIV 2', 17),
            ('7 + 3 * (10 DIV (12 DIV (3 + 1) - 1))', 22),
            ('7 + 3 * (10 DIV (12 DIV (3 + 1) - 1)) DIV (2 + 3) - 5 - 3 + (8)', 10),
            ('7 + (((3 + 2)))', 12),
            ('- 3', -3),
            ('+ 3', 3),
            ('5 - - - + - 3', 8),
            ('5 - - - + - (3 + 4) - +2', 10),
        ):
            interpreter = self.makeInterpreter(
                """PROGRAM Test;
                   VAR
                       a : INTEGER;
                   BEGIN
                       a := %s
                   END.
                """ % expr
            )
            interpreter.interpret()
            globals = interpreter.GLOBAL_MEMORY
            self.assertEqual(globals['a'], result)

    def test_float_arithmetic_expressions(self):
        for expr, result in (
            ('3.14', 3.14),
            ('2.14 + 7 * 4', 30.14),
            ('7.14 - 8 / 4', 5.14),
        ):
            interpreter = self.makeInterpreter(
                """PROGRAM Test;
                   VAR
                       a : REAL;
                   BEGIN
                       a := %s
                   END.
                """ % expr
            )
            interpreter.interpret()
            globals = interpreter.GLOBAL_MEMORY
            self.assertEqual(globals['a'], result)

    def test_procedure_call(self):
        text = """\
program Main;

procedure Alpha(a : integer; b : integer);
var x : integer;
begin
   x := (a + b ) * 2;
end;

begin { Main }

   Alpha(3 + 5, 7);

end.  { Main }
"""
        interpreter = self.makeInterpreter(text)
        interpreter.interpret()

    def test_program(self):
        text = """\
PROGRAM Part12;
VAR
   number : INTEGER;
   a, b   : INTEGER;
   y      : REAL;

PROCEDURE P1;
VAR
   a : REAL;
   k : INTEGER;
   PROCEDURE P2;
   VAR
      a, z : INTEGER;
   BEGIN {P2}
      z := 777;
   END;  {P2}
BEGIN {P1}

END;  {P1}

BEGIN {Part12}
   number := 2;
   a := number ;
   b := 10 * a + 10 * number DIV 4;
   y := 20 / 7 + 3.14
END.  {Part12}
"""
        interpreter = self.makeInterpreter(text)
        interpreter.interpret()

        globals = interpreter.GLOBAL_MEMORY
        self.assertEqual(len(globals.keys()), 4)
        self.assertEqual(globals['number'], 2)
        self.assertEqual(globals['a'], 2)
        self.assertEqual(globals['b'], 25)
        self.assertAlmostEqual(globals['y'], float(20) / 7 + 3.14)  # 5.9971...


if __name__ == '__main__':
    unittest.main()