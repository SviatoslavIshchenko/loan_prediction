import pandas as pd

from django.shortcuts import render

from .forms import LoanPredictionForm
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

