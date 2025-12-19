# utils.py (optional, or keep inside app.py)

import torch
from bs4 import BeautifulSoup
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def load_model(model_path):
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2
    )
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model

def html_to_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text().split())

def predict_text(model, text, max_len=256):
    enc = tokenizer(
        text,
        truncation=True,
        padding="max_length",
        max_length=max_len,
        return_tensors="pt"
    )
    with torch.no_grad():
        logits = model(**enc).logits
        pred = torch.argmax(logits, dim=1).item()
        prob = torch.softmax(logits, dim=1)[0][pred].item()
    return pred, prob
