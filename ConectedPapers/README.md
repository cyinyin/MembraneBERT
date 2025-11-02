功能

- 借助 https://www.connectedpapers.com/ 网站查找相关联文章
- 收集相关信息（论文信息和关联信息），存入数据库
- 根据关联信息，构建关系图，使用BFS广度优先搜索
- 生成其他文件格式

配置

- 配置selenium工具所需对应浏览器驱动: https://zhuanlan.zhihu.com/p/88152781 
- 驱动下载网址: https://registry.npmmirror.com/binary.html?path=chromedriver/

使用

- 初始论文标题在txt文件内，一行一个，如：test-title.txt
- ```text
  N2 in ZIF-8: Sorbate induced structural changes and self-diffusion
  Integrated metal organic framework/ionic liquid-based composite membrane for CO2 separation
  Computational identification of a metal organic framework for high selectivity membrane-based CO2/CH4 separations: Cu(hfipbb)(H2hfipbb)0.5
  ```
- 配置参数文件 config.json
- ```text
  {
    "title-file": "metal_organic_membrane.txt",
    "driver": "D:\chromedriver-win64\chromedriver.exe",
    "iteration": 8,
    "filter-keywords": ["metal"],
    "wait-time": 30,
    "is-zh": 1
  }
  ```
- 运行main.py
