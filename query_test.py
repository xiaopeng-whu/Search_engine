import os
import time
import lucene
import math
from java.nio.file import Paths

from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, FieldInfo, IndexOptions,MultiReader, Term
from org.apache.lucene.search import IndexSearcher, Explanation
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.pylucene.search.similarities import PythonClassicSimilarity
from org.apache.lucene.search.similarities import BM25Similarity


'''implement the document relevance score function'''
class SimpleSimilarity(PythonClassicSimilarity):
    def lengthNorm(self, numTerms):
        return math.sqrt(numTerms)

    def tf(self, freq):
        return math.sqrt(freq)

    # def sloppyFreq(self, distance):
    #     return 2.0

    def idf(self, docFreq, numDocs):
        return math.log((numDocs+1)/(docFreq+1))+1

    def idfExplain(self, collectionStats, termStats):
        return Explanation.match(1.0, "inexplicable", [])


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
        self.isearcher.setSimilarity(SimpleSimilarity())    # index和search的similarity应保持一致
        # self.isearcher.setSimilarity(BM25Similarity(1.2, 0.75))     # set BM25 as the similarity metric, k=1.2, b=0.75

    def format_query(self, fields, params):
        '''Format query to string "field:param" '''
        query = ''
        query = str(fields) + ': ' + str(params) + ''
        print("query:", query)  # 如： text:happy
        return query

    def query(self, field, param):
        print("#EXECUTING SIMPLE QUERY#")
        result = self.run_query(field, param)
        self.print_results(result)

    def run_query(self, field, param):
        '''Run a query with a given field and parameter'''
        self.init_searcher()
        arg = self.format_query(field, param)
        qp = QueryParser('text', self.analyzer)   # 实例化一个QueryParser对象，它描述查询请求，解析Query查询语句
        query = qp.parse(str(arg))  # 以查询语句为参数
        print('###NEW QUERY: field=' + field + '; param=' + param + ' ###')
        query_start_time = time.time()
        # explaination = self.isearcher.explain(query, 0)
        # print("explaination:", explaination)
        result = self.isearcher.search(query, 100).scoreDocs
        query_end_time = time.time()
        search_time = query_end_time - query_start_time
        print("Time taken = " + str(search_time) + "s\n")
        return result

    def print_results(self, result):
        '''Display results in organized way'''
        i = 0
        for r in result[:self.top_k]:   # 返回1~top_k结果
            i = i + 1
            doc = self.isearcher.doc(r.doc)
            print("----------------------------------------------------------------------------------------------------")
            print(str(i) + ':\t score:' + str(r.score) + '\t DOCNO:' + str(doc.get('doc_no')) + '\t DOCTYPE:' + str(doc.get('doc_type')) + '\t TEXTTYPE:' + str(doc.get('text_type')))
            # print('text: ' + doc.get('text'))
            # 对长文本做summary snippets提取
            text = doc.get('text')
            cnt = 0
            for j in range(len(text)):
                if cnt == 3:
                    break
                if text[j] == '\n':
                    cnt = cnt + 1
            print('text(only show the first two lines): ' + text[:j] + '......')


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    # searcher model
    path = os.path.expanduser('~/Search_engine/index1')
    info = [StandardAnalyzer(), SimpleFSDirectory(Paths.get(path))]
    searcher_class = searcher(path, info, top_k=10)
    # Search in text as simple query
    # searcher_class.query('text', 'new york city', 'simple')
    running = True
    while running:
        query_keyword = input('# search ')
        if query_keyword == 'exit!!!':
            running = False
        else:
            # print(list(search(query_string)))
            # print(query_keyword)
            searcher_class.query('text', query_keyword)