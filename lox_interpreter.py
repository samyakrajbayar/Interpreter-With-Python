#!/usr/bin/env python3
"""
Complete Lox Interpreter Implementation
Based on "Crafting Interpreters" by Robert Nystrom
"""

import sys
from enum import Enum, auto
from typing import Any, List, Optional, Dict, Callable
from dataclasses import dataclass
import time

# ==================== TOKEN TYPES AND TOKENS ====================

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    
    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    
    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int
    
    def __str__(self):
        return f"{self.type.name} {self.lexeme} {self.literal}"

# ==================== LEXICAL ERRORS ====================

class LoxError(Exception):
    pass

class LoxRuntimeError(LoxError):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)

class LoxReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value

# ==================== SCANNER ====================

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }
    
    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def scan_token(self):
        c = self.advance()
        
        match c:
            case '(':
                self.add_token(TokenType.LEFT_PAREN)
            case ')':
                self.add_token(TokenType.RIGHT_PAREN)
            case '{':
                self.add_token(TokenType.LEFT_BRACE)
            case '}':
                self.add_token(TokenType.RIGHT_BRACE)
            case ',':
                self.add_token(TokenType.COMMA)
            case '.':
                self.add_token(TokenType.DOT)
            case '-':
                self.add_token(TokenType.MINUS)
            case '+':
                self.add_token(TokenType.PLUS)
            case ';':
                self.add_token(TokenType.SEMICOLON)
            case '*':
                self.add_token(TokenType.STAR)
            case '!':
                self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    # Comment goes until end of line
                    while self.peek() != '\n' and not self.is_at_end():
                        self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                # Ignore whitespace
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _:
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    Lox.error(self.line, f"Unexpected character: {c}")
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]
    
    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            Lox.error(self.line, "Unterminated string.")
            return
        
        # Closing "
        self.advance()
        
        # Trim quotes
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        
        # Look for fractional part
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the .
            self.advance()
            
            while self.is_digit(self.peek()):
                self.advance()
        
        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)
    
    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'
    
    def is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'
    
    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)
    
    def add_token(self, token_type: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

# ==================== ABSTRACT SYNTAX TREE ====================

class Expr:
    pass

@dataclass(eq=False)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass(eq=False)
class Grouping(Expr):
    expression: Expr

@dataclass(eq=False)
class Literal(Expr):
    value: Any

@dataclass(eq=False)
class Unary(Expr):
    operator: Token
    right: Expr

@dataclass(eq=False)
class Variable(Expr):
    name: Token

@dataclass(eq=False)
class Assign(Expr):
    name: Token
    value: Expr

@dataclass(eq=False)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass(eq=False)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr]

@dataclass(eq=False)
class Get(Expr):
    object: Expr
    name: Token

@dataclass(eq=False)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

@dataclass(eq=False)
class This(Expr):
    keyword: Token

@dataclass(eq=False)
class Super(Expr):
    keyword: Token
    method: Token

class Stmt:
    pass

@dataclass(eq=False)
class Expression(Stmt):
    expression: Expr

@dataclass(eq=False)
class Print(Stmt):
    expression: Expr

@dataclass(eq=False)
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]

@dataclass(eq=False)
class Block(Stmt):
    statements: List[Stmt]

@dataclass(eq=False)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]

@dataclass(eq=False)
class While(Stmt):
    condition: Expr
    body: Stmt

@dataclass(eq=False)
class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]

@dataclass(eq=False)
class Return(Stmt):
    keyword: Token
    value: Optional[Expr]

@dataclass(eq=False)
class Class(Stmt):
    name: Token
    superclass: Optional[Variable]
    methods: List[Function]

