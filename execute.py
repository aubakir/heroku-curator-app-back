import numpy as np
from sklearn.ensemble import RandomForestRegressor


def ai():
    ##############################Example##############################
    #Пример входных данных (важность, время выполнения в днях и занятость разработчика)
    # Sample input data (importance, time to complete in days, and developer busyness)
    X = np.array([[5, 15, 0.5], [3, 10, 0.7], [1, 1, 0.9], [2, 4, 0.2]])

    # сложность задачи/ время выполнений
    y = np.array([[4.7,13], [3.2,12], [1,5], [2.4,3]])



    ##############################Learning##############################
    # required time to complete the task
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)


    ##############################Execute##############################
    # Используйте модель, чтобы предсказать сложность новой задачи
    # Use the model to predict the difficulty of a new task
    new_task = np.array([[2, 3, 0.9]])
    predicted_difficulty = model.predict(new_task)
    print("Predicted difficulty of the new task:", predicted_difficulty[0])



def validJson(json):
    json = json.replace('\'','\"')
    json = json.replace(': None',': \"None\"')
    json = json.replace(': True',': \"True\"')
    json = json.replace(': False',': \"False\"')

    return json