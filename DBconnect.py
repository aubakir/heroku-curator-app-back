import psycopg2



jira_username = 'admiral.adam23@gmail.com'
jira_password = 'xQV5E1ru9GB9v0ULFNQs8E4D'
jira_url = 'https://hackathon2023bcc.atlassian.net'

def connection():
    conn = psycopg2.connect(database="pvaqhini",
                            host="kandula.db.elephantsql.com",
                            user="pvaqhini",
                            password="i66Ot-t0BkQ7nLbfx8-LYayqZq3TS-3m",
                            port="5432")

    cursor = conn.cursor()

    return conn,cursor



def checkUser(user,pw):
    conn,cursor = connection()
    cursor.execute(f"SELECT * FROM users where username='{user}' and password='{pw}'")
    
    answer = cursor.fetchone()
    print(answer)

    if(answer==None):
        return '0'
    elif(answer):
        return '1'
