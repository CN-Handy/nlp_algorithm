# 1. 列表 (list): 有序、可变
# 用途：存储一系列可以改变的数据，比如待办事项、商品列表。
print("--- 列表 (list) ---")
tasks: list[str] = ["写代码", "开会", "看书"]
print(f"原始列表: {tasks}")

# 列表是可变的，可以添加、删除或修改元素
tasks.append("锻炼")
print(f"添加新任务后的列表: {tasks}")
tasks.remove("开会")
print(f"删除任务后的列表: {tasks}")

# 通过索引访问元素
print(f"列表的第一个任务: {tasks[0]}")
print("-" * 20)

# 2. 元组 (tuple): 有序、不可变
# 用途：存储一系列不希望被修改的数据，常用于坐标、颜色值等。
print("--- 元组 (tuple) ---")
# 元组一旦创建就不能修改
point: tuple[int, int] = (10, 20)
color: tuple[int, int, int] = (255, 0, 0)

print(f"一个点的坐标: {point}")
print(f"一种颜色的RGB值: {color}")

# 可以通过索引访问元素
print(f"x 坐标是: {point[0]}")

# 尝试修改元组会报错
# point[0] = 5 # TypeError: 'tuple' object does not support item assignment
print("-" * 20)

# 3. 字典 (dict): 无序、可变，键值对
# 用途：存储键值对数据，就像电话簿一样，通过键快速查找值。
print("--- 字典 (dict) ---")
# 存储用户信息，键是字符串，值可以是任意类型
user_info: dict[str, str] = {
    "name": "小明",
    "age": "25",
    "city": "北京"
}

print(f"用户信息: {user_info}")

# 通过键来访问和修改值
print(f"用户的年龄是: {user_info['age']}")
user_info["age"] = 26
print(f"更新后的用户信息: {user_info}")

# 添加新的键值对
user_info["occupation"] = "软件工程师"
print(f"添加职业后的用户信息: {user_info}")
print("-" * 20)

# 4. 集合 (set): 无序、不重复
# 用途：去重、成员测试、数学集合操作（交集、并集等）。
print("--- 集合 (set) ---")
fruits: set[str] = {"苹果", "香蕉", "橙子", "苹果"}

# 集合会自动去除重复元素
print(f"水果集合: {fruits}")

# 检查元素是否存在，效率很高
if "香蕉" in fruits:
    print("集合中包含香蕉。")

# 集合操作示例
another_fruits: set[str] = {"苹果", "葡萄", "西瓜"}
# 交集：两个集合中都有的元素
print(f"交集 (共同的水果): {fruits.intersection(another_fruits)}")
# 并集：两个集合中所有的不重复元素
print(f"并集 (所有水果): {fruits.union(another_fruits)}")
print("-" * 20)
