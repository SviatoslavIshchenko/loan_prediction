from django.db import models

class LoanPrediction(models.Model):

    # Характеристики позичальника
    gender = models.CharField(max_length=10)
    married = models.CharField(max_length=5)
    dependents = models.CharField(max_length=5)
    education = models.CharField(max_length=20)
    self_employed = models.CharField(max_length=5)

    # Фінансові характеристики
    applicant_income = models.FloatField()
    coapplicant_income = models.FloatField()
    loan_amount = models.FloatField()
    loan_amount_term = models.IntegerField()

    # Кредитна історія та місцевість
    credit_history = models.IntegerField()
    property_area = models.CharField(max_length=20)

    # Результати прогнозування
    probability = models.FloatField()
    prediction = models.IntegerField()

    # Дата та час створення прогнозу
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def loan_income_ratio(self):
        total_income = (
                self.applicant_income + self.coapplicant_income
        )

        if total_income > 0:
            return round(self.loan_amount / total_income, 4)

        return None

    @property
    def probability_percent(self):
        return round(self.probability * 100, 2)

    def __str__(self):
        return f"Заявка №{self.id}"

