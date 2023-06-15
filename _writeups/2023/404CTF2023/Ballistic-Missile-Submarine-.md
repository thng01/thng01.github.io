---
layout: writeup
category: 404CTF2023
chall_description: https://ctf.404ctf.fr/challenges#Ballistic%20Missile%20Submarine-105
points: 964
solves: Hardware, Radio-fréquences
tags: Hardware, Radio-fréquences
date: 2023-06-06
comments: false
---

## ## ## Challenge Description

![](../../../assets/CTFs/404CTF2023/radio_annonce.png)

We are given a file RadioLondres which is a raw data file, and a hint to use 192kHz.

## ## ## Solution

For this challenge, I use [Audacity](https://www.audacityteam.org/) to read and analyse the raw file. After having imported the file with the setting Stereo 192000 Hz, 32bit float and switch to spectrogram mode I saw this:
![audacity](E:\thng01.github.io\assets\CTFs\404CTF2023\radio_audacity.PNG)

This looks like a morse code to me. We can decode it with Cyberchef:

![flag](E:\thng01.github.io\assets\CTFs\404CTF2023\radio_flag.PNG)

So the ACCOLADE is the `{}` and we can see the format of the flag starting with 404CTF.

Let's submit it: `404CTF{P4UL_V3R14N3_35T_UN_MOR53_?}`
