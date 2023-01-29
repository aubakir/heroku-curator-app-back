import psycopg2


#Jira credential
jira_username = 'admiral.adam23@gmail.com'
jira_password = 'W9IX7kCK7DrQBNzNzQzqB463'
jira_url = 'https://hackathon2023bcc.atlassian.net'


#DB postgresql connect
def connection():
    conn = psycopg2.connect(database="pvaqhini",
                            host="kandula.db.elephantsql.com",
                            user="pvaqhini",
                            password="i66Ot-t0BkQ7nLbfx8-LYayqZq3TS-3m",
                            port="5432")

    cursor = conn.cursor()

    return conn,cursor



#authorization user/pass check
def checkUser(user,pw):
    conn,cursor = connection()
    cursor.execute(f"SELECT * FROM users where username='{user}' and password='{pw}'")
    
    answer = cursor.fetchone()
    print(answer)

    cursor.close()
    if(answer==None):
        return '0'
    elif(answer):
        return '1'

import requests

#Отправка комментарий
def addComment(text,project_name):
    
    json = {"update": {"comment": [{"add": {"body": f"{text}"}}]}}

    try:
        response = requests.put(f'{jira_url}/rest/api/2/issue/{project_name}',verify=True,json=json,auth=(jira_username, jira_password))
        
        if(response.status_code==204):
            return {'answer':'success'}
        else:
            return {'answer':'error'}

    except Exception as e:
        print(str(e))
        return {'answer':str(e)}
        


            
def getMax(data):
    result = []
    n = 0
    for i in range(len(data)):
        if(n<data[i][2]):
            n = data[i][2]
            result = data[i]
    
    return result


import json
from datetime import datetime, timedelta



