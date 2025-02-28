# trytond
Trytond docker. 


configuracion del pg_hba.conf

``` bash
# local   all             all                                     peer
local   all             all                                     scram-sha-256
# IPv4 local connections:
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             172.28.0.2/32           scram-sha-256
host    all             all             0.0.0.0/0               scram-sha-256
```
