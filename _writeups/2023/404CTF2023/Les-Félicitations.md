---
layout: writeup
category: 404CTF2023
chall_description: https://ctf.404ctf.fr/challenges#Les%20F%C3%A9licitations-46
points: 911
solves: 110
tags: Stegnography
date: 2023-06-06
comments: false
---

## ## Challenge Description

We are given a poem this time and required to find a hidden congralutation.

Tous étaient réunis dans la salle,

Criblant leur feuille de mots et posant leurs esprits sur papier.

Très encouragés par le déroulement des opérations,

Il suffisait simplement de les regarder pour voir leur dévotion

.-.. . -.-. --- -.. . -- --- .-. ... . -.-. . ... - ... -.-- -- .--. .-

Beaucoup d'entre eux étaient fiers de leur oeuvre

Cillant à peine quand dehors, un monstre jappait

Fierté mène cependant à orgueil

Et n'oubliez pas qu'orgueil mène à perte.

-- .- .. ... .-.. .- -.-. .- ... . .-. - .- .-. .. . -. .... .- .... .-

Juste au moment où leurs travaux allaient finir,

Hors du laboratoire, un cri retentissant fut émis

Peu d'humains avaient entendu ce genre de cris.

Exténués par cette énième attaque, les scientifiques se remirent au travail.

Flag Format: **`404CTF{VosSuperFélicitations}`**

## ## Solution

The first thing I see in this poem is the Morse code. However the Morse code gave me LECODEMORSECESTSYMPAMAISLACASERTARIENHAHA, which directly told us that the morse code is not the right solution. So let's head back to the poem.

This time I tried [Dcode's Cipher Identifier](https://www.dcode.fr/cipher-identifier) to get idea on the type of cipher. After having looked up on Google and Dcode, it seemed like the cipher here is Acrostic Poem, but the automatic extracter of Dcode didn't give me a good result. Then I came across the [wiki page about Acrostic](https://en.wikipedia.org/wiki/Acrostic) and there it says we can extract letters from lines with a rule, like first letters of each lines for example.

I looked again at the poem and realised if we extract the n-th letter of n-th line of the first paragraph, I get a word in french. So that's the rule, and the hidden message is "Très Bien Joué", which means "Very Well Played".

So the flag is **`404CTF{TrèsBienJoué}`**

