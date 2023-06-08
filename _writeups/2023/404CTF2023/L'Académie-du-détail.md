---
layout: writeup
category: 404CTF2023
chall_description: https://ctf.404ctf.fr/challenges#L'Acad%C3%A9mie%20du%20d%C3%A9tail-18
points: 200
solves: 360
tags: Web
date: 2023-06-06
comments: false
---

## ## Challenge Description

![Photo](../../../assets/CTFs/404CTF2023/annonce_academie.png "Annonce")

This is a Web challenge, and this time we have a site of the Academie Francais annoucing their new member, but not has been publicly accessible yet. Here is the home page:

![Photo](../../../assets/CTFs/404CTF2023/academie_homepage.png "Home page")



## ## Solution

First thing first, let's head to the login page. I tried to login as admin and it says wrong password.

![Photo](../../../assets/CTFs/404CTF2023/academie_admin.png "Login page")

Since there is not register page, I tried to login as "thng01" with a random password. I logged in successfully!

![Photo](../../../assets/CTFs/404CTF2023/acadedmie_login as thng01.png "Logged in")

But as we can guess, the account thng01 doesn't have access to information of the new member at /membres. This indicates that we need to impersonate the admin account.

While capturing the requests with Burp, I saw a cookie **access-token** and it was sent everytime I make a request. the token was 140 bytes long and looked like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkcyIsImV4cCI6MTY4NjIxMDc0NX0.KXBGSXhBbKimis4TXLsH5jQCIEc6Q7xCDV3UM0AkEvU
```

This is a **JWT** (JSON Web Token) 

> JSON Web Token (JWT) is an open standard (RFC 7519) that  defines a compact and self-contained way for securely transmitting  information between parties as a JSON object. This information can be  verified and trusted because it is digitally signed. JWTs can be signed  using a secret (with the HMAC algorithm) or a public/private key pair  using RSA or ECDSA.*	

A JWT has 3 parts, seperated by dots (.), namely Header, Payload and Signature. We can decode our **access-token** at [jwt.io](https://jwt.io/) as we can see here. The algorithm is HS256 and the payload is my username thng01 and expiry time. The third part is the signature signed by the application.

![Photo](../../../assets/CTFs/404CTF2023/acadedmie_tokenthng01.png "jwt.io")

Some applications support NONE Algorithm, which makes them vulnerable to a JWT None algorithm Attack and help us bypass their signature check since there is no algorithm is used to sign the JWT . To exploit this, we can used [JWT Burp Extension](https://portswigger.net/bappstore/f923cbf91698420890354c1d8958fee6) as I can change the token on the go with Burp. 

And with the username **admin**, algorithm **None** and no signature, my request to /membres as **admin** allowed us to get the flag!

![Photo](../../../assets/CTFs/404CTF2023/acadedmie_jwt.png "FLAG")

That's all for the challenge. See you around!