# ==================== PARSER ====================

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> List[Stmt]:
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt:
                statements.append(stmt)
        return statements
    
    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
    
    def class_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected class name.")
        
        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expected superclass name.")
            superclass = Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expected '{' before class body.")
        
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after class body.")
        return Class(name, superclass, methods)
    
    def function(self, kind: str) -> Function:
        name = self.consume(TokenType.IDENTIFIER, f"Expected {kind} name.")
        
        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body.")
        body = self.block()
        
        return Function(name, parameters, body)
    
    def var_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name.")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Var(name, initializer)
    
    def statement(self) -> Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        
        return self.expression_statement()
    
    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")
        
        # Initializer
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        # Condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")
        
        # Increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")
        
        body = self.statement()
        
        # Desugar for loop into while loop
        if increment:
            body = Block([body, Expression(increment)])
        
        if not condition:
            condition = Literal(True)
        body = While(condition, body)
        
        if initializer:
            body = Block([initializer, body])
        
        return body
    
    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after if condition.")
        
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return If(condition, then_branch, else_branch)
    
    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")
        return Print(value)
    
    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return Return(keyword, value)
    
    def while_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        body = self.statement()
        
        return While(condition, body)
    
    def block(self) -> List[Stmt]:
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements
    
    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return Expression(expr)
    
    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr = self.or_()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def or_(self) -> Expr:
        expr = self.and_()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def and_(self) -> Expr:
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expr:
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expr:
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def term(self) -> Expr:
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self) -> Expr:
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")
        return Call(callee, paren, arguments)
    
    def primary(self) -> Expr:
        if self.match(TokenType.TRUE):
            return Literal(True)
        
        if self.match(TokenType.FALSE):
            return Literal(False)
        
        if self.match(TokenType.NIL):
            return Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expected '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expected superclass method name.")
            return Super(keyword, method)
        
        if self.match(TokenType.THIS):
            return This(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expected expression.")
    
    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str) -> ParseError:
        Lox.error_token(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.CLASS, TokenType.FUN, TokenType.VAR,
                TokenType.FOR, TokenType.IF, TokenType.WHILE,
                TokenType.PRINT, TokenType.RETURN
            ]:
                return
            
            self.advance()

# ==================== ENVIRONMENT ====================

class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.enclosing = enclosing
        self.values: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        self.values[name] = value
    
    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing:
            return self.enclosing.get(name)
        
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
        
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).values[name]
    
    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name.lexeme] = value
    
    def ancestor(self, distance: int) -> 'Environment':
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

# ==================== CALLABLE OBJECTS ====================

class LoxCallable:
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        raise NotImplementedError
    
    def arity(self) -> int:
        raise NotImplementedError

class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturnException as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def bind(self, instance: 'LoxInstance') -> 'LoxFunction':
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)
    
    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"

class LoxClass(LoxCallable):
    def __init__(self, name: str, superclass: Optional['LoxClass'], methods: Dict[str, LoxFunction]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        instance = LoxInstance(self)
        
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer:
            return initializer.arity()
        return 0
    
    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass:
            return self.superclass.find_method(name)
        
        return None
    
    def __str__(self):
        return self.name

class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: Dict[str, Any] = {}
    
    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)
        
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value
    
    def __str__(self):
        return f"{self.klass.name} instance"

# Native Functions
class ClockFunction(LoxCallable):
    def arity(self) -> int:
        return 0
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        return time.time()
    
    def __str__(self):
        return "<native fn>"

# ==================== RESOLVER ====================

from enum import Enum

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

