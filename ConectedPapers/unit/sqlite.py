# -*- coding: utf-8 -*-
import os.path
import sqlite3
from unit import Args


class Sqlite(object):
    def __init__(self, database_file):
        need_create_table = False
        if not os.path.exists(database_file):
            need_create_table = True

        self._connect = sqlite3.connect(database_file)
        self._cursor = self._connect.cursor()
        self._table_name = 'paper'
        if need_create_table:
            self.init_table()
        self.header = ['title', 'author', 'year', 'journal', 'citations', 'year_citations', 'connected_papers_url', 'semantic_scholar_url', 'publisher_page_url', 'abstract', 'title_zh', 'abstract_zh']

    def init_table(self):
        # id integer primary key autoincrement
        sql = f'''
                    create table {self._table_name} (
                        title text primary key,
                        author text,
                        year text,
                        journal text,
                        citations text,
                        year_citations text,
                        connected_papers_url text,
                        semantic_scholar_url text,
                        publisher_page_url text,
                        abstract text,
                        title_zh text,
                        abstract_zh text
                    )
                '''
        self._cursor.execute(sql)
        self._connect.commit()

        text = ""
        for i in range(40):
            text += f'con_{i} text,'
        text = text[:-1]

        sql = f'''
                    create table graph (
                        title text primary key,
                        {text}
                    )
                '''
        # print(sql)
        self._cursor.execute(sql)
        self._connect.commit()

    def insert_paper(self, data: list):
        header, value = "", ""
        for index, item in enumerate(self.header):
            header += f'{item},'
            value += f'"{data[index]}",'
        header, value = header[:-1], value[:-1]

        sql = f'''insert into {self._table_name} ({header}) values ({value});'''
        # print(sql)
        # print(len(self.header), len(data))
        # print(header)
        # print(data)

        # self._cursor.execute("PRAGMA table_info(paper)")
        # print(self._cursor.fetchall())

        try:
            self._cursor.execute(sql)
            self._connect.commit()
        except sqlite3.IntegrityError as e:
            print(f'Warning: {e}, title: {data[0]}')
        pass

    def insert_connection(self, data: list):
        header, value = "title,", f'"{data[0]}",'
        for i in range(40):
            header += f'con_{i},'
            value += f'"{data[i+1]}",'
        header, value = header[:-1], value[:-1]

        sql = f'''insert into graph ({header}) values ({value});'''
        # print(sql)

        try:
            self._cursor.execute(sql)
            self._connect.commit()
        except sqlite3.IntegrityError as e:
            print(f'Warning: {e}, title: {data[0]}')
        pass

    def check_title_is_exists(self, title):
        sql = f'''select title from {self._table_name} where title="{title}";'''
        # print(sql)

        res = self._cursor.execute(sql)
        # fetchall() will return a list of the rows returned from the select
        if len(res.fetchall()) == 1:
            return True
        else:
            return False

    def check_title_is_exists_in_graph(self, title):
        sql = f'''select title from graph where title="{title}";'''
        # print(sql)

        res = self._cursor.execute(sql)
        # fetchall() will return a list of the rows returned from the select
        if len(res.fetchall()) == 1:
            return True
        else:
            return False

    def select_all_from_paper(self):
        sql = f'''select * from {self._table_name};'''
        # print(sql)

        res = self._cursor.execute(sql)

        # fetchall() will return a list of the rows returned from the select
        return res.fetchall()

    def select_all_from_graph(self):
        sql = f'''select * from graph;'''
        # print(sql)

        res = self._cursor.execute(sql)
        # fetchall() will return a list of the rows returned from the select
        for item in res:
            print(item)

    def select_connection_from_graph(self, title):
        sql = f'''select * from graph where title="{title}";'''
        # print(sql)

        res = self._cursor.execute(sql)

        # fetchall() will return a list of the rows returned from the select
        return res.fetchall()

    def select_url_from_paper(self, title):
        sql = f'''select connected_papers_url from {self._table_name} where title="{title}";'''
        # print(sql)

        res = self._cursor.execute(sql)

        # fetchall() will return a list of the rows returned from the select
        return res.fetchall()

    def check_table(self):
        sql = f'''select title from {self._table_name};'''
        print(f'info: {sql}')
        paper_title = self._cursor.execute(sql).fetchall()
        paper_title_set = set()
        for item in paper_title:
            paper_title_set.add(item[0])

        sql = f'''select title from graph;'''
        print(f'info: {sql}')
        connection_title = self._cursor.execute(sql).fetchall()
        connection_title_set = set()
        for item in connection_title:
            connection_title_set.add(item[0])

        for item in connection_title_set:
            if item not in paper_title_set:
                sql = f'''delete from graph where title="{item}";'''
                print(f'info: {sql}')
                self._cursor.execute(sql)

        self._connect.commit()
        # print(self.check_title_is_exists(title))

    def delete_title(self, title):
        """
        func : Delete both detailed information and relationship graph
        :param title:
        :return:
        """
        if self.check_title_is_exists(title):
            sql = f'''delete from paper where title="{title}";'''
            print(f'info: {sql}')
            self._cursor.execute(sql)

            sql = f'''delete from graph where title="{title}";'''
            print(f'info: {sql}')
            self._cursor.execute(sql)

            self._connect.commit()

        else:
            print(f'Warning: not delete: {title}')

    def __del__(self):
        self._connect.close()


if __name__ == '__main__':
    _args = Args()
    sqlite = Sqlite(_args.database)
    # _t = 'Protein–Sol: a web tool for predicting protein solubility from sequence'
    # _t = 'Protein-Sol: a web tool for predicting protein solubility from sequence'
    # print(sqlite.check_title_is_exists_in_graph(_t))

    # delete title
    _title = [
        "N2 in ZIF-8: Sorbate induced structural changes and self-diffusion"
    ]

    pass
