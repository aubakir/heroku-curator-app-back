import DBconnect
import requests


#Отправка комментарий
def addComment(text,project_name):
    
    json = {"update": {"comment": [{"add": {"body": f"{text}"}}]}}

    try:
        response = requests.put(f'{DBconnect.jira_url}/rest/api/2/issue/{project_name}',verify=True,json=json,auth=(DBconnect.jira_username, DBconnect.jira_password))
        
        if(response.status_code==204):
            return {'answer':'success'}
        else:
            return {'answer':'error'}

    except Exception as e:
        print(str(e))
        return {'answer':str(e)}
        

#addComment('1','BCC-1')