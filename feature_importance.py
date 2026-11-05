
import joblib
import pandas as pd
from pathlib import Path

# Шлях до збереженої моделі
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "predictor" / "ml_models"

# Завантажуємо Pipeline
model = joblib.load(MODEL_DIR / "loan_logistic_pipeline.pkl")

# Отримуємо етапи Pipeline
preprocessor = model.named_steps["preprocessor"]
classifier = model.named_steps["classifier"]

# Назви ознак після обробки
feature_names = preprocessor.get_feature_names_out()

# Коефіцієнти логістичної регресії
coefficients = classifier.coef_[0]

# Формуємо таблицю
importance = pd.DataFrame({
    "Ознака": feature_names,
    "Коефіцієнт": coefficients,
    "Абсолютний коефіцієнт": abs(coefficients)
})

# Сортуємо за величиною коефіцієнтів
importance = importance.sort_values(
    by="Абсолютний коефіцієнт",
    ascending=False
)

print("\nКоефіцієнти Logistic Regression:")
print(importance.to_string(index=False))
