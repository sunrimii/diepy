class A:
    def __init__(self):
        self.b = 1

if hasattr(A(), "b"):
    print(1)