class Resolver:
    def __init__(self, interpreter: 'Interpreter'):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
    
    def resolve_statements(self, statements: List[Stmt]):
        for statement in statements:
            self.resolve_stmt(statement)
    
    def resolve_stmt(self, stmt: Stmt):
        if isinstance(stmt, Block):
            self.begin_scope()
            self.resolve_statements(stmt.statements)
            self.end_scope()
        elif isinstance(stmt, Class):
            enclosing_class = self.current_class
            self.current_class = ClassType.CLASS
            
            self.declare(stmt.name)
            self.define(stmt.name)
            
            if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
                Lox.error_token(stmt.superclass.name, "A class can't inherit from itself.")
            
            if stmt.superclass:
                self.current_class = ClassType.SUBCLASS
                self.resolve_expr(stmt.superclass)
                
                self.begin_scope()
                self.scopes[-1]["super"] = True
            
            self.begin_scope()
            self.scopes[-1]["this"] = True
            
            for method in stmt.methods:
                declaration = FunctionType.METHOD
                if method.name.lexeme == "init":
                    declaration = FunctionType.INITIALIZER
                self.resolve_function(method, declaration)
            
            self.end_scope()
            
            if stmt.superclass:
                self.end_scope()
            
            self.current_class = enclosing_class
        elif isinstance(stmt, Expression):
            self.resolve_expr(stmt.expression)
        elif isinstance(stmt, Function):
            self.declare(stmt.name)
            self.define(stmt.name)
            
            self.resolve_function(stmt, FunctionType.FUNCTION)
        elif isinstance(stmt, If):
            self.resolve_expr(stmt.condition)
            self.resolve_stmt(stmt.then_branch)
            if stmt.else_branch:
                self.resolve_stmt(stmt.else_branch)
        elif isinstance(stmt, Print):
            self.resolve_expr(stmt.expression)
        elif isinstance(stmt, Return):
            if self.current_function == FunctionType.NONE:
                Lox.error_token(stmt.keyword, "Can't return from top-level code.")
            
            if stmt.value:
                if self.current_function == FunctionType.INITIALIZER:
                    Lox.error_token(stmt.keyword, "Can't return a value from an initializer.")
                self.resolve_expr(stmt.value)
        elif isinstance(stmt, Var):
            self.declare(stmt.name)
            if stmt.initializer:
                self.resolve_expr(stmt.initializer)
            self.define(stmt.name)
        elif isinstance(stmt, While):
            self.resolve_expr(stmt.condition)
            self.resolve_stmt(stmt.body)
    
    def resolve_expr(self, expr: Expr):
        if isinstance(expr, Assign):
            self.resolve_expr(expr.value)
            self.resolve_local(expr, expr.name)
        elif isinstance(expr, Binary):
            self.resolve_expr(expr.left)
            self.resolve_expr(expr.right)
        elif isinstance(expr, Call):
            self.resolve_expr(expr.callee)
            for argument in expr.arguments:
                self.resolve_expr(argument)
        elif isinstance(expr, Get):
            self.resolve_expr(expr.object)
        elif isinstance(expr, Grouping):
            self.resolve_expr(expr.expression)
        elif isinstance(expr, Literal):
            pass
        elif isinstance(expr, Logical):
            self.resolve_expr(expr.left)
            self.resolve_expr(expr.right)
        elif isinstance(expr, Set):
            self.resolve_expr(expr.value)
            self.resolve_expr(expr.object)
        elif isinstance(expr, Super):
            if self.current_class == ClassType.NONE:
                Lox.error_token(expr.keyword, "Can't use 'super' outside of a class.")
            elif self.current_class != ClassType.SUBCLASS:
                Lox.error_token(expr.keyword, "Can't use 'super' in a class with no superclass.")
            self.resolve_local(expr, expr.keyword)
        elif isinstance(expr, This):
            if self.current_class == ClassType.NONE:
                Lox.error_token(expr.keyword, "Can't use 'this' outside of a class.")
            self.resolve_local(expr, expr.keyword)
        elif isinstance(expr, Unary):
            self.resolve_expr(expr.right)
        elif isinstance(expr, Variable):
            if self.scopes and expr.name.lexeme in self.scopes[-1] and self.scopes[-1][expr.name.lexeme] == False:
                Lox.error_token(expr.name, "Can't read local variable in its own initializer.")
            self.resolve_local(expr, expr.name)
    
    def resolve_function(self, function: Function, func_type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = func_type
        
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve_statements(function.body)
        self.end_scope()
        
        self.current_function = enclosing_function
    
    def begin_scope(self):
        self.scopes.append({})
    
    def end_scope(self):
        self.scopes.pop()
    
    def declare(self, name: Token):
        if not self.scopes:
            return
        
        scope = self.scopes[-1]
        if name.lexeme in scope:
            Lox.error_token(name, "Already a variable with this name in this scope.")
        
        scope[name.lexeme] = False
    
    def define(self, name: Token):
        if not self.scopes:
            return
        
        self.scopes[-1][name.lexeme] = True
    
    def resolve_local(self, expr: Expr, name: Token):
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return

# ==================== INTERPRETER ====================

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals: Dict[Expr, int] = {}
        
        # Define native functions
        self.globals.define("clock", ClockFunction())
    
    def interpret(self, statements: List[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            Lox.runtime_error(error)
    
    def execute(self, stmt: Stmt):
        if isinstance(stmt, Block):
            self.execute_block(stmt.statements, Environment(self.environment))
        elif isinstance(stmt, Class):
            superclass = None
            if stmt.superclass:
                superclass = self.evaluate(stmt.superclass)
                if not isinstance(superclass, LoxClass):
                    raise LoxRuntimeError(stmt.superclass.name, "Superclass must be a class.")
            
            self.environment.define(stmt.name.lexeme, None)
            
            if stmt.superclass:
                self.environment = Environment(self.environment)
                self.environment.define("super", superclass)
            
            methods = {}
            for method in stmt.methods:
                function = LoxFunction(method, self.environment, method.name.lexeme == "init")
                methods[method.name.lexeme] = function
            
            klass = LoxClass(stmt.name.lexeme, superclass, methods)
            
            if superclass:
                self.environment = self.environment.enclosing
            
            self.environment.assign(stmt.name, klass)
        elif isinstance(stmt, Expression):
            self.evaluate(stmt.expression)
        elif isinstance(stmt, Function):
            function = LoxFunction(stmt, self.environment, False)
            self.environment.define(stmt.name.lexeme, function)
        elif isinstance(stmt, If):
            if self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.then_branch)
            elif stmt.else_branch:
                self.execute(stmt.else_branch)
        elif isinstance(stmt, Print):
            value = self.evaluate(stmt.expression)
            print(self.stringify(value))
        elif isinstance(stmt, Return):
            value = None
            if stmt.value:
                value = self.evaluate(stmt.value)
            
            raise LoxReturnException(value)
        elif isinstance(stmt, Var):
            value = None
            if stmt.initializer:
                value = self.evaluate(stmt.initializer)
            
            self.environment.define(stmt.name.lexeme, value)
        elif isinstance(stmt, While):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
    
    def execute_block(self, statements: List[Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth
    
    def evaluate(self, expr: Expr) -> Any:
        if isinstance(expr, Assign):
            value = self.evaluate(expr.value)
            
            distance = self.locals.get(expr)
            if distance is not None:
                self.environment.assign_at(distance, expr.name, value)
            else:
                self.globals.assign(expr.name, value)
            
            return value
        elif isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            
            if expr.operator.type == TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            elif expr.operator.type == TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero.")
                return float(left) / float(right)
            elif expr.operator.type == TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            elif expr.operator.type == TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return self.stringify(left) + self.stringify(right)
                raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
            elif expr.operator.type == TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return float(left) > float(right)
            elif expr.operator.type == TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) >= float(right)
            elif expr.operator.type == TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) < float(right)
            elif expr.operator.type == TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return float(left) <= float(right)
            elif expr.operator.type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr.operator.type == TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
        elif isinstance(expr, Call):
            callee = self.evaluate(expr.callee)
            
            arguments = []
            for argument in expr.arguments:
                arguments.append(self.evaluate(argument))
            
            if not isinstance(callee, LoxCallable):
                raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
            
            if len(arguments) != callee.arity():
                raise LoxRuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
            
            return callee.call(self, arguments)
        elif isinstance(expr, Get):
            obj = self.evaluate(expr.object)
            if isinstance(obj, LoxInstance):
                return obj.get(expr.name)
            
            raise LoxRuntimeError(expr.name, "Only instances have properties.")
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Logical):
            left = self.evaluate(expr.left)
            
            if expr.operator.type == TokenType.OR:
                if self.is_truthy(left):
                    return left
            else:
                if not self.is_truthy(left):
                    return left
            
            return self.evaluate(expr.right)
        elif isinstance(expr, Set):
            obj = self.evaluate(expr.object)
            
            if not isinstance(obj, LoxInstance):
                raise LoxRuntimeError(expr.name, "Only instances have fields.")
            
            value = self.evaluate(expr.value)
            obj.set(expr.name, value)
            return value
        elif isinstance(expr, Super):
            distance = self.locals[expr]
            superclass = self.environment.get_at(distance, "super")
            
            obj = self.environment.get_at(distance - 1, "this")
            
            method = superclass.find_method(expr.method.lexeme)
            
            if not method:
                raise LoxRuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")
            
            return method.bind(obj)
        elif isinstance(expr, This):
            return self.lookup_variable(expr.keyword, expr)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)
            
            if expr.operator.type == TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(right)
            elif expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)
        elif isinstance(expr, Variable):
            return self.lookup_variable(expr.name, expr)
        
        return None
    
    def lookup_variable(self, name: Token, expr: Expr) -> Any:
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")
    
    def is_truthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True
    
    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        return a == b
    
    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"
        
        if isinstance(obj, bool):
            return str(obj).lower()
        
        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        
        return str(obj)

