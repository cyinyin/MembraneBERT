# coding=utf-8
"""
# Functional Objectives
- Identify core papers: listed in a TXT file, one title per line.
- Search for the paper titles on [https://www.connectedpapers.com/](https://www.connectedpapers.com/) and expand the relationship graph based on the first result.
- Collect relevant information (paper details and connections) and store it in a database.
- Construct a relationship graph based on the connections using BFS (Breadth-First Search).
- Generate other file formats.
"""
from unit import Args
from unit.connection import spider
from unit.write import Write
if __name__ == "__main__":
    _args = Args()
    # _args.log.init()

    # Scrape related literature
    spider(_args)

    # Write results to a file
    w = Write(_args)
    w.to_excel()
    w.to_markdown()

    pass

