uv run python -m src.ml.train_model
uv run python -m src.rag.store
uv run python main.py
uv run streamlit run app.py