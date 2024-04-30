import hashlib
import os.path
import time
from globals import ALLOWED_EXTENSIONS, filename2faiss, UPLOAD_FOLDER
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_suffix(filename):
    print(filename)
    return filename.rsplit('.', 1)[1]


def generate_char_id():
    m2 = hashlib.md5()
    m2.update(str(time.time()).encode('utf-8'))

    return m2.hexdigest()[8:-8]


def load_txt(file_name):
    with open(os.path.join(UPLOAD_FOLDER, file_name), "r") as f:
        text = f.read()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    docs = text_splitter.create_documents([text])
    faiss_index = FAISS.from_documents(docs, OpenAIEmbeddings())
    filename2faiss[file_name] = faiss_index


def load_pdf(file_name):
    loader = PyPDFLoader(os.path.join(UPLOAD_FOLDER, file_name))
    doc = loader.load()
    faiss_index = FAISS.from_documents(doc, OpenAIEmbeddings())
    filename2faiss[file_name] = faiss_index


def load_file(file_name):
    suffix = get_suffix(file_name)
    if suffix == "txt" or suffix == "md":
        load_txt(file_name)
    elif suffix == "pdf":
        load_pdf(file_name)


if __name__ == '__main__':
    print(generate_char_id())
