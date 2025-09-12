# Lox Interpreter

A complete implementation of the Lox programming language interpreter in Python, following Robert Nystrom's "Crafting Interpreters" book.

## Features

- **Complete Language Implementation**: Full scanner, parser, resolver, and interpreter
- **Dynamic Typing**: Variables can hold values of any type
- **Control Flow**: if/else statements, while loops, and for loops
- **Functions**: First-class functions with lexical scoping and closures
- **Classes**: Object-oriented programming with inheritance
- **Built-in Functions**: Native functions like `clock()` for system time

## Language Features

### Data Types
- **Booleans**: `true` and `false`
- **Numbers**: Double-precision floating point
- **Strings**: Double-quoted string literals
- **Nil**: `nil` represents "no value"

### Variables and Assignment
```lox
var name = "Alice";
var age = 25;
var isStudent = true;
```

### Control Flow
```lox
if (condition) {
    // do something
} else {
    // do something else
}

while (condition) {
    // loop body
}

for (var i = 0; i < 10; i = i + 1) {
    // loop body
}
```

### Functions
```lox
fun greet(name) {
    return "Hello, " + name + "!";
}

print greet("World");
```

### Classes and Inheritance
```lox
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

var dog = Dog("Buddy");
dog.speak(); // "Buddy barks"
```

## Usage

### Running from Command Line
```bash
python lox_interpreter.py [script.lox]
```

### Interactive REPL
```bash
python lox_interpreter.py
```
Type `exit` to quit the REPL.

### Programmatic Usage
```python
from lox_interpreter import Lox

# Run Lox code
source_code = """
    var message = "Hello, World!";
    print message;
"""
Lox.run(source_code)
```

## Example Programs

### Fibonacci Calculator
```lox
fun fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 2) + fibonacci(n - 1);
}

print "Fibonacci(10) = " + fibonacci(10);
```

### Class Example with Inheritance
```lox
class Vehicle {
    init(brand) {
        this.brand = brand;
    }
    
    info() {
        print "This is a " + this.brand;
    }
}

class Car < Vehicle {
    init(brand, model) {
        super.init(brand);
        this.model = model;
    }
    
    info() {
        super.info();
        print "Model: " + this.model;
    }
}

var car = Car("Toyota", "Camry");
car.info();
```

## Architecture

The interpreter consists of several key components:

1. **Scanner**: Tokenizes the source code
2. **Parser**: Builds an Abstract Syntax Tree (AST)
3. **Resolver**: Performs semantic analysis and variable resolution
4. **Interpreter**: Executes the AST using the visitor pattern

## Error Handling

The interpreter provides comprehensive error reporting for:
- Lexical errors (invalid characters)
- Syntax errors (malformed expressions)
- Runtime errors (type mismatches, undefined variables)
- Semantic errors (invalid variable access)

## Requirements

- Python 3.8+
- No external dependencies required

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/lox-interpreter.git
cd lox-interpreter
```

2. Make the script executable (optional):
```bash
chmod +x lox_interpreter.py
```

3. Run the interpreter:
```bash
python lox_interpreter.py
```

## Testing

The interpreter includes built-in tests that demonstrate various language features. Run the script without arguments to see test examples in action.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Based on "Crafting Interpreters" by Robert Nystrom
- Implements the complete Lox language specification
- Thanks to the programming language implementation community

## Learn More

For a detailed explanation of how interpreters work and the theory behind this implementation, check out the excellent book "Crafting Interpreters" at [craftinginterpreters.com](https://craftinginterpreters.com/).
