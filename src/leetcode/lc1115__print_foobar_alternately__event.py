from threading import Event
from typing import Callable


class FooBar:
    def __init__(self, n):
        self.n = n
        self.event_foo = Event()
        self.event_bar = Event()
        self.event_foo.set()

    def foo(self, printFoo: Callable[[], None]) -> None:

        for i in range(self.n):

            self.event_foo.wait()

            # printFoo() outputs "foo". Do not change or remove this line.
            printFoo()

            self.event_foo.clear()
            self.event_bar.set()

    def bar(self, printBar: Callable[[], None]) -> None:

        for i in range(self.n):

            self.event_bar.wait()

            # printBar() outputs "bar". Do not change or remove this line.
            printBar()

            self.event_bar.clear()
            self.event_foo.set()


if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor

    foobar = FooBar(2)

    foo = foobar.foo
    bar = foobar.bar

    with ThreadPoolExecutor() as tpe:
        futures = {
            "bar": tpe.submit(bar, lambda: print("bar")),
            "foo": tpe.submit(foo, lambda: print("foo")),
        }

        for name, future in futures.items():
            future.result(2)
