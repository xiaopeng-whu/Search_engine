import os
import lucene
from java.nio.file import Paths

from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, FieldInfo, IndexOptions,MultiReader, Term
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser


class searcher:
    def __init__(self, path, info, top_k):
        '''Initializes the searcher class'''
        self.path = path
        self.isearcher = None
        self.store = info[1]
        self.analyzer = info[0]
        self.init_searcher()
        self.top_k = top_k

    def init_searcher(self):
        '''Initializes the lucene searcher'''
        self.isearcher = IndexSearcher(DirectoryReader.open(self.store))    # 实例化一个IndexSearcher对象，它的参数为SimpleFSDirectory对象

    def format_query(self, fields, params):
        '''Format query to string "field:param" '''
        query = ''
        query = str(fields) + ': ' + str(params) + ''
        # print("query:", query)  # 如： text:happy
        return query

    def query(self, field, param, option):
        if option == "simple":
            print("#EXECUTING SIMPLE QUERY#")
            result = self.run_query(field, param)
            self.print_results(result)
        # elif option == "expansion":
        #     print("#EXECUTING EXPANDED QUERY#")
        #     result2 = self.expand(field, param)

    def run_query(self, field, param):
        '''Run a query with a given field and parameter'''
        self.init_searcher()
        arg = self.format_query(field, param)
        qp = QueryParser('id', self.analyzer)   # 实例化一个QueryParser对象，它描述查询请求，解析Query查询语句
        query = qp.parse(str(arg))  # 以查询语句为参数
        print('###NEW QUERY: field=' + field + '; param=' + param + ' ###')
        # ***implement the document relevance score function by yourself***
        result = self.isearcher.search(query, 100).scoreDocs
        return result

    def print_results(self, result):
        '''Display results in organized way'''
        print('Results size: ', len(result))
        i = 0
        for r in result[:self.top_k]:   # 返回top_k结果
            i = i + 1
            doc = self.isearcher.doc(r.doc)
            print("---------------")
            print(str(i) + ':\t score:' + str(r.score) + '\t DOCNO:' + str(doc.get('doc_no')) + '\t DOCTYPE:' + str(doc.get('doc_type')) + '\t TEXTTYPE:' + str(doc.get('text_type')))
            print('text: ' + doc.get('text'))   # 需要对长文本做summary snippets提取


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    # searcher model
    path = os.path.expanduser('~/Search_engine/index1')
    info = [StandardAnalyzer(), SimpleFSDirectory(Paths.get(path))]
    searcher_class = searcher(path, info, top_k=10)
    # Search in comment_body as simple query
    searcher_class.query('text', 'new york', 'simple')