# -*- coding: utf-8 -*-

from unit.sqlite import Sqlite
from unit import Args
import openpyxl


class Write:
    def __init__(self, args: Args):
        self._check_func = args.check_is_keyword_in_strings
        self._excel_file = args.excel_file
        self._markdown = args.markdown
        self._log = args.log
        self._is_zh = args.is_zh

        self._sqlite = Sqlite(args.database)
        self._result = self._sqlite.select_all_from_paper()
        self._header = self._sqlite.header

        # 对结果按引用量排序
        self._result = list(self._result)
        self._result.sort(key=lambda x: float(x[5]), reverse=True)

        count = 0
        for item in self._result:
            if self._check_func(item[0]):
                print(item)
                count += 1
            if count > 4:
                break

        pass

    def to_excel(self):
        self._log.append('Starting write to excel.')
        target_workbook = openpyxl.Workbook(write_only=True)
        target_sheet = target_workbook.create_sheet('sheet0')

        # 表头
        header = ['title', 'author', 'year', 'journal', 'citations', 'year_citations', 'connected_papers_url', 'semantic_scholar_url', 'publisher_page_url', 'abstract']
        if self._is_zh:
            header = ['title', 'author', 'year', 'journal', 'citations', 'year_citations', 'connected_papers_url', 'semantic_scholar_url', 'publisher_page_url', 'abstract', 'title_zh', 'abstract_zh']

        target_sheet.append(header)

        # 写入
        if self._is_zh:
            for item in self._result:
                if self._check_func(item[0]):
                    target_sheet.append(item)
        else:
            for item in self._result:
                if self._check_func(item[0]):
                    item = list(item)
                    item = item[:-2]
                    target_sheet.append(item)

        target_workbook.save(self._excel_file)
        pass

    def to_markdown(self):
        self._log.append('Starting write to markdown.')

        # 索引
        header = {'title': 0, 'author': 1, 'year': 2, 'journal': 3, 'citations': 4, 'year_citations': 5,
                  'connected_papers_url': 6, 'semantic_scholar_url': 7, 'publisher_page_url': 8, 'abstract': 9,
                  'title_zh': 10, 'abstract_zh': 11}

        # 写入
        sign = 0
        with open(self._markdown, 'w', encoding='utf-8') as w:
            for item in self._result:
                if not self._check_func(item[0]):
                    continue
                sign += 1

                if self._is_zh:  # 标题、链接、引用，年均引用，作者、年份，期刊、中文标题、中文摘要
                    strs = f'''### {sign}.{item[header.get('title')]}
- {item[header.get('publisher_page_url')]}
- {item[header.get('citations')]}, {item[header.get('year_citations')]}, {item[header.get('author')]}
- {item[header.get('year')]}, {item[header.get('journal')]}
- {item[header.get('title_zh')]}
- {item[header.get('abstract_zh')]}

'''
                else:  # 标题、链接、引用，年均引用，作者、年份，期刊、摘要
                    strs = f'''### {sign}.{item[header.get('title')]}
- {item[header.get('publisher_page_url')]}
- {item[header.get('citations')]}, {item[header.get('year_citations')]}, {item[header.get('author')]}
- {item[header.get('year')]}, {item[header.get('journal')]}
- {item[header.get('abstract')]}

'''
                w.write(strs)
        pass


if __name__ == '__main__':
    _args = Args()
    _w = Write(_args)
    _w.to_excel()
    pass
