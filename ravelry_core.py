from ravelry_auth import load_credentials_from_file
from scraper import scrape_pattern
from sentiment import train_sentiment_model, predict_sentiment
from storage import save_dataframe, load_dataframe


def run_pipeline(
    mode,
    pattern_slug="agnete-cardigan",
    username=None,
    password=None,
    credentials_path=None,
    credentials_key=None,
    session=None,
    excel_path="Agnete-Cardigan.xlsx",
    predictions_path="predictions.xlsx",
    train_csv_path="train.csv",
    on_progress=None,
):
    mode = str(mode)
    df = None
    report = None

    if mode in {"1", "3", "scrape", "both"}:
        if session is None and (not username or not password):
            username, password = load_credentials_from_file(
                path=credentials_path,
                key=credentials_key,
            )

        df = scrape_pattern(
            pattern_slug=pattern_slug,
            username=username,
            password=password,
            credentials_path=credentials_path,
            credentials_key=credentials_key,
            session=session,
            on_progress=on_progress,
        )
        save_dataframe(df, excel_path)
        if on_progress:
            on_progress(f"Saved scrape results to {excel_path}.")

    if mode in {"2", "3", "sentiment", "both"}:
        if df is None:
            if on_progress:
                on_progress(f"Loading data from {excel_path}...")
            df = load_dataframe(excel_path)

        if on_progress:
            on_progress("Training sentiment model...")
        model, report = train_sentiment_model(train_csv_path=train_csv_path)

        if on_progress:
            on_progress("Predicting sentiment on project notes...")
        predictions_df = predict_sentiment(model, df)
        save_dataframe(predictions_df, predictions_path)
        if on_progress:
            on_progress(f"Saved predictions to {predictions_path}.")

    return {
        "dataframe": df,
        "report": report,
        "excel_path": excel_path,
        "predictions_path": predictions_path if mode in {"2", "3", "sentiment", "both"} else None,
    }