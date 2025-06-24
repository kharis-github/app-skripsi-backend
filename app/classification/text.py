import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import requests
import ast
import pandas as pd

more_stop_words = ['kaburajadulu'] # hapus teks kaburajadulu
# inisialisasi stopword remover
stop_words = StopWordRemoverFactory().get_stop_words()
stop_words.extend(more_stop_words)

new_array = ArrayDictionary(stop_words)
stop_words_remover_new = StopWordRemover(new_array)

# inisialisasi stemmer
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# fetch dictionary slang words Bahasa Indonesia dari github


async def get_slang_dict():
    url = "https://raw.githubusercontent.com/louisowen6/NLP_bahasa_resources/master/combined_slang_words.txt"
    response = requests.get(url)
    dict = ast.literal_eval(response.text)
    slang_dict = {f" {k} ": f" {v} " for k, v in dict.items()}
    return slang_dict


# text preprocessing: proses standar text preprocessing


def text_cleaning(text):
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)  # hapus mentions
    text = re.sub(r'#\w+', '', text)  # hapus tagar
    text = re.sub(r'RT[\s]+', '', text)  # hapus retweet
    text = re.sub(r'https?://\S+', '', text)  # hapus URL

    text = re.sub(r'[^a-zA-Z\s]', '', text)  # hapus karakter non-alfanumerik
    text = re.sub(r'\s+', ' ', text).strip()  # hapus spasi berlebihan

    return text.lower()  # lowercase

# text normalization: normalisasi teks ke bentuk yang standar


def normalisasi(str_text, norm):
    for i in norm:
        str_text = str_text.replace(i, norm[i])
    return str_text


# stopwords removal: hapus stopwords


def stopwords_removal(text):

    text = stop_words_remover_new.remove(text)
    return text

# tokenization


def tokenize(text):
    return text.split()


# stemming untuk data yang reguler
def stemming(text):
    return stemmer.stem(text)

# stemming untuk data yang telah tertokenisasi


def stemming_for_tokenized(text_array):
    stemmed_array = []
    # stem setiap kata pada array
    for w in text_array:
        w_stemmed = stemmer.stem(w)
        stemmed_array.append(w_stemmed)
    # gabungkan stemmed_array menjadi satu string
    stemmed_string = []
    stemmed_string = " ".join(stemmed_array)
    return stemmed_string

# terapkan proses text preprocessing pada data DataFrame


async def text_preprocessing(data: pd.DataFrame):
    # 1 | text cleaning
    data['cleaning'] = data['full_text'].apply(text_cleaning)
    # 2 | normalization
    slang_dict = await get_slang_dict()
    data['normalized'] = data['cleaning'].apply(
        lambda x: normalisasi(x, slang_dict))
    # 3 | stopwords removal
    data['stopwords'] = data['normalized'].apply(stopwords_removal)
    # 4 | stemming
    data['stemming'] = data['stopwords'].apply(stemming)
    # print('[DEBUG]: Selesai proses stemming')
    # print(data['stemming'].head(20))
    # 5 | return
    return data  # kembalikan hasil bersih data, dan hasil proses-proses lainnya
