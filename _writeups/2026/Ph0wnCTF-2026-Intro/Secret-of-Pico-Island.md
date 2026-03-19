---
layout: writeup
category: Ph0wnCTF-2026-Intro
chall_description: 
points: 
solves: 
tags: Patching Reverse 
date: 2026-03-19
comments: false
---

## ## Challenge Description

A patched demo of "The secret of monkey island" with a description "You should play the demo".

[Challenge file](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\ph0wn-monkey1.zip)

##  ## Solution

After extracting the game we can take a look at the structure: 

* LFL files: this is the "room" files that contains scripts in the room, graphics and object etc
* DISK01LEC: the game resource container (Script, Strings...)
* dat: music.dat and sample.dat seems like resources file to me

As the challenge suggest, I spend some time running around in the game. This is a really old and classic game, and to run this we need `scummvm` to load the game.

The demo was patched with Picolecroco as Pirate and all the conversations was about Ph0wnctf, kinda cool to me. 

During the playthrough, we can activate the DEBUG mode of scummvm and use it as cheat mode to move around to the room like 901 902 904 and 000. 



Ok enough playing let's get to work. I decide to use [ScummEX](https://downloads.scummvm.org/frs/extras/ScummEx/scummex-win32.exe) to view the DISK01LEC file. I extracted some SC (script) file easily but they seem so numerous so we need a better approach.

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\island1.png)



After reading about SCUMM at this [article](https://tonick.net/p/2021/03/a-deep-dive-into-the-scumm-bytecode/) I find something interesting:

> *Monkey Island* (and SCUMM games in general) are structured in one index file (like `monkey.000`) and 1..n data files (like `monkey.001`). First of all these files are [XORed](https://en.wikipedia.org/wiki/Exclusive_or) with a specific value - for whatever reason. For *The Secret of Monkey Island* this value is `0x69`. If you want to make sense of them in a hex-editor you will first have to XOR them with this value.

So let's write a short python that XOR 0x69 with DISK01.LEC:

```python
input_file = "DISK01.LEC"
output_file = "xored69.out"

with open(input_file, "rb") as f:
    data = f.read()

xored = bytes([b ^ 0x69 for b in data])

with open(output_file, "wb") as f:
    f.write(xored)
```

And we found something: a hint for Flag is in script #98 room 58, disk 01 and a false flag Ph0wn(LuredUlittleScumm). Of course this flag didn't work but we found a hint.

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\island2.png)

Now let's check SC98 out: to extract I use a tool called [scummtr](https://github.com/dwatteau/scummtr) used as fan translation tools for SCUMM games. It helps dumping all the script in a SCUMM structure. (You can extract with Scummex too but it gonna be hardwork)

If you play the demo and use DEBUG mode room 58 command, it will teleport you to the room 58, which is the intro of the demo. So the flag is hidden here.

After dumping we have a directory, we can find the SC98 at [/DISK_0001/LF_0058/SC_0098](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\SC_0098)

To decompile this I use [descumm](https://manpages.debian.org/testing/scummvm-tools/descumm.6.en.html) and get result](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\SC098.txt).

```bash
descumm ./SC_0098 -o -0 > SC098.txt
```

At the OFFSET `[0459]` we have this:

```
[0420] (80) breakHere();
[0421] (18) /* goto 0424; */
[0424] (18) goto 047A;
[0427] (27) SetStringChar(22,14,118);
[042C] (27) SetStringChar(22,16,79);
[0431] (27) SetStringChar(22,7,108);
[0436] (27) SetStringChar(22,10,121);
[043B] (27) SetStringChar(22,6,83);
[0440] (27) SetStringChar(22,15,114);
[0445] (27) SetStringChar(22,8,105);
[044A] (27) SetStringChar(22,17,39);
[044F] (27) SetStringChar(22,11,83);
[0454] (27) SetStringChar(22,9,109);
[0459] (14) print(255,[Pos(72,32),Clipped(320),Text("The flag is " + getString(VAR_ROOM_RESOURCE))]);
[0459] (14) print(255,[Pos(72,32),Clipped(320),Text("The flag is " + getString(VAR_ROOM_RESOURCE))]);
...
[047A] (62) stopScript(99);
```

So to get the flag we just need to read VAR_ROOM_RESOURCE (vOlySri'Sm) and  combine with the OPCODE 27 to get the flag.



Or if you have time and like poking around, we can try another way to trigger the 0459 by patching the demo ourselves to jump to this OFFSET using the offset 0424 with OPCODE 18 goto.



In the doc of scumm:

> ## jumpRelative ($18)
>
> jumps
>
> ### Encoding
>
> ```
> opcode target[16]
> ```
>
> ### Operation
>
> ```
> PC := PC + target
> ```
>
> The inline constant target is read as a signed word and added to the program counter after the instruction has been read. Therefore, if target is zero, the instruction will do nothing; if target is -3, an infinite loop will result.



Let's try with hexeditor, find the offset 0x0424 we will see a value 18 7A 04, we can simply change to 18 00 00 so it will jump to the next 0x0427 instead of 047A and eventually  0459 will be executed, which shows us the flag.

![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\island3.png)

Now we can recompile using another tool in scummtr: scummrp to reompile into 1 DISK01.LEC and run the scummvm:
![](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\islandflag.png)

Now not only we get the flag but we did get it shown in the demo.

[Here](../../../\assets\CTFs\Ph0wnCTF-2026-Intro\secret-of-pico-island.tar.gz) is the repatched version of the demo. 

That's the last challenge at the intro. See you soon! 
