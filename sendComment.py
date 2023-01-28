import requests
import json



def send(text):
    data = {
            "update": {
                "comment": [
                    {
                        "add": {
                        "body": f"{text}"
                        }
                    }
                ]
            }
            }

    headers = {'Content-type': 'application/json'}
