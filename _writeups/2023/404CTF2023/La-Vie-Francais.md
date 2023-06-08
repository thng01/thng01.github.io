---
layout: writeup
category: 404CTF2023
chall_description: https://ctf.404ctf.fr/challenges#La%20Vie%20Fran%C3%A7aise-113
points: 956
solves: 81
tags: Web
date: 2023-06-06
comments: false
---

## ## Challenge Description

![Photo](../../../assets/CTFs/404CTF2023/annonce_laviefrancais.png "Annonce")

We have access to a website La Vie Francais (which was hinted that there exists a SQL server, since the admin banned sqlmap)

![Photo](../../../assets/CTFs/404CTF2023/laviefrancais1.png "Home page")

From the description and context of the challenge, it seems like we need to login as Madame Forestier to get the flag.



## ## Solution

In the beginning, I thought that we have to bypass the login form but it has a filter that reject all but the alphanumeric character with this error message: " Seuls les caractères alphanumériques sont autorisés "

However it was a rabbit hole!

![Photo](../../../assets/CTFs/404CTF2023/laviefrancais2.png "Login")

The real trick here is after we login: /account endpoint with the cookie uuid

![Photo](../../../assets/CTFs/404CTF2023/laviefrancais3.png "Account")

When we change the uuid to **` ' OR 1=1#'** the page no longer shows our name but jacquesrival instead.

![Photo](../../../assets/CTFs/404CTF2023/laviefrancais_jaques.png "SQL Test")

This confirmed that this section is vulnerable to SQLi. Now let's exploit it.

First thing first we need to find out the number of columns of the return table before using the UNION attack with the payload **`' UNION SELECT 1,2,3#'**

![Photo](../../../assets/CTFs/404CTF2023/laviefrancaisexploit1.png "SQL Test")

As we can see above, the field 1 is for the username, field 2 is some kind of message for the type user or admin maybe? and the 3 is perhap the uuid.

With this payload **`' UNION SELECT 1,database(),2'`** I found the database name **` usersdb`**

Then with **`' UNION SELECT table_name,2,3 from information_schema.tables where table_schema='usersdb'#`** I found the table **`users**

![Photo](../../../assets/CTFs/404CTF2023/laviefrancaisexploitusers.png "SQL Test")

For the columns name we use **`' UNION SELECT group_concat(column_name),2,3 from information_schema.columns where table_name='users'#**

![Photo](../../../assets/CTFs/404CTF2023/laviefrancaisexploitcolumns.png "SQL columns names")

Now all we need to do to leak the uuid of the owner and impersonate Madame Forestier!

**`' UNION SELECT group_concat(username,':',uuid SEPARATOR '#####'),2,3 from users#** leads us to the uuid of Madame Forestier madeleineforestier:8650580d3fe9431f8281b2212e9ff0de.

Change our uuid in cookie with Chrome Dev Tools (or modify it with Burp) and we can see the admin page.

![Photo](../../../assets/CTFs/404CTF2023/laviefrancaisfinal.png "GG")
