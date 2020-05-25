class Message:
    BAD_CMD = 'Unknown command'
    INP_CUR = 'Enter currency'
    INP_DUR = 'Enter duration in seconds'
    INP_VAL = 'Enter border rate'
    HELP = """The bot helps you to monitor currency rates.

**Get rates:**
```
/rates
     Enter duration in seconds
5
...Five seconds later...
     EUR 78.15  USD 71.73
```

**Stop loss**
```
/stop_loss
    Enter currency
USD
    Enter border rate
71.5
...Some time later...
    EUR 78.02  USD 71.42
```
"""
