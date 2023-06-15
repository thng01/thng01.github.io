---
layout: writeup
category: 404CTF2023
chall_description: https://ctf.404ctf.fr/challenges#Un%20vol%20?%20-41
points: 787
solves: 177
tags: OSINT
date: 2023-06-06
comments: false
---

[Link to challenges](https://ctf.404ctf.fr/challenges#Un%20vol%20?%20-41)

## ## Challenge Description

![Photo](../../../assets/CTFs/404CTF2023/annonce_unvol.png "Annonce")

This OSINT challenge requires us to find out where Arsène Lupin hides his loot, given 6 photos of him in Paris. We shall examine those photos one by one. The flag format is **`404CTF{hiding_place}`**

## ## Solution

Let's take a look at the first picture

![Photo](../../../assets/CTFs/404CTF2023/Arsene_01.png)

The location of this photo can be found easily on Google Maps with the name of the Association Building, and street name. 

![Photo](../../../assets/CTFs/404CTF2023/Arsene_02.png)

For the second one, it was a bit different since the Street view of Maps is outdated and doesn't have the construction, but with the street name + 2 building, 1 of bricks 1 in white is enough for us to find.

I keep on finding the location of the rest and pin them on the map. Since they are all clear with names and signs, we should have no problem finding their location at all.

![Photo](../../../assets/CTFs/404CTF2023/Arsene_03.png)

![Photo](../../../assets/CTFs/404CTF2023/Arsene_04.png)

![Photo](../../../assets/CTFs/404CTF2023/Arsene_05.png)

![Photo](../../../assets/CTFs/404CTF2023/Arsene_06.png)

And finally, we need to figure out the relation among those pins. Here is what I found:

![Photo](../../../assets/CTFs/404CTF2023/mapsreal.png)

After having linked all the pins with black line, I realized that perhap Lupin is trying to create an emerald shape (I tried to fill in the rest with red lines), so I looked for the missing pins but it was pointless. Then I decided to go for the center and voilà, it leads us to "La tombe de Frédéric Chopin"  (Green elipse above).

So, the flag is **`404CTF{la_tombe_de_frederic_chopin}`**
