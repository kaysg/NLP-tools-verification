# coding: utf-8

import re
import nltk
import MeCab
import pykakasi
from bs4 import BeautifulSoup

__author__ = "kaysg"
__status__ = "dev"

def remove_html_tags(html_doc, lines_concat = True):
    """ Remove html tags from input strings
    >>> sample_doc = '''<html><head><title>The Dormouse's story</title></head>
    ... <body><p class="title"><b>A Mad Tea-Party</b></p></body>
    ... </html>'''
    >>> remove_html_tags(sample_doc, False)
    "The Dormouse's story\\nA Mad Tea-Party\\n"
    >>> remove_html_tags(sample_doc, True)
    "The Dormouse's story A Mad Tea-Party"
    """

    soup = BeautifulSoup(html_doc, 'html.parser')
    text = soup.get_text()
    if lines_concat:
        text = ' '.join(text.splitlines())
    return text

def find_matched_pos(str, pattern):
    """ Find all positions (start,end) of matched characters
    >>> find_matched_pos('ss12as34cdf', '\d')
    [(2, 3), (3, 4), (6, 7), (7, 8)]
    """
    match_objs = re.finditer(pattern ,str)
    match_pos = [match_obj.span() for match_obj in match_objs]

    return match_pos

def wn_lemma(str):
    """ Perform lemmatizing using WordNet's lemmatizer
    >>> wn_lemma('women')
    'woman'
    >>> wn_lemma('corpora')
    'corpus'
    """
    lemmatizer = nltk.WordNetLemmatizer()
    lemmatized = lemmatizer.lemmatize(str)
    return lemmatized

def remove_stopwords(wordlist):
    """ remove stopwords and short length words
    >>> remove_stopwords(['He', 'grinned', 'and', 'said', ',', '"', 'I', 'make', 'lots', 'of', 'money', '.'])
    ['grinned', 'said', 'make', 'lots', 'money']
    """
    max_wordlen = 3
    stopset = set(nltk.corpus.stopwords.words('english'))
    wordlist = [w for w in wordlist if len(w) > max_wordlen and w not in stopset]
    return wordlist

def remove_stopwords_jp(wordlist):
    ''' remove stopwords
    jp_stopwords.txt is created based on stopwords in SlothLib
    >>> remove_stopwords_jp(['また', 'あの', '人', 'が', '前', 'の', '方', 'から', 'やってきた'])
    ['また', 'あの', 'が', 'の', 'やってきた']
    '''
    import codecs
    with codecs.open('jp_stopwords.txt', 'r', 'utf-8') as f:
        stopwords = f.readlines()
    stopset = set(sw.replace('\n','') for sw in stopwords)
    wordlist = [w for w in wordlist if w not in stopset]
    return wordlist

def mcb_tokenize(str):
    """ Perform tokenize to a Japanese string
    >>> mcb_tokenize(u'今日のお天気は晴れです')
    ['今日', 'の', 'お', '天気', 'は', '晴れ', 'です']
    """
    t = MeCab.Tagger("-Owakati")
    str_wakachi = t.parse(str)
    words = str_wakachi.split(" ")
    if words[-1] == "\n":
        words = words[:-1]
    return words

def mcb_POS_tag_jp(str):
    """Japanese morphological analysis (POS tagging) using ipadic
    >>> mcb_POS_tag_jp(u'今日のお天気は晴れです')
    [['今日', 'キョウ', '今日', '名詞-副詞可能', '', ''], ['の', 'ノ', 'の', '助詞-連体化', '', ''], ['お', 'オ', 'お', '接頭詞-名詞接続', '', ''], ['天気', 'テンキ', '天気', '名詞-一般', '', ''], ['は', 'ハ', 'は', '助詞-係助詞', '', ''], ['晴れ', 'ハレ', '晴れ', '名詞-一般', '', ''], ['です', 'デス', 'です', '助動詞', '特殊・デス', '基本形'], ['EOS'], ['']]
    """
    t = MeCab.Tagger("-Ochasen")
    tagged_words = t.parse(str).split('\n')
    tagged_words = [tw.split('\t') for tw in tagged_words]
    return tagged_words

def mcbne_POS_tag_jp(str):
    """Japanese morphological analysis (POS tagging) using ipadic-NEologd
    >>> mcbne_POS_tag_jp(u'今日のお天気は晴れです')
    [['今日', '名詞', '副詞可能', '*', '*', '*', '*', '今日', 'キョウ', 'キョー'], ['の', '助詞', '連体化', '*', '*', '*', '*', 'の', 'ノ', 'ノ'], ['お天気', '名詞', '一般', '*', '*', '*', '*', 'お天気', 'オテンキ', 'オテンキ'], ['は', '助詞', '係助詞', '*', '*', '*', '*', 'は', 'ハ', 'ワ'], ['晴れ', '名詞', '一般', '*', '*', '*', '*', '晴れ', 'ハレ', 'ハレ'], ['です', '助動詞', '*', '*', '*', '特殊・デス', '基本形', 'です', 'デス', 'デス'], ['EOS'], ['']]
    """
    t = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    tagged_words = t.parse(str).split('\n')
    tagged_words = [tw.replace("\t", ",").split(',') for tw in tagged_words]
    return tagged_words

def get_noun_verb_jp(str):
    """ Get unique words (noun and verb) from a Japanese string (feature extraction)
    >>> get_noun_verb_jp(u'シンガポールは、東南アジアの主権都市国家かつ島国である。マレー半島南端、赤道の137km北に位置する。')
    ['シンガポール', '東南アジア', '主権', '都市国家', '島国', 'マレー半島', '南端', '赤道', '137km', '北', '位置', 'する']
    """
    tagged_words = mcbne_POS_tag_jp(str)
    noun_verb = [w[0] for w in tagged_words if len(w)>1 and (w[1]=='名詞' or w[1]=='動詞')]
    noun_verb = remove_stopwords_jp(noun_verb)
    return noun_verb

def jp_text_to_roman(str):
    ''' Convert Japanese text to Roman/Alphabet text
    >>> jp_text_to_roman(u'今日のお天気は晴れです')
    'kyou noo tenki ha hare desu'
    >>> jp_text_to_roman(u'矢野浩二')
    'yano kouji'
    '''

    w = pykakasi.wakati()
    k = pykakasi.kakasi()
    k.setMode('H', 'a')  # Hiragana to Alphabet/Roman Letter
    k.setMode('K', 'a')  # Katakana to Alphabet/Roman Letter
    k.setMode('J', 'a')  # Kanji to Alphabet/Roman Letter
    k.setMode('C', False)  # Capitalize

    result = str
    for parser in [w, k]:
        c = parser.getConverter()
        result = c.do(result)

    return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()

