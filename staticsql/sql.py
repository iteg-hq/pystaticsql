import os
import codecs
import re

from .entity import Entity, Attribute

lexer = (
    ("NEWLINE", r"(\n|\r\n|\r)"),
    ("WS", r"([ \t]+)"),

    ("CREATE", r"(create)\b"),
    ("TABLE", r"(table)\b"),
    ("VIEW", r"(view)\b"),
    ("AS", r"(as)\b"),
    ("SELECT", r"(select)\b"),
    ("CONSTRAINT", r"(constraint)\b"),
    ("PRIMARY", r"(primary|\[primary\])\b"),
    ("CLUSTERED", r"(clustered)\b"),
    ("ASC", r"(asc)\b"),
    ("DESC", r"(desc)\b"),
    ("WITH", r"(with)\b"),
    ("FROM", r"(from)\b"),
    ("KEY", r"(key)\b"),
    ("NOT", r"(not)\b"),
    ("NULL", r"(null)\b"),
    ("MAX", r"(max)\b"),

    ("PERIOD", r"(\.)"),
    ("COMMA", r"(,)"),
    ("LPAREN", r"(\()"),
    ("RPAREN", r"(\))"),
    ("STRING", r"('[^']+')"),
    ("DIGITS", r"(\-?\d+)"),
    ("NAME", r"\[([^\]]+)\]"),
    ("NAME", r"([_a-zæøå][_a-zæøå0-9]*)"),
    ("JUNK", r"([^\s]+)"),
)

lexer = [(token_type, re.compile(regex, re.I)) for (token_type, regex) in lexer]

class Token(object):
    def __init__(self, typename, value, line_number, column_number):
        self.typename = typename
        self.value = value
        self.line_number = line_number
        self.column_number = column_number

    def __repr__(self):
        return f"<Token {self.typename} @ [L{self.line_number}:C{self.column_number}] '{self.value}'>"

def gettokens(sql):
    tokens = []
    pos = 0
    line_number = 1
    column_number = 1
    while pos < len(sql):
        for token_type, regex in lexer:
            m = regex.match(sql, pos)
            if m:
                # The start and end of the matching group
                a, b = m.span(1)
                pos = m.end()
                if token_type == "NEWLINE":
                    line_number += 1
                    column_number = 1
                    break
                token = Token(token_type, sql[a:b], line_number, column_number)
                if token.typename != "WS":
                    tokens.append(token)
                column_number += b-a
                break
        else:
            raise Exception("No match", sql[pos:pos+10])
    tokens.append(Token("EOF", pos, line_number, column_number))
    return tokens

class ParseException(Exception):
    pass

