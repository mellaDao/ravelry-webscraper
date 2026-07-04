import re
from pathlib import Path
import pickle

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

MODEL_PATH = "sentiment_model.pkl"

def _preprocessor(text):
    return re.sub(r"[^a-z ]", "", text.lower())

def train_sentiment_model(train_csv_path="train.csv", test_size=0.20, random_state=123):
    # load cached model if it exists
    if Path(MODEL_PATH).is_file():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
        
    train_file = Path(train_csv_path)
    if not train_file.is_file():
        raise FileNotFoundError(f"Training file not found: {train_file}")

    amazon_df = pd.read_csv(train_file, names=["sentiment", "title", "review"])
    amazon_df["title"] = amazon_df["title"].fillna("")

    features = amazon_df.title + ". " + amazon_df.review
    labels = amazon_df.sentiment.replace(
        {
            1: "Negative",
            2: "Negative",
            3: "Neutral",
            4: "Positive",
            5: "Positive",
        }
    )

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=test_size,
        random_state=random_state,
    )

    model = Pipeline(
        [
            (
                "vec",
                CountVectorizer(
                    stop_words="english",
                    min_df=1000,
                    preprocessor=_preprocessor,
                ),
            ),
            ("tfid", TfidfTransformer()),
            ("lr", SGDClassifier(loss="log_loss")),
        ]
    )
    model.fit(x_train, y_train)

    y_test_pred = model.predict(x_test)
    report = classification_report(y_test, y_test_pred)

     # save model for next time
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, report), f)

    return model, report


def predict_sentiment(model, df, notes_column="project_notes"):
    if notes_column not in df.columns:
        raise KeyError(f"Column '{notes_column}' not found in dataframe.")

    notes = df[notes_column].fillna("")
    result_df = df.copy()
    result_df["prediction"] = model.predict(notes)
    return result_df