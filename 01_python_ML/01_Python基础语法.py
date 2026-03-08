import sys

# 获取 Python 版本信息
version_info = sys.version_info

print(f"完整的 Python 版本字符串: {sys.version}")
print(f"Python 主要版本号: {version_info.major}")
print(f"Python 次要版本号: {version_info.minor}")
print(f"Python 修订版本号: {version_info.micro}")

# 你也可以使用 f-string 格式化输出
print(f"当前使用的 Python 版本是：{version_info.major}.{version_info.minor}.{version_info.micro}")


# 2. 函数 (Functions)
# 函数是一段可重用的代码，用于执行特定任务。
# 这个函数接受两个整数参数，并返回它们的和。
# 我们使用了类型注解 (Type Hinting) 来提高可读性。
def add_numbers(a: int, b: int) -> int:
    """
    这是一个使用类型注解的函数，用于计算两个整数的和。
    :param a: 第一个整数
    :param b: 第二个整数
    :return: 两个整数的和
    """
    return a + b


result = add_numbers(10, 20)
print(f"使用函数计算 10 + 20 的结果: {result}")
print("-" * 20)


# 3. 类 (Classes)
# 类是创建对象的蓝图。对象是具有属性（数据）和方法（函数）的实体。
# 这个类代表一个“学生”，具有姓名和年龄属性，以及一个打招呼的方法。
class Student:
    """
    这是一个用于表示学生的类。
    """

    # 构造函数，在创建对象时被调用
    def __init__(self, name: str, age: int):
        # 实例变量，用于存储每个学生的属性
        self.name = name
        self.age = age

    # 类的方法
    def say_hello(self) -> str:
        return f"大家好，我叫 {self.name}，今年 {self.age} 岁。"


# 创建一个 Student 类的对象（也叫实例）
student1 = Student("小明", 18)

# 调用对象的方法
print(student1.say_hello())
print("-" * 20)