#Добавления исполнителя
def insertNewTask(data):

    data = json.loads(data)
    
    
    id_jira = data['id'] #Task id
    task_name = data['key'] #Task name
    task_author = data['fields']['creator']['displayName'] #author task
    task_user = data['fields']['assignee']['displayName']
    start_date = str(datetime.today().strftime('%Y-%m-%d'))
    end_date = data['fields']['duedate']
    
    #Status 
    #1 - на расмотрений у аналитика
    #2 - в ожида
    
    conn,cursor = connection()
    cursor.execute(f"""insert into task_work (
                        id_jira, 
                        name, 
                        user_name, 
                        author, 
                        start_date,
                        end_date, 
                        status) values(
                             {id_jira},
                            '{task_name}',
                            '{task_user}',
                            '{task_author}',
                            '{start_date}',
                            '{end_date}',
                            1);""")
    conn.commit()

    #Вытаскиваем когда разработчик может освободиться
    cursor.execute(f"""select u1.username,u1.fio, count(u1.username) from users u1, skills_user su1, skills_prog sp1
                where su1.tab_number = u1.user_id and su1.prog_id=sp1.id and su1.prog_id in (
                select su.prog_id from users u,skills_user su,skills_prog sp 
                where u.username='{task_user}' and u.user_id=su.tab_number and su.prog_id=sp.id and u.role='Разработчик') 
                and u1.role='Разработчик' and u1.username!='{task_user}' GROUP BY user_id;""")
    data = cursor.fetchall()
    
    user_date = str(data[0]).split(' ')[0]
    user_date = datetime.strptime(user_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    print(user_date,end_date)
    #Проверка пользователь занять или нет
    if(user_date<end_date):
        #Отправка комментарий
        end_date = start_date + timedelta(days=3)
        result = addComment(f'Аналитик свободен, время выполнений работы с {str(start_date)} по {str(end_date)}',task_name)
        print(result)
    else:
        #Отправка комментарий
        
        end_date = user_date + timedelta(days=3)
        result = addComment(f'Аналитик на текуищий момент занят. Готов взять в работу с {str(user_date)} по {str(end_date)}',task_name)
        print(result)

        

        


import json
from datetime import datetime,date

def updateTaskDevelop(data):

    data = json.loads(data)
    
    
    id_jira = data['id'] #Task id
    task_name = data['key'] #Task name
    task_author = data['fields']['creator']['displayName'] #author task
    task_user = data['fields']['assignee']['displayName'] #исполнитель
    task_day = data['fields']['customfield_10043'] #аналитик предположил время занятности в днях
    task_level = data['fields']['customfield_10043'] # сложность задачи (анализ аналитика)
    start_date = str(datetime.today().strftime('%Y-%m-%d')) #преполагаема дата начали
    end_date = date.today() + timedelta(days=int(task_day)) #преполагаема дата окончаний
    
    #Status 
    #1 - на расмотрений у аналитика
    #2 - в ожида
    
    conn,cursor = connection()
    cursor.execute(f"""update task_work set user_name='{task_user}', level={task_level}, start_date='{start_date}' , end_date='{str(end_date)}', status=1 where id_jira={id_jira}""")
    conn.commit()

    #Вытаскиваем когда разработчик может освободиться
    cursor.execute(f"""SELECT END_DATE FROM task_work WHERE user_name='{task_user}' AND END_DATE in (SELECT MAX(END_DATE) FROM task_work  WHERE user_name='{task_user}' AND STATUS=2)""")
    data = cursor.fetchone()
    
    user_date = str(data[0]).split(' ')[0]
    user_date = datetime.strptime(user_date, '%Y-%m-%d').date()
    

    #Проверка пользователь занять или нет
    if(user_date<end_date):
        #Отправка комментарий
        result = addComment(f'Пользователь свободен и может взять задачу: {str(user_date)}',task_name)
        print(result)
    else:
        user_end_date = user_date + timedelta(days=int(task_day))
        #Отправка комментарий
        print(f'Пользователь на данный момент занят. Задача может быть взято с {str(user_date)} по {str(user_end_date)}',task_name)
        result = addComment(f'Пользователь на данный момент занят. Задача может быть взято с {str(user_date)} по {str(user_end_date)}',task_name)
        print(result)

        #Поиск других разработчиков
        cursor.execute(f"""select u1.username,u1.fio, count(u1.username) from users u1, skills_user su1, skills_prog sp1
                where su1.tab_number = u1.user_id and su1.prog_id=sp1.id and su1.prog_id in (
                select su.prog_id from users u,skills_user su,skills_prog sp 
                where u.username='{task_user}' and u.user_id=su.tab_number and su.prog_id=sp.id and u.role='Разработчик') 
                and u1.role='Разработчик' and u1.username!='{task_user}' GROUP BY user_id""")
        data = cursor.fetchall()

        user_data = getMax(data)
        if(user_data):

            cursor.execute(f"""SELECT u.fio, tw.end_date FROM task_work tw , users u WHERE u.username=tw.user_name and tw.user_name='{user_data[0]}' AND tw.END_DATE in (SELECT MIN(tw1.END_DATE) FROM task_work tw1  WHERE tw1.user_name='{user_data[0]}' AND tw1.STATUS=2)""")
            data = cursor.fetchone()


            dop_user_fio = data[0]
            dop_user_end_date = str(data[1]).split(' ')[0]
            dop_user_end_date = datetime.strptime(dop_user_end_date, '%Y-%m-%d').date()

            print(str(dop_user_end_date))
            print(str(user_date))
            
            #Если другой пользователь свободен раньше
            if(dop_user_end_date<user_date):

                dop_user_start_date = dop_user_end_date + timedelta(days=1)
                dop_user_end_date = dop_user_start_date + timedelta(days=int(task_day))

                print(f'{dop_user_fio} наиболее схожий по скиллам {task_user}. И он можете взять в работу с {dop_user_start_date} по {dop_user_end_date}')
                result = addComment(f'{dop_user_fio} наиболее схожий по скиллам {task_user}. И он можете взять в работу с {dop_user_start_date} по {dop_user_end_date}',task_name)
            else:

                print(f'Система предлагает создать сверх план для пользователя {task_user}')
                result = addComment(f'Система предлагает создать сверх план для пользователя {task_user}',task_name)

    return {'answer':'success'}
            
        
   
    




# #CREATE
# data = '''{"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/10014", "id": 10014, "key": "HAC-13", "changelog": {"startAt": 0, "maxResults": 0, "total": 0, "histories": "None"}, "fields": {"statuscategorychangedate": "2023-01-29T10:37:39.918+0600", "issuetype": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issuetype/10005", "id": 10005, "description": "Stories track functionality or features expressed as user goals.", "iconUrl": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10315?size=medium", "name": "Story", "untranslatedName": "None", "subtask": "False", "fields": {}, "statuses": [], "namedValue": "Story"}, "timespent": "None", "customfield_10030": "None", "customfield_10031": "None", "project": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/project/10002", "id": 10002, "key": "HAC", "name": "Hackathon", "description": "None", "avatarUrls": {"48x48": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413", "24x24": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=small", "16x16": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=xsmall", "32x32": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=medium"}, "issuetypes": "None", "projectCategory": "None", "email": "None", "lead": "None", "components": "None", "versions": "None", "projectTypeKey": "software", "simplified": "True"}, "fixVersions": [], "aggregatetimespent": "None", "resolution": "None", "customfield_10035": "None", "customfield_10036": "None", "customfield_10037": "None", "customfield_10027": "None", "customfield_10028": "None", "customfield_10029": "None", "resolutiondate": "None", "workratio": -1, "lastViewed": "None", "issuerestriction": {"issuerestrictions": {}, "shouldDisplay": "True"}, "watches": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-13/watchers", "watchCount": 1, "isWatching": "False"}, "created": 1674967059597, "customfield_10020": "None", "customfield_10021": "None", "customfield_10022": "None", "customfield_10023": "None", "priority": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/priority/3", "id": 3, "name": "Medium", "iconUrl": "https://hackathon2023bcc.atlassian.net/images/icons/priorities/medium.svg", "namedValue": "Medium"}, "customfield_10024": "None", "customfield_10025": "None", "customfield_10026": "None", "labels": [], "customfield_10016": "None", "customfield_10017": "None", "customfield_10018": {"hasEpicLinkFieldDependency": "False", "showField": "False", "nonEditableReason": {"reason": "PLUGIN_LICENSE_ERROR", "message": "Ссылка на родителя доступна только пользователям Jira Premium."}}, "customfield_10019": "0|i00033:", "timeestimate": "None", "aggregatetimeoriginalestimate": "None", "versions": [], "issuelinks": [], "assignee": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "updated": 1674967059597, "status": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/status/10003", "description": "", "iconUrl": "https://hackathon2023bcc.atlassian.net/", "name": "To Do", "untranslatedName": "None", "id": 10003, "statusCategory": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/statuscategory/2", "id": 2, "key": "new", "colorName": "blue-gray", "name": "New"}, "untranslatedNameValue": "None"}, "components": [], "timeoriginalestimate": "None", "description": "None", "customfield_10010": "None", "customfield_10014": "None", "timetracking": {"originalEstimate": "None", "remainingEstimate": "None", "timeSpent": "None", "originalEstimateSeconds": 0, "remainingEstimateSeconds": 0, "timeSpentSeconds": 0}, "customfield_10015": "None", "customfield_10005": "None", "customfield_10006": "None", "customfield_10007": "None", "security": "None", "customfield_10008": "None", "attachment": [], "customfield_10009": "None", "aggregatetimeestimate": "None", "summary": "Its a new down", "creator": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21dbc8c3018ca8a1c33d3", "name": "None", "key": "None", "accountId": "63d21dbc8c3018ca8a1c33d3", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "24x24": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "16x16": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "32x32": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png"}, "displayName": "Smith", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "subtasks": [], "customfield_10040": "None", "customfield_10041": "None", "customfield_10042": "None", "reporter": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21dbc8c3018ca8a1c33d3", "name": "None", "key": "None", "accountId": "63d21dbc8c3018ca8a1c33d3", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "24x24": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "16x16": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "32x32": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png"}, "displayName": "Smith", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "customfield_10043": "None", "customfield_10044": "None", "aggregateprogress": {"progress": 0, "total": 0}, "customfield_10001": "None", "customfield_10045": "None", "customfield_10046": "None", "customfield_10002": "None", "customfield_10003": "None", "customfield_10047": "None", "customfield_10004": "None", "customfield_10038": "None", "customfield_10039": "None", "environment": "None", "duedate": "2023-01-31", "progress": {"progress": 0, "total": 0}, "votes": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-13/votes", "votes": 0, "hasVoted": "False"}, "comment": {"maxResults": 0, "total": 0, "startAt": 0, "comments": [], "last": "False"}, "worklog": {"maxResults": 20, "total": 0, "startAt": 0, "worklogs": [], "last": "False"}}, "renderedFields": "None"}'''
# insertNewTask(data)



# #UPDATE
# data = '''{"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/10014", "id": 10014, "key": "HAC-13", "changelog": {"startAt": 0, "maxResults": 0, "total": 0, "histories": "None"}, "fields": {"statuscategorychangedate": "2023-01-29T10:37:39.918+0600", "issuetype": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issuetype/10005", "id": 10005, "description": "Stories track functionality or features expressed as user goals.", "iconUrl": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10315?size=medium", "name": "Story", "untranslatedName": "None", "subtask": "False", "fields": {}, "statuses": [], "namedValue": "Story"}, "timespent": "None", "customfield_10030": "None", "project": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/project/10002", "id": 10002, "key": "HAC", "name": "Hackathon", "description": "None", "avatarUrls": {"48x48": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413", "24x24": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=small", "16x16": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=xsmall", "32x32": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=medium"}, "issuetypes": "None", "projectCategory": "None", "email": "None", "lead": "None", "components": "None", "versions": "None", "projectTypeKey": "software", "simplified": "True"}, "customfield_10031": "None", "fixVersions": [], "aggregatetimespent": "None", "resolution": "None", "customfield_10035": "None", "customfield_10036": "None", "customfield_10037": "None", "customfield_10027": "None", "customfield_10028": "None", "customfield_10029": "None", "resolutiondate": "None", "workratio": -1, "watches": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-13/watchers", "watchCount": 2, "isWatching": "False"}, "lastViewed": "2023-01-29T11:19:41.715+0600", "issuerestriction": {"issuerestrictions": {}, "shouldDisplay": "True"}, "created": 1674967059597, "customfield_10020": "None", "customfield_10021": "None", "customfield_10022": "None", "priority": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/priority/3", "id": 3, "name": "Medium", "iconUrl": "https://hackathon2023bcc.atlassian.net/images/icons/priorities/medium.svg", "namedValue": "Medium"}, "customfield_10023": "None", "customfield_10024": "2023-01-29T10:44:30.345+0600", "customfield_10025": "None", "customfield_10026": "None", "labels": [], "customfield_10016": "None", "customfield_10017": "None", "customfield_10018": {"hasEpicLinkFieldDependency": "False", "showField": "False", "nonEditableReason": {"reason": "PLUGIN_LICENSE_ERROR", "message": "Ссылка на родителя доступна только пользователям Jira Premium."}}, "customfield_10019": "0|i00033:", "aggregatetimeoriginalestimate": "None", "timeestimate": "None", "versions": [], "issuelinks": [], "assignee": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d5161b8dd199a03e127ad7", "name": "None", "key": "None", "accountId": "63d5161b8dd199a03e127ad7", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "24x24": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "16x16": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "32x32": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png"}, "displayName": "Baglanbek", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "updated": 1674969594020, "status": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/status/10003", "description": "", "iconUrl": "https://hackathon2023bcc.atlassian.net/", "name": "To Do", "untranslatedName": "None", "id": 10003, "statusCategory": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/statuscategory/2", "id": 2, "key": "new", "colorName": "blue-gray", "name": "New"}, "untranslatedNameValue": "None"}, "components": [], "timeoriginalestimate": "None", "description": "None", "customfield_10010": "None", "customfield_10014": "None", "customfield_10015": "None", "timetracking": {"originalEstimate": "None", "remainingEstimate": "None", "timeSpent": "None", "originalEstimateSeconds": 0, "remainingEstimateSeconds": 0, "timeSpentSeconds": 0}, "customfield_10005": "None", "customfield_10006": "None", "customfield_10007": "None", "security": "None", "customfield_10008": "None", "aggregatetimeestimate": "None", "customfield_10009": "None", "attachment": [], "summary": "Its a new down", "creator": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21dbc8c3018ca8a1c33d3", "name": "None", "key": "None", "accountId": "63d21dbc8c3018ca8a1c33d3", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "24x24": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "16x16": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "32x32": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png"}, "displayName": "Smith", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "subtasks": [], "customfield_10040": "None", "customfield_10041": "None", "customfield_10042": "None", "customfield_10043": "5", "reporter": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21dbc8c3018ca8a1c33d3", "name": "None", "key": "None", "accountId": "63d21dbc8c3018ca8a1c33d3", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "24x24": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "16x16": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png", "32x32": "https://secure.gravatar.com/avatar/3c717695e72499e00abb9942254171be?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FS-3.png"}, "displayName": "Smith", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "aggregateprogress": {"progress": 0, "total": 0}, "customfield_10044": "None", "customfield_10001": "None", "customfield_10045": "None", "customfield_10046": "None", "customfield_10002": "None", "customfield_10047": "None", "customfield_10003": "None", "customfield_10004": "None", "customfield_10038": "None", "customfield_10039": "None", "environment": "None", "duedate": "2023-01-31", "progress": {"progress": 0, "total": 0}, "votes": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-13/votes", "votes": 0, "hasVoted": "False"}, "comment": {"maxResults": 2, "total": 2, "startAt": 0, "comments": [{"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/10014/comment/10006", "id": 10006, "author": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "body": "Пользователь освободиться: 2023-02-20", "renderedBody": "None", "updateAuthor": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "created": 1674967470345, "updated": 1674967470345, "visibility": "None"}, {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/10014/comment/10007", "id": 10007, "author": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "body": "Аналитик на текуйщий момент занят. Готов взять в работу с 2023-02-20 по 2023-02-23", "renderedBody": "None", "updateAuthor": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "created": 1674969420450, "updated": 1674969420450, "visibility": "None"}], "last": "False"}, "worklog": {"maxResults": 20, "total": 0, "startAt": 0, "worklogs": [], "last": "False"}}, "renderedFields": "None"}'''
# updateTask(data)



'''
CREATE TABLE task_waiting (
	id serial PRIMARY KEY,
    id_jira integer,
    name VARCHAR (100),
    user_name VARCHAR (100),
	author VARCHAR (100),        
    level integer,
    end_date TIMESTAMP,
	status integer 
);
'''

