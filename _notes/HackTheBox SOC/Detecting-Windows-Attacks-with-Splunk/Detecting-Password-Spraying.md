---
layout: note_post
category: HackTheBox SOC
module: Detecting Windows Attacks with Splunk
title: Detecting Password Spraying
date: 2025-09-03
tags: windows splunk soc

---

### Detecting Password Spraying

Password Spraying is an attack where the attacker use a small common set of passwords for multiple accounts. It's like multiple accounts - 1 password compared to bruteforce attack (1 account - multiple passwords).

The pattern of this type of attack is <span style="color:green">Event ID 4625 - Failed Logon </span>. There are also other event log that can help:

* 4768 and ErrorCode 0x6 - Kerberos Invalid Users
* 4768 and ErrorCode 0x12 - Kerberos Disabled Users
* 4776 and ErrorCode 0xC000006A - NTLM Invalid Users
* 4776 and ErrorCode 0xC0000064 - NTLM Wrong Password
* 4648 - Authenticate Using Explicit Credentials
* 4771 - Kerberos Pre-Authentication Failed



**Question:**

![Question](../../../\assets\Notes\SOC\q1s2.png)

Here is the given Splunk search:

```
index=main earliest=1690280680 latest=1690289489 source="WinEventLog:Security" EventCode=4625
| bin span=15m _time
| stats values(user) as Users, dc(user) as dc_user by src, Source_Network_Address, dest, EventCode, Failure_Reason
```

This search is looking for Event ID **4625** (Failed Logon), within a timeframe, with a **timebucket of 15 minutes** and then aggregate the results by 5 factors above.

<span style="color:green">bin span=15m _time</span> will floor the event's `_time` to interval of 15 minutes (ex: 09:07 -> 09:00, 09:25 -> 09:15)


To solve this, simply change the search to **All time**, and add filter for the targeted machine.

![Question](E:\thng01.github.io\assets\Notes\SOC\a1s2.png)

