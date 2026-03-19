---
layout: writeup
category: Ph0wnCTF-2026-Intro
chall_description: 
points: 
solves: 
tags: OSINT
date: 2026-03-19
comments: false
---

## ## Challenge Description

A photo from `picolecroco` going surfing for Xmas vacation and had spiny lobster for dinner, we are asked to find out what did he had for drink at dinner and its price.

The flag takes form `ph0wn{NAME_AMOUNT_CURRENCY}`

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro/pico1.png) 

## ## Solution

We have the username so we can start with Whatsmyname and found his Instagram, X and some other accounts.

Seems like he is active on his Instagram:
![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro/picox.png)

On his Instagram we can find the uncropped version of the challenge photo:

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\pico2.png)

He also writing about "Caribbean wave", and Pacific on 4WD. So I assume that he spent his vacation in a country that is famous for surfing and get both access to Caribbean and Pacific ocean. and if you zoom out the background you will see a welcome panel with P-something G-something:
![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\pico3.png)



A bit of research lead me to the `Playa Grande` at Costa Rica which satisfies all our criteria.

We can let it sit there for a while.



Next: The 25 December he had spiny lobster with Gin, Orange Bitter, Red Vermouth and Green Charteuse. So for drink he had `Bijou`, a cocktail made from those ingredients. He also talked about having this dinner at a nearby restaurant. 

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\pico4.png)

So what we need to do is: Find a restaurant near the surfing beach at Playa Grande, Costa Rica that serve spiny lobster and bijou cocktail. After a bit of searching with google maps "spiny lobster near Playa Grande bijou" I found `The Sidebar at Playa Langosta` . It's just now that I realize the hint "sidecar" in his Instagram post. Now just head to the menu and get the flag:

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\menu.png)



So the flag is  **`ph0wn{bijou_10500_CRC}`**.
