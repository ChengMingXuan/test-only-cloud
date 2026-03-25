"""
修复 supplement 目录下 Selenium 测试文件的缩进错误。
问题：test method 内 driver.get(PAGE_URL) 之后的断言/赋值语句
      缩进为 8 空格（类体级别），应为 12 空格（方法体级别）。
"""
from pathlib import Path

supplement_dir = Path(__file__).parent / "tests" / "generated" / "supplement"
fixed = 0

for py_file in sorted(supplement_dir.glob("test_*.py")):
    content = py_file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    result = []
    in_dangling = False  # 是否处于"悬挂代码"区域

    for line in lines:
        stripped = line.lstrip()
        leading = len(line) - len(line.lstrip(" "))

        # 触发条件：driver.get(PAGE_URL) 在方法体内（12 空格缩进）
        if leading == 12 and stripped.startswith("driver.get(PAGE_URL)"):
            result.append(line)
            in_dangling = True
            continue

        if in_dangling:
            # 停止：下一个装饰器 / 方法定义 / 类定义
            if stripped.startswith("@") or stripped.startswith("def test_") or stripped.startswith("class "):
                in_dangling = False
                result.append(line)
                continue
            # 空行：保持状态继续
            if not stripped.strip():
                result.append(line)
                continue
            # 悬挂代码：前导空格 < 12 → 补 4 空格
            if leading < 12:
                result.append("    " + line)
                continue

        result.append(line)

    new_content = "".join(result)
    if new_content != content:
        py_file.write_text(new_content, encoding="utf-8")
        fixed += 1
        print(f"  Fixed: {py_file.name}")

print(f"\nTotal fixed: {fixed} files")
