import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

resources = ["punkt", "stopwords", "wordnet", "omw-1.4"]
for res in resources:
    try:
        nltk.data.find(f"tokenizers/{res}" if res == "punkt" else f"corpora/{res}")
    except LookupError:
        nltk.download(res, quiet=True)

def processing_text(text):
    text = text.lower()
    clean_text = ""

    for ch in text:
        if ch not in string.punctuation:
            clean_text += ch

    tokens = word_tokenize(clean_text,language='english')
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    filtered_text = [
        lemmatizer.lemmatize(word, pos='v')
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(filtered_text)
