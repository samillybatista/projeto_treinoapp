import json

# Carregar o JSON dos treinos
with open("../Data/set.json", "r") as file:
    data = json.load(file)


# Iterar sobre cada treino no cronograma
for date, treino in data["schedule"].items():
    print(f"\nData do treino: {date}")
    print(f"Tipo de treino: {treino['type']}")

    # Iterar sobre os exercícios
    for exercise in treino["exercises"]:
        # Exibir categoria do exercício
        category = exercise.get("category", "Sem categoria")
        print(f"\nCategoria: {category}")

        # Exibir detalhes se existirem
        if "details" in exercise and exercise["details"]:
            print(f"Detalhes: {exercise['details']}")

        # Verificar e exibir exercícios específicos (caso existam)
        if "sets" in exercise:
            print("Exercícios:")
            for item in exercise["sets"]:
                print(f" - {item}")
