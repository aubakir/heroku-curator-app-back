# import numpy as np
# from sklearn.ensemble import RandomForestRegressor


# def ai():
#     ##############################Example##############################
#     #Пример входных данных (важность, время выполнения в днях и занятость разработчика)
#     # Sample input data (importance, time to complete in days, and developer busyness)
#     X = np.array([[5, 15, 0.5], [3, 10, 0.7], [1, 1, 0.9], [2, 4, 0.2]])

#     # сложность задачи/ время выполнений
#     y = np.array([[4.7,13], [3.2,12], [1,5], [2.4,3]])



#     ##############################Learning##############################
#     # required time to complete the task
#     model = RandomForestRegressor(n_estimators=100)
#     model.fit(X, y)


#     ##############################Execute##############################
#     # Используйте модель, чтобы предсказать сложность новой задачи
#     # Use the model to predict the difficulty of a new task
#     new_task = np.array([[2, 3, 0.9]])
#     predicted_difficulty = model.predict(new_task)
#     print("Predicted difficulty of the new task:", predicted_difficulty[0])



import psycopg2

#DB postgresql connect
def connection():
    conn = psycopg2.connect(database="pvaqhini",
                            host="kandula.db.elephantsql.com",
                            user="pvaqhini",
                            password="i66Ot-t0BkQ7nLbfx8-LYayqZq3TS-3m",
                            port="5432")

    cursor = conn.cursor()

    return conn,cursor

json_ex = {'username':'','fio':'','role':'','all_date_customer':'','get_date_developer':'','task_difficulty':'','user_rating':''}

def sumRating():

    

    data = []

    conn,cursor = connection()
    cursor.execute(f"SELECT username,fio,role FROM users where role is not null and role != 'Бизнес'")
    username = cursor.fetchall()

    #Сколько дней он сэкономил или потратил
    get_date = ''
    
    #средний сложность задачи
    

    #Общая время которая предполагалась 
    
    

    for user in username:

        obj_date = ''
        level = 0
        level_fact = 0

        json = {'username':'','fio':'','role':'','all_date_customer':'','get_date_developer':'','task_difficulty':'','user_rating':''}

        json['username'] = user[0]
        json['fio'] = user[1]
        json['role'] = user[2]


        #start_date,end_date,real_end_date,level
        cursor.execute(f"select * from task_work where user_name='{user[0]}' and status=3 and start_date >= '2022-10-01 00:00:00' and end_date <= '2023-01-01 00:00:00'")
        allDate = cursor.fetchall()

        for date in allDate:
            start_date = date[6]
            end_date = date[7]
            real_end_date = date[8]
            level = level + date[9] + 1
            level_fact = level_fact + date[9]
            
            #Предпологаема время
            date_customer = start_date - end_date
            #Время за который закончил разработчик
            date_developer = start_date - real_end_date

            #Считаем общию дату которая предпологалась
            if(obj_date==''):
                obj_date = date_customer
            else:
                obj_date = obj_date + date_customer


            #Если разработчик раньше закончил задачу
            if(date_customer<date_developer):
                date_plus = (date_customer*-1)-(date_developer*-1)
                if(get_date==''):
                    get_date = date_plus
                else:
                    get_date = get_date + date_plus
                
                

            #Если разработчик позже закончил задачу
            elif(date_customer>date_developer):
                date_plus = (date_customer*-1)-(date_developer*-1)
                if(get_date==''):
                    get_date = get_date
                else:
                    get_date = get_date + date_plus

        if(level):
            #per = ('СРЕДНЯЯ СЛОЖНОСТЬ ЗАДАЧИ ЗА КВАРТАЛ'/'ДНИ КОТОРЫЕ БЫЛИ ВЫДАНЫ В ОБЩЕМ') * (100 + ('ДНИ КОТОРЫЙ БЫЛО СЭКОНОМЛЕНО'/100)/'ДНИ КОТОРЫЕ БЫЛИ ВЫДАНЫ В ОБЩЕМ')
            
            per = 100 + (int(str(get_date).split(' ')[0])*100)/(int(str(obj_date).split(' ')[0])*-1)
            
            json['all_date_customer'] = str(obj_date)
            json['get_date_developer'] = str(get_date)
            json['task_difficulty'] = str(level_fact/(len(allDate)))
            json['user_rating'] = str((level/(len(allDate)))*(per/100))

            print('общию дату которая предпологалась',str(obj_date))
            print('сколько сэкономил',str(get_date))
            print('средний сложность задачи',str(level/(len(allDate))))
            print('Рейтинг за этот квартал',(level/(len(allDate)))*(per/100))
    
            data.append(json)
    
    return data




