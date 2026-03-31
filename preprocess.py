import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def processing_text(text):
    text = text.lower()
    clean_text = "".join([ch for ch in text if ch not in string.punctuation])


    tokens = clean_text.split()
    
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    filtered_text = [
        lemmatizer.lemmatize(word, pos='v')
        for word in tokens
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(filtered_text)
