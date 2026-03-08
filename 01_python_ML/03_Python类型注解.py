from typing import List
from typing import Dict


def fun(a):
    print(a)


def fun(a: str):
    print(a)


# 案例：一个简单的数学函数
def add(a: int, b: int) -> int:
    """
    计算两个整数的和。
    """
    return a + b

a = "2"
add(a, 2)

# 案例：一个处理字符串的函数
def greet(name: str) -> str:
    """
    生成一个问候语。
    """
    return f"Hello, {name}!"


# 案例：一个不返回任何值的函数，返回值注解为 None
def log_message(message: str) -> None:
    """
    打印一条日志信息。
    """
    print(f"日志: {message}")


# 调用函数
print(f"10 + 5 = {add(10, 5)}")
print(greet("Alice"))
log_message("程序已启动。")

# 在 Python 3.9+ 中，可以直接使用 list[str]
names: list[str] = ["Alice", "Bob", "Charlie"]


add("1", "2")