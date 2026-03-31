import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

resources = ["punkt", "stopwords", "wordnet", "omw-1.4"]
for res in resources:
    try:
        if res == "punkt":
            nltk.data.find("tokenizers/punkt")
        else:
            nltk.data.find(f"corpora/{res}")
    except LookupError:
        nltk.download(res, quiet=True)

def processing_text(text):
    text = text.lower()
    clean_text = "".join(ch for ch in text if ch not in string.punctuation)

    tokens = word_tokenize(clean_text)
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    filtered_text = [
        lemmatizer.lemmatize(word, pos='v')
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(filtered_text)
