# ![Tea](https://cloud.githubusercontent.com/assets/3391295/14614369/372907fa-05a1-11e6-8272-956c2cc447cb.png)

[![Build Status](https://travis-ci.org/TeaLang/tea.svg?branch=master)](https://travis-ci.org/TeaLang/tea)

Tea is small, code written in Tea simple and short.
It was crafted for reading, extending and maintaining.

## A leafy example
```tea
// leafy.tea
import std.io;

func greet(greeting, name: string): string {
    return "%s, %s!" % [greeting, name];
}

io.println("You called", args.join(","));
io.print("Please enter your name: ");
var name: string = io.readln();

if (length(trim(name)) == 0) {
    io.println("Ok, I won't greet you :(");
} else {
    io.print("How many times? ");
    var times: int = io.readln();
    
    for (i: int = 0; i < times; i += 1) {
        print(greet("Hello", name));
    }
}
```