# ==================== MAIN LOX CLASS ====================

class Lox:
    had_error = False
    had_runtime_error = False
    interpreter = Interpreter()
    
    @classmethod
    def main(cls, args: List[str]):
        if len(args) > 1:
            print("Usage: lox [script]")
            sys.exit(64)
        elif len(args) == 1:
            cls.run_file(args[0])
        else:
            cls.run_prompt()
    
    @classmethod
    def run_file(cls, path: str):
        try:
            with open(path, 'r') as file:
                source = file.read()
            cls.run(source)
            
            if cls.had_error:
                sys.exit(65)
            if cls.had_runtime_error:
                sys.exit(70)
        except FileNotFoundError:
            print(f"Could not read file '{path}'.")
            sys.exit(74)
    
    @classmethod
    def run_prompt(cls):
        print("Lox Interpreter - Type 'exit' to quit")
        while True:
            try:
                line = input("> ")
                if line.strip() == "exit":
                    break
                cls.run(line)
                cls.had_error = False
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
    
    @classmethod
    def run(cls, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens)
        statements = parser.parse()
        
        if cls.had_error:
            return
        
        resolver = Resolver(cls.interpreter)
        resolver.resolve_statements(statements)
        
        if cls.had_error:
            return
        
        cls.interpreter.interpret(statements)
    
    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)
    
    @classmethod
    def error_token(cls, token: Token, message: str):
        if token.type == TokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, f" at '{token.lexeme}'", message)
    
    @classmethod
    def runtime_error(cls, error: LoxRuntimeError):
        print(f"[line {error.token.line}] Runtime Error: {error.message}")
        cls.had_runtime_error = True
    
    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True

# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example Lox programs to test various features
    
    # Test 1: Basic expressions and variables
    print("=== Test 1: Basic Expressions ===")
    test1 = """
    var a = 10;
    var b = 20;
    print a + b;
    print a * b;
    print "Hello, " + "World!";
    """
    Lox.run(test1)
    
    # Test 2: Control flow
    print("\n=== Test 2: Control Flow ===")
    test2 = """
    var x = 5;
    if (x > 3) {
        print "x is greater than 3";
    } else {
        print "x is not greater than 3";
    }
    
    var i = 0;
    while (i < 3) {
        print "Loop iteration: " + i;
        i = i + 1;
    }
    """
    Lox.run(test2)
    
    # Test 3: Functions
    print("\n=== Test 3: Functions ===")
    test3 = """
    fun greet(name) {
        return "Hello, " + name + "!";
    }
    
    fun fibonacci(n) {
        if (n <= 1) return n;
        return fibonacci(n - 2) + fibonacci(n - 1);
    }
    
    print greet("Alice");
    print "Fibonacci(6) = " + fibonacci(6);
    """
    Lox.run(test3)
    
    # Test 4: Classes and inheritance
    print("\n=== Test 4: Classes ===")
    test4 = """
    class Animal {
        init(name) {
            this.name = name;
        }
        
        speak() {
            print this.name + " makes a sound";
        }
    }
    
    class Dog < Animal {
        speak() {
            print this.name + " barks";
        }
    }
    
    var animal = Animal("Generic");
    var dog = Dog("Buddy");
    
    animal.speak();
    dog.speak();
    """
    Lox.run(test4)
    
    print("\nLox Interpreter Test Complete!")
    
    # Uncomment to run as interactive REPL
    # Lox.main(sys.argv[1:])
