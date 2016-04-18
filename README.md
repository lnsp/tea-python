# ![Tea](https://cloud.githubusercontent.com/assets/3391295/14614369/372907fa-05a1-11e6-8272-956c2cc447cb.png)


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