class Parser(object):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.pos = 0
        self.tokens = []
        self.table = Entity()
        self.key_items = list()        

    def parse(self, sql):
        self.tokens = gettokens(sql)
        self.skip_until("CREATE")
        self.expect("CREATE")
        if self.lookahead("TABLE"):
            self.create_table()
        if self.lookahead("VIEW"):
            self.create_view()

    def create_table(self):
        self.expect("TABLE")

        self.name()

        # Skip everything until the opening paren of the table definition
        self.skip_until("LPAREN")
        self.expect("LPAREN")

        # Until the next token is not a closing paren
        while not self.lookahead("RPAREN"):
            # If named constraint, discard the name
            if self.lookahead("CONSTRAINT", "NAME"):
                self.expect("CONSTRAINT")
                self.expect("NAME")
                # if primary key, parse it
                if self.lookahead("PRIMARY", "KEY"):
                    self.primary_key()
                # otherwise, skip it
                else:
                    skipped_tokens = list(self.skip_until("COMMA", "RPAREN"))
                    ##at = skipped_tokens[0].line_number
                    ##print(f"Line {at}: Skipped " + " ".join(token.value for token in skipped_tokens))
            # Otherwise, parse it as an attribute
            else:
                self.table.attributes.append(self.attribute())


            next_token = self.get_next_token()
            if not next_token.typename in ("COMMA", "RPAREN"):
                raise ParseException(next_token, "Comma or right paren expected")
            # If the table member ends in a comma, consume it
            if next_token.typename == "COMMA":
                self.expect("COMMA")
        self.expect("RPAREN")

    def name(self):
        # Remember which token we're at before we try anything
        if self.lookahead("NAME", "PERIOD", "NAME"):
            # Try for a dotted name
            self.table.schema = self.expect("NAME").value
            self.expect("PERIOD")
            self.table.name = self.expect("NAME").value
        else:
            # If that fails, try for an unqualified name, defaulting the schema
            self.table.name = self.expect("NAME").value
            self.table.schema = None

    def primary_key(self):
        self.expect("PRIMARY")
        self.expect("KEY")
        self.expect("LPAREN")
        while not self.lookahead("RPAREN"):
            self.key_items.append(self.expect("NAME").value)
            if self.lookahead("ASC") or self.lookahead("DESC"):
                self.skip()
            if self.lookahead("COMMA"):
                self.skip()

    def attribute(self):
        attribute = Attribute()
        attribute.is_nullable = True

        # We expect a name as the 
        if not self.lookahead("NAME"):
            raise ParseException("Expected column name", self.get_next_token())
        attribute.name = self.expect("NAME").value

        # Immediately after the name, we expect a data type
        attribute.data_type = self.data_type()

        # Scan for phrases of interest until we see a terminator
        while not self.lookahead("COMMA") and not self.lookahead("RPAREN"):
            if self.lookahead("NOT", "NULL"):
                self.expect("NOT")
                self.expect("NULL")
                attribute.is_nullable = False
            elif self.lookahead("NULL"):
                self.expect("NULL")
                attribute.is_nullable = True
            elif self.lookahead("PRIMARY", "KEY"):
                self.expect("PRIMARY")
                self.expect("KEY")
                self.key_items = [ attribute.name ]
            else:
                self.skip_any()

        return attribute


    def data_type(self):
        """Parse and return a SQL data type name
        """
        # [typename](
        if self.lookahead("NAME", "LPAREN"):

            typename = self.expect("NAME").value.upper()
            self.expect("LPAREN")
            # MAX)
            if self.lookahead("MAX", "RPAREN"):
                self.expect("MAX")
                self.expect("RPAREN")
                return f"{typename}(MAX)"

            # 123)
            elif self.lookahead("DIGITS", "RPAREN"):
                length = self.expect("DIGITS").value
                self.expect("RPAREN")
                return f"{typename}({length})"

            # 123, 456)
            elif self.lookahead("DIGITS", "COMMA", "DIGITS", "RPAREN"):
                length = self.expect("DIGITS").value
                self.expect("COMMA")
                precision = self.expect("DIGITS").value
                self.expect("RPAREN")
                return f"{typename}({length}, {precision})"
            # Parenthesis contents not valid - error out
            else:
                raise ParseException("Expecting MAX, a umber or two numbers separated by a comma", self.get_next_token())
        # Non-fancy name            
        else:
            return self.expect("NAME").value.upper()

    def create_view(self):
        self.expect("VIEW")
        self.name()
        self.expect("AS")
        while not self.lookahead("EOF"):
            if self.lookahead("NAME", "COMMA"):
                self.table.attributes.append(Attribute(name=self.expect("NAME").value))
                self.expect("COMMA")
            elif self.lookahead("NAME", "FROM"):
                self.table.attributes.append(Attribute(name=self.expect("NAME").value))
                self.expect("FROM")
                break
            elif self.lookahead("NAME", "EOF"):
                self.table.attributes.append(Attribute(name=self.expect("NAME").value))
                break
            else:
                self.skip_any()


    def get_next_token(self, offset=0):
        next_token_pos = self.pos + offset
        if next_token_pos < len(self.tokens):
            return self.tokens[next_token_pos]
        else:
            raise ParseException("Unexpected end of file")

    def lookahead(self, *type_names):
        """Checks that the next tokens are of the types specified
        """
        for offset, type_name in enumerate(type_names):
            try:
                token = self.get_next_token(offset)
            except:
                return False
            if not token or token.typename != type_name:
                return False
        return True

    def expect(self, *token_types):
        """Return the next token if it is of one of the specified types.
        If the token is not of the specified type, 
        """
        token = self.tokens[self.pos]
        if token.typename in token_types:
            self.pos += 1
            return token
        else:
            raise ParseException(token, ", ".join(token_types))

    def skip(self):
        """Skip a single token. The skipped token is returned
        """
        token = self.get_next_token()
        self.pos += 1
        return token


    def skip_any(self):
        """Skip a single token or a single parenthesis.
        The skipped tokens are returned as a list.
        """
        if self.lookahead("LPAREN"):
            return self.skip_paren()
        else:
            return [self.skip()]

    def skip_until(self, *token_types):
        """Skip tokens until the next token is of one of the specified types.
        The skipped tokens are returned as a list.
        """
        tokens = []
        while not self.get_next_token().typename in token_types:
            tokens.extend(self.skip_any())
        return tokens

    def skip_paren(self):
        """Skip a single parenthesis, including the closing parenthesis.
        Nested parentheses are skipped, and the skipped tokens are returned as a list.
        """
        tokens = []
        # skip opening paren
        tokens.append(self.expect("LPAREN"))
        # while we're not at the closing paren
        while not self.lookahead("RPAREN"):
            # if we see a nested paren, skip it
            if self.lookahead("LPAREN"):
                tokens.extend(self.skip_paren())
            # else, skip a single token
            else:
                tokens.append(self.skip())
        # skip the closing paren
        tokens.append(self.expect("RPAREN"))
        return tokens

def parse(sql, unique_tag=None, verbose=False):
    parser = Parser(verbose)
    parser.parse(sql)
    if parser.key_items and unique_tag:
        for i, item in enumerate(parser.key_items):
            parser.table.get_attribute(item).tags.append(f"{unique_tag}:{i+1}")
    return parser.table
