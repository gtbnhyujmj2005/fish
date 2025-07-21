# 📚 PubMed 自動摘要 + 翻譯工具
# 功能：搜尋文章 → 摘要濃縮 → 自動翻譯

!pip install biopython transformers sentencepiece googletrans==4.0.0-rc1 --quiet

from Bio import Entrez
from transformers import pipeline
from googletrans import Translator
import pandas as pd

# 1️⃣ Entrez API 設定
Entrez.email = "your_email@example.com"  # <- 請改成你自己的 email

# 2️⃣ 查詢 PubMed ID 清單
def search_pubmed(term, retmax=5):
    handle = Entrez.esearch(db="pubmed", term=term, retmax=retmax)
    record = Entrez.read(handle)
    return record["IdList"]

# 3️⃣ 抓摘要文字
def fetch_abstract(pmid):
    handle = Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="text")
    return handle.read()

# 4️⃣ 自動摘要模型 + 翻譯初始化
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
translator = Translator()

# 5️⃣ 主流程
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
                "Abstract": "(失敗)",
                "Summary": str(e),
                "翻譯摘要": "-"
            })

    return pd.DataFrame(results)

# ✅ 範例使用：查「carp blue pigment gene」
df = run_pipeline("carp blue pigment gene", n=3)
df.head()
