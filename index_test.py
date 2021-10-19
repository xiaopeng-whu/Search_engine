import os
import lxml.etree as etree
import lucene
from java.nio.file import Paths

from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, TextField, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader, FieldInfo, IndexOptions,MultiReader, Term
from org.apache.lucene.store import SimpleFSDirectory
# import similarities
from org.apache.pylucene.search.similarities import PythonClassicSimilarity
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.search.similarities import TFIDFSimilarity
from org.apache.lucene.search import Explanation


# ***implement the document relevance score function by yourself***
class SimpleSimilarity(PythonClassicSimilarity):
    def lengthNorm(self, numTerms):
        return 1.0

    def tf(self, freq):
        return freq

    def sloppyFreq(self, distance):
        return 2.0

    def idf(self, docFreq, numDocs):
        return 1.0

    def idfExplain(self, collectionStats, termStats):
        return Explanation.match(1.0, "inexplicable", [])


class _indexer:
    def __init__(self, data, path, fields_name):
        self.fields = []
        self.data = data
        self.fields_n = fields_name
        self.writer_path = path
        self.init_fields()
        # StandardAnalyzer 根据空格和符号来完成分词，还可以完成数字、字母、E-mail地址、IP地址以及中文字符的分析处理
        self.analyzer = StandardAnalyzer()  # 实例化一个分析器

    def init_writer(self):
        '''Initializes the writer, the storage directory, and the configuration'''
        self.store = SimpleFSDirectory(Paths.get(self.writer_path))     # 实例化一个SimpleFSDirectory对象，将索引保存至本地文件之中
        config = IndexWriterConfig(self.analyzer)
        config.setSimilarity(SimpleSimilarity())    # index和search的similarity应保持一致
        # config.setSimilarity(BM25Similarity(1.2, 0.75))   # BM25貌似就是默认方式？
        # config.setSimilarity(TFIDFSimilarity())
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        # Writer
        self.writer = IndexWriter(self.store, config)   # 在Directory对象上实例化一个IndexWriter对象
        # print(self.writer.getInfoStream())
        self.writer.commit()

    def init_fields(self):
        '''Initialize the fields in an array(the indices will be matching the data indices)
        For later use in the data writer'''
        fields = []

        # Define doc_no field
        doc_no_f = FieldType()
        doc_no_f.setStored(True)
        doc_no_f.setTokenized(False)
        fields.append(doc_no_f)

        # Define doc_type field
        doc_type_f = FieldType()
        doc_type_f.setStored(True)
        doc_type_f.setTokenized(False)
        fields.append(doc_type_f)

        # Define text_type field
        text_type_f = FieldType()
        text_type_f.setStored(True)
        text_type_f.setTokenized(False)
        fields.append(text_type_f)

        # Define text field
        text_f = FieldType()
        text_f.setStored(True)
        text_f.setTokenized(True)
        text_f.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS) # documents, term frequencies and positions are indexed
        fields.append(text_f)

        self.fields = fields
        return fields

    def close_writer(self):
        '''Close the writer'''
        try:
            self.writer.commit()
            self.writer.close()
        except:
            print('Writer already closed')

    def write_doc(self, doc):
        '''Add document into the writer'''
        self.writer.addDocument(doc)

    def write_data(self):
        '''Get an array of array with 4 fields
        Write data into the lucene writer'''
        # Idea was to commit regularly(every 10 docs) but commit are computationaly expensive
        # printo = True
        self.init_writer()
        for d in self.data:
            # Insert array fields into lucene fields
            f0 = Field(self.fields_n[0], d[0], self.fields[0])
            f1 = Field(self.fields_n[1], d[1], self.fields[1])
            f2 = Field(self.fields_n[2], d[2], self.fields[2])
            f3 = Field(self.fields_n[3], d[3], self.fields[3])
            # Add lucene fields to a lucene document
            doc = Document()
            doc.add(f0)
            doc.add(f1)
            doc.add(f2)
            doc.add(f3)
            # Write the documents into the lucene index
            self.write_doc(doc)
        # Close writer
        self.get_fields_name()
        self.close_writer()

    def get_fields_name(self):
        '''Print and return fields names'''
        print(self.writer.getFieldNames())
        return self.writer.getFieldNames()

    def get_info(self):
        ''''''
        return [self.analyzer, self.store]


def xml_crawling(filename):
    xml = etree.parse(filename)
    root = xml.getroot()  # 获取根节点
    doc_no = root.xpath('//DOCNO')[0].text.strip()
    doc_type = root.xpath('//DOCTYPE')[0].text.strip()
    txt_type = root.xpath('//TXTTYPE')[0].text.strip()
    # text = root.xpath('//TEXT')[0].text.replace('\n', '')   # .replace('\n', '').replace('\r', '')
    text = root.xpath('//TEXT')[0].text     # 为了print整洁没必要去除换行符
    # ***存在text为空的文件情况，可能对后面的处理过程产生影响，这里mark一下***
    # print(text)

    return [doc_no, doc_type, txt_type, text]


def convert_character(filename):
    with open(filename, "r", encoding="utf-8") as f1, open("%s.bak" % filename, "w", encoding="utf-8") as f2:
        for line in f1:
            if '&' in line:
                line = line.replace('&', '&amp;')
            f2.write(line)
    return


def data_reader(dataset_path, datas):
    for filepath, dirnames, filenames in os.walk(dataset_path):
        for filename in filenames:
            file_name = os.path.join(filepath, filename)  # https://blog.csdn.net/qq_39721240/article/details/90704223
            # print(file_name)
            convert_character(file_name)
            if os.path.exists(file_name + '.bak'):
                data = xml_crawling(file_name + '.bak')
                os.remove(file_name + '.bak')
            else:
                data = xml_crawling(file_name)
            # print(data)
            datas.append(data)


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    # print(lucene.VERSION)

    # data retrieval
    # datas = [['doc_no1','doc_type1','text_type1','text1'],['doc_no2','doc_type2','text_type2','text2']]
    datas = []
    dataset_path = './tdt3'
    # dataset_path = './tdt3/19981001'
    data_reader(dataset_path, datas)
    print(len(datas))
    # Init_indexer
    # os.path.expanduser(path) 可以将参数中开头部分的 ~ 或 ~user 替换为当前用户的home目录并返回
    path = os.path.expanduser('~/Search_engine/index1')
    fields_n = ['doc_no', 'doc_type', 'text_type', 'text']
    indexer = _indexer(datas, path, fields_n)
    fields = indexer.init_fields()
    indexer.write_data()
    info = indexer.get_info()
    print(info)


