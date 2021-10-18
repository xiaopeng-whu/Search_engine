import lxml.etree as etree
import os

'''
    xml_crawling:
        爬取xml文件中的关键信息  参考 https://yshblog.com/blog/151
        https://blog.csdn.net/weixin_45492007/article/details/103481551
'''


def xml_crawling(filename):
    xml = etree.parse(filename)
    root = xml.getroot()  # 获取根节点
    # for node in root.getchildren():
    #     print(node.tag)
    doc_no = root.xpath('//DOCNO')[0].text.strip()
    doc_type = root.xpath('//DOCTYPE')[0].text.strip()
    txt_type = root.xpath('//TXTTYPE')[0].text.strip()
    # for node in root.xpath('//TEXT'):
    #     print(node.text.replace('\n', ''))  # .replace('\n', '').replace('\r', '')
    # text = root.xpath('//TEXT')[0].text.replace('\n', '')   # .replace('\n', '').replace('\r', '')
    text = root.xpath('//TEXT')[0].text # 为了print整洁没必要去除换行符
    # ***存在text为空的文件情况，可能对后面的处理过程产生影响，这里mark一下***
    # print(text)

    return [doc_no, doc_type, txt_type, text]


'''
    convert_character:
        filename = "CNN19981001_0130_0263.txt"    # TEXT中存在特殊字符'&'，XML无法解析
        需要对TEXT域中的文字中的'&'替换为'&amp;'，创建一个临时文件提取完自动删除节省空间
        暂未发现其他特殊字符影响信息的爬取，故只对'&'作处理；如果'<'也存在则不能直接转义处理，这样会导致xml找不到起始的'<'标记
        参考 https://blog.csdn.net/weixin_40567689/article/details/89736716
        https://blog.csdn.net/qq1124794084/article/details/80788129
'''


def convert_character(filename):
    with open(filename, "r", encoding="utf-8") as f1, open("%s.bak" % filename, "w", encoding="utf-8") as f2:
        for line in f1:
            if '&' in line:
                line = line.replace('&', '&amp;')
            f2.write(line)
    return


'''
    data_reader:
        遍历数据集所有xml文件，提取关键信息至二维列表中
'''


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
            print(data)
            datas.append(data)


if __name__ == "__main__":
    datas = []
    # dataset_path = './tdt3'
    dataset_path = './tdt3/19981001'

    # data retrieval
    data_reader(dataset_path, datas)
    print(len(datas))
    print(datas[0][3])

    # indexer





    # filename = "CNN19981001_0130_0263.txt"    # TEXT中存在特殊字符'&'，XML无法解析
    # # filename = "ABC19981001_1830_0000.txt"
    # convert_character(filename)
    # if os.path.exists(filename+'.bak'):
    #     data = xml_crawling(filename+'.bak')
    #     os.remove(filename+'.bak')
    # else:
    #     data = xml_crawling(filename)
    # print(data)
