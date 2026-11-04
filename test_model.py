from predictor.ml_service import model, features, threshold

print("Модель успішно завантажена!")

print("\nТип моделі:")
print(type(model))

print("\nКількість предикторів:")
print(len(features))

print("\nСписок предикторів:")
for i, feature in enumerate(features, start=1):
    print(f"{i}. {feature}")

print("\nПоріг класифікації:")
print(threshold)

print("\nЕтапи Pipeline:")
print(model.named_steps.keys())
