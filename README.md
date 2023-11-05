# network-connector
Wi-Fi Network Connector based on [netsh](https://learn.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-contexts) commands

### USE-CASE
Checks for internet connection, if not found tries to connect to one of the available networks in the following priority order:

~~~
⟶ PREFERRED # by user
⟶ KNOWN
⟶ OPEN
⟶ PASSWORD PROTECTED
~~~

### USAGE

~~~
python run.py
~~~