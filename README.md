# mejsel 0.1
A collection of Facebook Chisel commands.

## Available commands
Mejsel contains commands for visualizing CGRects and CGPoints, and for
printing information about the current method when stopped in a method preamble. The following sections explain the commands briefly; for more information, use the `help <command_name>` command in lldb.

### Visualization commands

| Command | Description |
|---------------|:-----------------|
| `vrect <rect> <refview>` | Visualizes (using a red-bordered view) a CGRect whose coordinates are specified in the coordinate space of `refview`.
| `vpoint <point> <refview>`| Similar to `vrect`but takes a CGPoint as the first parameter instead of a CGRect.

**Note:** The arguments passed to the above commands are required to be wrapped in quotes if they contain whitespace. If you don't wrap them, you'll probably be presented with a bunch of lldb error messages.

### Preamble commands
The following commands only work as expected when stopped in a method preamble, e.g. a Framework method that you don't have the symbols for.

| Command | Description |
|---------------|:-----------------|
| `parg [--all] [<index>] [<type>]` | Prints method arguments. Tries to guess the argument type based on the method signature. **Note:** Does not work very well for structs.
| `pself`| Prints the value of `self`.
| `psel` | Prints the value of the `sel` argument, i.e. the selector for the current method.

## Caveats

These commands haven't been used for very long which means that there are a lot of situations in which they don't work. If you happen to find a certain incantation of a command that always results in errors, please report an issue and I'll have a look.
