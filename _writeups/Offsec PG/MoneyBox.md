---
layout: writeup
category: Offsec-PG
section: Labs
chall_description: 
points: 
solves: 
tags: 
date: 2026-03-19
comments: false
---

## ## Challenge Description

A medium box with some steganography and SSH bruteforcing. 

## ## Enumeration

As usual I started with nmap for port scanning using following command:

```
nmap -sC -sV -A -p- [ Box IP ]
#Got 21, 22 and 80 openned => ftp, ssh and http
```

With -sC option nmap reveal the ftp allowed anonymous login, so I take a look at port 21 with username anonymous and leave the password empty. There I found a `trytofind.jpg`



![](../..//\assets\CTFs\Offsec-PG/MoneyBox/ftp.PNG)

When inspecting the jpg, there are several steganography technique to hide information in jpg, but seems like I was stuck there for now, so I move on with the port 80. 

## The HTTP service

Next I ran ffuf on the site, finding endpoint /blogs, and by juggling around the source, I found a secret **3xtr4ctd4t4**. Hmm wonder what this might be. If you are familiar with steganography tools, you will know about **steghide** and how to hide data into jpg with password. So we have all we need:

![](../..//\assets\CTFs\Offsec-PG/MoneyBox/key.PNG)

```
steghide extract -p 3xtr4ctd4t4 -sf trytofind.jpg
=> data.txt	
```

![](../..//\assets\CTFs\Offsec-PG/MoneyBox/steghide.PNG)

Seems like 2 devs are trying to communicate, and now we know the password of renu is a weak one.

## SSH bruteforce

So let's fire up **Hydra** and get our access. For ssh I use this command:

``` 
hydra -l renu -P Path_to_rockyou.txt [ Box IP ] ssh
```

![](../..//\assets\CTFs\Offsec-PG/MoneyBox/sshbruteforece.PNG)

So we got our access into the box, where I got my first flag. 

## Privilege Escalation

While looking around for a PE pivot, I found another user called `lily`, and they listed `renu` as their authorized_keys.

> The `authorized_keys` file is a server-side configuration file used in SSH public key authentication to list the public keys that are permitted to log into a user account. 
>
> Each line contains a single public key, consisting of space-separated fields: options (optional), key type, base64-encoded key string, and an optional comment. Lines starting with `#` are treated as comments.

![](../..//\assets\CTFs\Offsec-PG/MoneyBox/lily.PNG)

As `lily` with sudo -l, I found a PE threat:  

> (ALL : ALL) NOPASSWD: /usr/bin/perl means: As lily,I can run sudo without their password, and execute  exactly/user/bim/perl as any user and any group

<img src="../..//\assets\CTFs\Offsec-PG/MoneyBox/proof.PNG" />

So I spawned a shell and get the proof.txt
