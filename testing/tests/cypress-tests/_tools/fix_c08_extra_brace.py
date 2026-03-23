"""
修复 C08 多余的 }); 行
在 fix_all_tests.py 运行时，将 cy.wrap($p).find(...).then() 改为 body.find() 后
留下了多余的 }); 行，导致语法错误
"""
import re
import glob
import os

# 模式：cy.get('body').then(...)  inline(单行)
# 后面紧跟着一个多余的 "          });  " 行（10个空格 + });）
# 然后是 "        }" (8个空格 + })

# 准确匹配：
# Line N:   cy.get('body').then($body => { const $nx = ...; });
# Line N+1: "          });
# Line N+2: "        }
PATTERN = re.compile(
    r"([ \t]+cy\.get\('body'\)\.then\(\$body\s*=>\s*\{[^\n]*"
    r"ant-pagination-next[^\n]*\}\);\n)"  # Line with body.then inline ending in });
    r"([ \t]+\}\);\n)"                    # Extra }); line to REMOVE
    r"([ \t]+\}\n)",                      # The correct } line
    re.MULTILINE
)

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()
    
    fixed = PATTERN.sub(r'\1\3', original)
    
    if fixed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f"  ✅ 修复 {os.path.basename(filepath)}")
        return True
    else:
        print(f"  ⏭️  {os.path.basename(filepath)}: 无需修复")
        return False

files = sorted(glob.glob('d:/2026/aiops.v2/tests/cypress-tests/e2e/*.cy.js'))
fixed = sum(fix_file(f) for f in files)
print(f"\n共修复 {fixed} 个文件")
