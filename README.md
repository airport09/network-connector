# network-connector
Wi-Fi Network Connector with Netsh Commands

### Usage
Checks for internet connection, if not found tries to connect to one of the available networks in the following priority order:

~~~
-----preferred by user network
---known network
--open network
-password protected network
~~~

### Run 

~~~
python run.py
~~~