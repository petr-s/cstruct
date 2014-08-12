CStruct
=======

Using struct module alone in project with a lot of/complicated structures might be messy.
Therefore here is the library which will make your life much easier.

```python
class Foo(Struct):
	x = Int()
	greetings = String(5)

foo = Foo()
foo.read(file)

foo.set(42, "hello")
foo.write(file)
```