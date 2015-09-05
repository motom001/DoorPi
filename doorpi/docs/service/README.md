
try first to run as application via `sudo doorpi_cli --trace` and see logoutput at screen

```
sudo cp doorpi /etc/init.d/doorpi
sudo update-rc.d doorpi defaults
sudo service doorpi start
```

see logfile @ /var/log/doorpi/*
