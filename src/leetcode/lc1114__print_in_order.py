from threading import Condition


class Foo:
    def __init__(self):
        print(0)
        self.state = 0
        self.state_cv = Condition()

    def first(self, printFirst: "Callable[[], None]") -> None:
        # printFirst() outputs "first". Do not change or remove this line.
        printFirst()

        with self.state_cv:
            self.state += 1
            self.state_cv.notify_all()

    def second(self, printSecond: "Callable[[], None]") -> None:
        with self.state_cv:
            self.state_cv.wait_for(lambda: self.state >= 1)

        # printSecond() outputs "second". Do not change or remove this line.
        printSecond()

        with self.state_cv:
            self.state += 1
            self.state_cv.notify_all()

    def third(self, printThird: "Callable[[], None]") -> None:
        with self.state_cv:
            self.state_cv.wait_for(lambda: self.state >= 2)

        # printThird() outputs "third". Do not change or remove this line.
        printThird()


if __name__ == "__main__":
    foo = Foo()
    from concurrent.futures import ThreadPoolExecutor

    messages = {
        i: func for i, func in enumerate([foo.first, foo.second, foo.third], 1)
    }

    with ThreadPoolExecutor() as tpe:
        futures = [
            tpe.submit(func, lambda: print(f"printing {i}"))
            for i, func in messages.items()
        ]

        for future in futures:
            future.result(1)
