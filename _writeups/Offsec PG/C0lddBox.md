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

A beginner-friendly Wordpress box with simple PE challenge. This is a easy box so I don't write too many details on this.

## ## Solution

As nmap reveal a http port opened with Wordpress running with some dev mentioned (Hugo,C0ldd) at /hidden:

![](../..//\assets\CTFs\Offsec-PG/C0ldd/hidden.PNG)

So I tried to enumerate all the users on the box:

```
wpscan --url [IP_box] --enumerate u
```

I got c0ldd, hugo and philip. 
![](../..//\assets\CTFs\Offsec-PG/C0ldd/user enum.PNG)



Next thing we should do is bruteforcing these users with:

```
wpscan — url [IP_box] -U c0ldd,hugo,philip -P /usr/share/wordlists/rockyou.txt
```

and got access to the Wordpress admin panel:
![](../..//\assets\CTFs\Offsec-PG/C0ldd/cred.PNG)



As an admin I can change the 404.php template in **Appearance>Editor** to a [PHP reverse shell](https://github.com/pentestmonkey/php-reverse-shell) and trigger a 404 code by searching for a non-existing article. With this I got a shell as www-data:

![](../..//\assets\CTFs\Offsec-PG/C0ldd/shell.PNG)

In the search for credentials `c0ldd` as the user.txt flag is in /home/c0ldd, wp-config.php contains a password that worth trying for and it worked. A simple switch to c0ldd allowed us to get user flag.

Next is to get the root access. The first thing I would try everytime is to check sudo privilege with `sudo -l`, revealing access to usr/bin/vim as root. All we need to do is go to https://gtfobins.org/, learn how to spawn a shell with vim and read that /root/proof.txt flag.

