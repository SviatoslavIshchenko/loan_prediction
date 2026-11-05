import pandas as pd
from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .forms import LoanPredictionForm
from .models import LoanPrediction
from .ml_service import model, features, threshold

import csv
from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


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
    # Отримуємо назви ознак після обробки
    preprocessor = model.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out()

    # Отримуємо коефіцієнти Logistic Regression
    classifier = model.named_steps["classifier"]
    coefficients = classifier.coef_[0]

    # Зрозумілі назви факторів
    factor_names = {
        "Gender": "Стать",
        "Married": "Сімейний стан",
        "Dependents": "Кількість утриманців",
        "Education": "Освіта",
        "Self_Employed": "Самозайнятість",
        "ApplicantIncome": "Дохід заявника",
        "CoapplicantIncome": "Дохід співзаявника",
        "LoanAmount": "Сума кредиту",
        "Loan_Amount_Term": "Термін кредитування",
        "Credit_History": "Кредитна історія",
        "Property_Area": "Тип місцевості",
        "LoanIncomeRatio": "Співвідношення кредиту до доходу",
    }

    # Групуємо коефіцієнти за початковими факторами
    grouped = {name: [] for name in factor_names}

    for feature, coefficient in zip(feature_names, coefficients):
        # Прибираємо префікси num__ та cat__
        feature = feature.split("__", 1)[-1]

        for name in factor_names:
            if feature == name or feature.startswith(name + "_"):
                grouped[name].append(abs(coefficient))
                break

    # Обчислюємо середнє абсолютне значення
    importance = []

    for name, values in grouped.items():
        if values:
            average = sum(values) / len(values)

            importance.append({
                "name": factor_names[name],
                "value": round(average, 6)
            })

    # Сортуємо за спаданням
    importance.sort(
        key=lambda item: item["value"],
        reverse=True
    )

    return render(
        request,
        "predictor/feature_importance.html",
        {"importance": importance}
    )

def prediction_detail(request, prediction_id):
    prediction = get_object_or_404(
        LoanPrediction,
        id=prediction_id
    )

    return render(
        request,
        "predictor/prediction_detail.html",
        {"prediction": prediction}
    )

def export_csv(request):
    predictions = LoanPrediction.objects.all().order_by("-created_at")

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )

    response["Content-Disposition"] = (
        'attachment; filename="loan_predictions.csv"'
    )

    # Для правильного відображення кирилиці в Excel
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")

    writer.writerow([
        "ID",
        "Дата",
        "Стать",
        "Сімейний стан",
        "Кількість утриманців",
        "Освіта",
        "Самозайнятість",
        "Дохід заявника",
        "Дохід співзаявника",
        "Сума кредиту",
        "Термін кредитування",
        "Кредитна історія",
        "Тип місцевості",
        "Кредит / дохід",
        "Ймовірність",
        "Результат"
    ])

    for item in predictions:
        writer.writerow([
            item.id,
            item.created_at.strftime("%d.%m.%Y %H:%M"),
            item.gender,
            item.married,
            item.dependents,
            item.education,
            item.self_employed,
            item.applicant_income,
            item.coapplicant_income,
            item.loan_amount,
            item.loan_amount_term,
            item.credit_history,
            item.property_area,
            round(
                item.loan_amount / (
                        item.applicant_income + item.coapplicant_income
                ), 4
            ) if (item.applicant_income + item.coapplicant_income) > 0 else "",
            round(item.probability * 100, 2),
            "Схвалено" if item.prediction == 1 else "Відхилено"
        ])

    return response

def export_excel(request):
    predictions = LoanPrediction.objects.all().order_by("-created_at")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Історія прогнозів"

    headers = [
        "ID", "Дата", "Стать", "Сімейний стан",
        "Кількість утриманців", "Освіта", "Самозайнятість",
        "Дохід заявника", "Дохід співзаявника",
        "Сума кредиту", "Термін кредитування",
        "Кредитна історія", "Тип місцевості",
        "Кредит / дохід", "Ймовірність (%)", "Результат"
    ]

    sheet.append(headers)

    for item in predictions:
        total_income = item.applicant_income + item.coapplicant_income

        ratio = (
            round(item.loan_amount / total_income, 4)
            if total_income > 0 else None
        )

        sheet.append([
            item.id,
            item.created_at.strftime("%d.%m.%Y %H:%M"),
            item.gender,
            item.married,
            item.dependents,
            item.education,
            item.self_employed,
            item.applicant_income,
            item.coapplicant_income,
            item.loan_amount,
            item.loan_amount_term,
            item.credit_history,
            item.property_area,
            ratio,
            round(item.probability * 100, 2),
            "Схвалено" if item.prediction == 1 else "Відхилено"
        ])

    # Оформлення заголовків
    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill(
            start_color="2864A8",
            end_color="2864A8",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    # Ширина стовпців
    for column in sheet.columns:
        letter = column[0].column_letter
        sheet.column_dimensions[letter].width = 22

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="loan_predictions.xlsx"'
    )

    workbook.save(response)

    return response
