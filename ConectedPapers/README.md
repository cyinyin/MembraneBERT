Features

- Use https://www.connectedpapers.com/ to find related papers.
- Collect related information (paper details and connection data) and store it in a database.
- Build a graph based on the connection data using BFS (Breadth-First Search).
- Generate additional output file formats (Excel, Markdown, JSON, etc.).

Configuration

- Install the required browser driver for Selenium: https://zhuanlan.zhihu.com/p/88152781 
- Driver download URL: https://registry.npmmirror.com/binary.html?path=chromedriver/

Usage

- List the initial paper titles in a TXT file, one title per line, e.g., test-title.txt:
- ```text
  N2 in ZIF-8: Sorbate induced structural changes and self-diffusion
  Integrated metal organic framework/ionic liquid-based composite membrane for CO2 separation
  Computational identification of a metal organic framework for high selectivity membrane-based CO2/CH4 separations: Cu(hfipbb)(H2hfipbb)0.5
  ```
- Configuration file config.json:
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
- Run main.py to execute the pipeline.