import psycopg2
import jira

#Jira credential
jira_username = 'admiral.adam23@gmail.com'
jira_password = 'xQV5E1ru9GB9v0ULFNQs8E4D'
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
        

#addComment('1','BCC-1')


import json
from datetime import datetime

def insertNewTask(data):

    data = json.loads(data)
    
    
    id_jira = data['id'] #Task id
    task_name = data['key'] #Task name
    task_author = data['fields']['creator']['displayName'] #author task
    task_user = data['fields']['assignee']['displayName']
    start_date = str(datetime.today().strftime('%Y-%m-%d'))
    end_date = data['fields']['duedate']
    task_level = data['fields']['customfield_10016']
    
    #Status 
    #1 - на расмотрений у аналитика
    #2 - в ожида
    
    conn,cursor = connection()
    # cursor.execute(f"""insert into task_work (
    #                     id_jira, 
    #                     name, 
    #                     user_name, 
    #                     author, 
    #                     level,  
    #                     start_date,
    #                     end_date, 
    #                     status) values(
    #                          {id_jira},
    #                         '{task_name}',
    #                         '{task_user}',
    #                         '{task_author}',
    #                          {task_level},
    #                         '{start_date}',
    #                         '{end_date}',
    #                         1);""")
    # conn.commit()

    #Вытаскиваем когда разработчик может освободиться
    cursor.execute(f"""SELECT END_DATE FROM task_work WHERE user_name='{task_user}' AND END_DATE in (SELECT MAX(END_DATE) FROM task_work  WHERE user_name='{task_user}' AND STATUS=2)""")
    data = cursor.fetchone()
    
    user_date = str(data[0]).split(' ')[0]
    user_date = datetime.strptime(user_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    #Проверка пользователь занять или нет
    if(user_date<end_date):
        #Отправка комментарий
        result = addComment(f'Пользователь свободен и может взять задачу: {str(user_date)}',task_name)
        print(result)
    else:
        #Отправка комментарий
        result = addComment(f'Пользователь освободиться: {str(user_date)}',task_name)
        print(result)

        #Поиск других разработчиков
        cursor.execute(f"""SELECT u.fio, tw.end_date FROM task_work tw , users u WHERE u.username=tw.user_name and tw.user_name!='{task_user}' AND tw.END_DATE in (SELECT MIN(tw1.END_DATE) FROM task_work tw1  WHERE tw1.user_name!='{task_user}' AND tw1.STATUS=2)""")
        data = cursor.fetchone()

        if(data):
            dop_user_fio = data[0]
            dop_user_end_date = data[1]

            dop_user_end_date = str(dop_user_end_date).split(' ')[0]
            dop_user_end_date = datetime.strptime(dop_user_end_date, '%Y-%m-%d').date()

            print(str(user_date))
            print(str(dop_user_end_date))
            if(user_date>dop_user_end_date):
                print(f'Альтарнатива: {dop_user_fio}, освободиться {str(dop_user_end_date)}')
            else:
                print('Сверх работу создайте')
            
            
            
        

        
        
        
        
   
    





# data = '''{"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/10012", "id": 10012, "key": "HAC-11", "changelog": {"startAt": 0, "maxResults": 0, "total": 0, "histories": "None"}, "fields": {"statuscategorychangedate": "None", "issuetype": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issuetype/10005", "id": 10005, "description": "Stories track functionality or features expressed as user goals.", "iconUrl": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10315?size=medium", "name": "Story", "untranslatedName": "None", "subtask": "False", "fields": {}, "statuses": [], "namedValue": "Story"}, "timespent": "None", "customfield_10030": "None", "customfield_10031": "None", "project": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/project/10002", "id": 10002, "key": "HAC", "name": "Hackathon", "description": "None", "avatarUrls": {"48x48": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413", "24x24": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=small", "16x16": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=xsmall", "32x32": "https://hackathon2023bcc.atlassian.net/rest/api/2/universal_avatar/view/type/project/avatar/10413?size=medium"}, "issuetypes": "None", "projectCategory": "None", "email": "None", "lead": "None", "components": "None", "versions": "None", "projectTypeKey": "software", "simplified": "True"}, "fixVersions": [], "aggregatetimespent": "None", "customfield_10035": "None", "resolution": "None", "customfield_10036": "None", "customfield_10037": "None", "customfield_10027": "None", "customfield_10028": "None", "customfield_10029": "None", "resolutiondate": "None", "workratio": -1, "watches": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-11/watchers", "watchCount": 1, "isWatching": "False"}, "issuerestriction": {"issuerestrictions": {}, "shouldDisplay": "True"}, "lastViewed": "None", "created": 1674917801247, "customfield_10020": "None", "customfield_10021": "None", "customfield_10022": "None", "customfield_10023": "None", "priority": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/priority/3", "id": 3, "name": "Medium", "iconUrl": "https://hackathon2023bcc.atlassian.net/images/icons/priorities/medium.svg", "namedValue": "Medium"}, "customfield_10024": "None", "customfield_10025": "None", "customfield_10026": "None", "labels": [], "customfield_10016": 3.0, "customfield_10017": "None", "customfield_10018": {"hasEpicLinkFieldDependency": "False", "showField": "False", "nonEditableReason": {"reason": "PLUGIN_LICENSE_ERROR", "message": "Ссылка на родителя доступна только пользователям Jira Premium."}}, "customfield_10019": "0|i0002n:", "aggregatetimeoriginalestimate": "None", "timeestimate": "None", "versions": [], "issuelinks": [], "assignee": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d5161b8dd199a03e127ad7", "name": "None", "key": "None", "accountId": "63d5161b8dd199a03e127ad7", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "24x24": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "16x16": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png", "32x32": "https://secure.gravatar.com/avatar/e5151b4628efde9b738aa9c76a47568b?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FB-1.png"}, "displayName": "Baglanbek", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "updated": 1674917801247, "status": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/status/10003", "description": "", "iconUrl": "https://hackathon2023bcc.atlassian.net/", "name": "To Do", "untranslatedName": "None", "id": 10003, "statusCategory": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/statuscategory/2", "id": 2, "key": "new", "colorName": "blue-gray", "name": "New"}, "untranslatedNameValue": "None"}, "components": [], "timeoriginalestimate": "None", "description": "None", "customfield_10010": "None", "customfield_10014": "None", "timetracking": {"originalEstimate": "None", "remainingEstimate": "None", "timeSpent": "None", "originalEstimateSeconds": 0, "remainingEstimateSeconds": 0, "timeSpentSeconds": 0}, "customfield_10015": "None", "customfield_10005": "None", "customfield_10006": "None", "security": "None", "customfield_10007": "None", "customfield_10008": "None", "customfield_10009": "None", "aggregatetimeestimate": "None", "attachment": [], "summary": "Byak create Task 3", "creator": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "subtasks": [], "customfield_10040": "None", "customfield_10041": "None", "customfield_10042": "None", "reporter": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/user?accountId=63d21c5369c7ae3958d21c1a", "name": "None", "key": "None", "accountId": "63d21c5369c7ae3958d21c1a", "emailAddress": "None", "avatarUrls": {"48x48": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "24x24": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "16x16": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png", "32x32": "https://secure.gravatar.com/avatar/98e7652b2d663f1851ee2f8e575e5079?d=https%3A%2F%2Favatar-management--avatars.us-west-2.prod.public.atl-paas.net%2Finitials%2FM-0.png"}, "displayName": "Mayra", "active": "True", "timeZone": "Asia/Almaty", "groups": "None", "locale": "None", "accountType": "atlassian"}, "customfield_10043": "None", "customfield_10044": "None", "aggregateprogress": {"progress": 0, "total": 0}, "customfield_10001": "None", "customfield_10045": "None", "customfield_10046": "None", "customfield_10002": "None", "customfield_10047": "None", "customfield_10003": "None", "customfield_10004": "None", "customfield_10038": "None", "customfield_10039": "None", "environment": "None", "duedate": "2023-01-31", "progress": {"progress": 0, "total": 0}, "votes": {"self": "https://hackathon2023bcc.atlassian.net/rest/api/2/issue/HAC-11/votes", "votes": 0, "hasVoted": "False"}, "comment": {"maxResults": 0, "total": 0, "startAt": 0, "comments": [], "last": "False"}, "worklog": {"maxResults": 20, "total": 0, "startAt": 0, "worklogs": [], "last": "False"}}, "renderedFields": "None"}'''
# insertNewTask(data)



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

