# Tea

Tea is small and simple.
It was crafted for reading, extending and maintaining.
The interpreter is still in early-alpha and can only run ASTs.

## A leafy example
```tea
// leafy.tea
import std.io;

func sayHello(name: string): string {
    return "Hello, %s!" % name;
}

func main(args: list) {
    io.println("You called", args.join(","));
    io.print("Please enter your name: ");
    var name = io.readLine();
    sayHello(name);
}
```
