# coding=utf-8
"""
# 功能目标
- 确定核心论文：放在txt文中，一行一个
- 根据论文标题，在 https://www.connectedpapers.com/ 上搜索结果，根据第一条展开 关系图
- 收集相关信息（论文信息和关联信息），存入数据库
- 根据关联信息，构建关系图，使用BFS广度优先搜索
- 生成其他文件格式
"""
from unit import Args
from unit.connection import spider
from unit.write import Write
if __name__ == "__main__":
    _args = Args()
    # _args.log.init()

    # 爬取相关文献
    spider(_args)

    # 输入结果到文件
    w = Write(_args)
    w.to_excel()
    w.to_markdown()

    pass
