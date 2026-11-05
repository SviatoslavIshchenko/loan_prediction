import pandas as pd
import joblib
from django.shortcuts import render

from .forms import LoanPredictionForm
from .models import LoanPrediction
from .ml_service import model, features, threshold


def predict_loan(request):

    # Початкові значення для шаблону
    prediction = None
    probability = None
    error_message = None

    # Перевіряємо, чи користувач надіслав форму
    if request.method == "POST":

        # Отримуємо дані з форми
        form = LoanPredictionForm(request.POST)

        # Перевіряємо правильність введених даних
        if form.is_valid():

            data = form.cleaned_data.copy()

            # Розрахунок сукупного доходу
            total_income = (
                data["ApplicantIncome"]
                + data["CoapplicantIncome"]
            )

            # Розрахунок LoanIncomeRatio
            data["LoanIncomeRatio"] = (
                data["LoanAmount"] / total_income
            )

            # Перетворення числових категорій
            data["Credit_History"] = float(
                data["Credit_History"]
            )

            data["Loan_Amount_Term"] = float(
                data["Loan_Amount_Term"]
            )

            # Формування DataFrame
            input_df = pd.DataFrame(
                [data],
                columns=features
            )

            # Прогнозування
            probability = float(
                model.predict_proba(input_df)[0, 1]
            )

            # Застосування порогу класифікації
            prediction = int(
                probability >= float(threshold)
            )

            # Збереження результату прогнозування в базу даних
            LoanPrediction.objects.create(
                gender=data["Gender"],
                married=data["Married"],
                dependents=data["Dependents"],
                education=data["Education"],
                self_employed=data["Self_Employed"],

                applicant_income=data["ApplicantIncome"],
                coapplicant_income=data["CoapplicantIncome"],
                loan_amount=data["LoanAmount"],
                loan_amount_term=int(data["Loan_Amount_Term"]),

                credit_history=int(data["Credit_History"]),
                property_area=data["Property_Area"],

                probability=probability,
                prediction=prediction
            )

        else:
            error_message = (
                "Перевірте правильність введених даних."
            )

    else:
        # Якщо сторінку відкрито вперше
        form = LoanPredictionForm()

    # Дані, які передаємо у HTML-шаблон
    context = {
        "form": form,
        "prediction": prediction,
        "probability": (
            round(probability * 100, 2)
            if probability is not None
            else None
        ),
        "threshold": float(threshold),
        "error_message": error_message
    }

    return render(
        request,
        "predictor/predict.html",
        context
    )

# Сторінка історії прогнозів
def history(request):

    # Отримуємо всі прогнози з бази даних
    predictions = LoanPrediction.objects.all().order_by("-created_at")

    # Загальна кількість прогнозів
    total = predictions.count()

    # Кількість прогнозованих схвалень
    approved = predictions.filter(prediction=1).count()

    # Кількість прогнозованих відмов
    rejected = predictions.filter(prediction=0).count()

    # Дані для HTML-шаблону
    context = {
        "predictions": predictions,
        "total": total,
        "approved": approved,
        "rejected": rejected
    }

    return render(
        request,
        "predictor/history.html",
        context
    )

# Сторінка коефіцієнтів Logistic Regression
def feature_importance(request):

    model = joblib.load(
        "predictor/ml_models/loan_logistic_pipeline.pkl"
    )

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    # Назви ознак після обробки
    feature_names = preprocessor.get_feature_names_out()

    # Коефіцієнти моделі
    coefficients = classifier.coef_[0]

    # Формуємо таблицю
    features = []

    for name, coef in zip(feature_names, coefficients):
        features.append({
            "name": name,
            "coefficient": round(float(coef), 6),
            "importance": round(abs(float(coef)), 6)
        })

    # Сортуємо за абсолютним значенням
    features.sort(
        key=lambda x: x["importance"],
        reverse=True
    )

    return render(
        request,
        "predictor/feature_importance.html",
        {"features": features}
    )

