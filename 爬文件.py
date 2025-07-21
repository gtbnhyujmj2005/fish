# 安裝必要套件（執行一次）
!pip install biopython transformers sentencepiece googletrans==4.0.0-rc1 --quiet

from Bio import Entrez
from transformers import pipeline
from googletrans import Translator
import pandas as pd

# 請換成你的 email（Entrez API 要求）
Entrez.email = "your_email@example.com"

# 1. 搜尋 PubMed
def search_pubmed(term, retmax=5):
    handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax)
    record = Entrez.read(handle)
    return record["IdList"]

# 2. 取得摘要
def fetch_abstract(pmid):
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
    return handle.read()

# 3. 建立摘要模型
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 4. 翻譯工具
translator = Translator()

# 主流程
def run_pipeline(search_term, n=3):
    pmids = search_pubmed(search_term, retmax=n)
    results = []

    for pmid in pmids:
        try:
            abstract = fetch_abstract(pmid)
            summary = summarizer(abstract, max_length=100, min_length=20, do_sample=False)[0]['summary_text']
            translated = translator.translate(summary, dest='zh-tw').text
            results.append({
                "PMID": pmid,
                "Abstract": abstract.strip(),
                "Summary": summary.strip(),
                "翻譯摘要": translated.strip()
            })
        except Exception as e:
            results.append({
                "PMID": pmid,
                "Abstract": "(取得失敗)",
                "Summary": str(e),
                "翻譯摘要": "-"
            })

    return pd.DataFrame(results)

# 以青花瓷鯉魚色素基因為範例關鍵字
df = run_pipeline("carp blue pigment gene", n=3)
print(df)
