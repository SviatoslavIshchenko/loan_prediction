from django import forms

class LoanPredictionForm(forms.Form):

    Gender = forms.ChoiceField(
        label="Стать",
        choices=[
            ("Male", "Чоловіча"),
            ("Female", "Жіноча")
        ]
    )

    Married = forms.ChoiceField(
        label="Сімейний стан",
        choices=[
            ("Yes", "Одружений / заміжня"),
            ("No", "Неодружений / незаміжня")
        ]
    )

    Dependents = forms.ChoiceField(
        label="Кількість утриманців",
        choices=[
            ("0", "0"),
            ("1", "1"),
            ("2", "2"),
            ("3+", "3 або більше")
        ]
    )

    Education = forms.ChoiceField(
        label="Освіта",
        choices=[
            ("Graduate", "Вища освіта"),
            ("Not Graduate", "Без вищої освіти")
        ]
    )

    Self_Employed = forms.ChoiceField(
        label="Самозайнятість",
        choices=[
            ("Yes", "Так"),
            ("No", "Ні")
        ]
    )

    ApplicantIncome = forms.FloatField(
        label="Дохід заявника",
        min_value=0
    )

    CoapplicantIncome = forms.FloatField(
        label="Дохід співзаявника",
        min_value=0,
        initial=0
    )

    LoanAmount = forms.FloatField(
        label="Сума кредиту",
        min_value=0.01
    )

    Loan_Amount_Term = forms.ChoiceField(
        label="Термін кредитування (місяців)",
        choices=[
            (str(months), f"{months} місяців")
            for months in [
                12, 36, 60, 84, 120, 180,
                240, 300, 360, 480
            ]
        ],
        initial="360"
    )

    Credit_History = forms.ChoiceField(
        label="Кредитна історія",
        choices=[
            ("1", "Позитивна"),
            ("0", "Негативна")
        ]
    )

    Property_Area = forms.ChoiceField(
        label="Тип місцевості",
        choices=[
            ("Urban", "Місто"),
            ("Semiurban", "Передмістя"),
            ("Rural", "Сільська місцевість")
        ]
    )

    def clean(self):
        cleaned_data = super().clean()

        applicant_income = cleaned_data.get("ApplicantIncome")
        coapplicant_income = cleaned_data.get("CoapplicantIncome")

        if (
            applicant_income is not None
            and coapplicant_income is not None
            and applicant_income + coapplicant_income <= 0
        ):
            raise forms.ValidationError(
                "Сукупний дохід повинен бути більшим за нуль."
            )

        return cleaned_data
