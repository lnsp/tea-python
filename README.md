# ![Tea](https://cloud.githubusercontent.com/assets/3391295/23532925/c1c217d2-ffae-11e6-8f4d-2ffe792f82f7.png)

[![Build Status](https://travis-ci.org/TeaLang/tea.svg?branch=master)](https://travis-ci.org/TeaLang/tea)

**Careful! This project is deprecated and no longer in development. Refer to the Go implementation for a more recent version.**

Code written in Tea is simple and small, even Tea itself is short (less than 3000 lines of code).
It was crafted for reading, extending and maintaining.

## How about a little taste of Tea?
```tea
// tasty.tea
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
