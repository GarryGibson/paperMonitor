# paperMonitor

This small Python script reads data from a combined temperature and humidity sensor, and displays them along with the current time on an ePaper (think Kindle) screen.

It also uploads the readings to MariaDB database running on a NAS.

You'll need a config file like this, called *config.json*

```
{
    "DEFAULT":{
        "DBCONNECTION":{
            "HOST":"127.0.0.1",
            "PORT":3306,
            "DATABASE":"humidtemp",
            "USER":"user",
            "PASSWORD":"password"
        }
    }
}
```

