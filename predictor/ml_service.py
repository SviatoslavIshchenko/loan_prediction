
from pathlib import Path
import joblib

# Шлях до папки зі збереженою моделлю
MODEL_DIR = Path(__file__).resolve().parent / "ml_models"

# Завантаження навченої моделі разом із Pipeline
model = joblib.load(
    MODEL_DIR / "loan_logistic_pipeline.pkl"
)

# Завантаження списку предикторів
features = joblib.load(
    MODEL_DIR / "features.pkl"
)

# Завантаження порогу класифікації
threshold = joblib.load(
    MODEL_DIR / "threshold.pkl"
)
