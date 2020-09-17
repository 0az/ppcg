from threading import Condition
from typing import Callable


class FooBar:
    def __init__(self, n):
        self.n = n
        self.state = 0
        self.state_cv = Condition()

    def foo(self, printFoo: Callable[[], None]) -> None:

        for i in range(self.n):

            with self.state_cv:
                self.state_cv.wait_for(lambda: self.state >= 2 * i, 1)

                # printFoo() outputs "foo". Do not change or remove this line.
                printFoo()

                self.state += 1
                self.state_cv.notify_all()

    def bar(self, printBar: Callable[[], None]) -> None:

        for i in range(self.n):

            with self.state_cv:
                self.state_cv.wait_for(lambda: self.state >= 2 * i + 1, 1)

                # printBar() outputs "bar". Do not change or remove this line.
                printBar()

                self.state += 1
                self.state_cv.notify_all()


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
