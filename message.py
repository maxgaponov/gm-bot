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

    @staticmethod
    def get_rate_message(rates):
        message = '  '.join(['{} {:.2f}'.format(name, rate) for (name, rate) in rates.items()])
        return message


    @staticmethod
    def get_stop_loss_message(rates, cur):
        message = 'Stop loss {} {:.2f}'.format(cur, rates[cur])
        return message


    @staticmethod
    def get_take_profit_message(rates, cur):
        message = 'Take profit {} {:.2f}'.format(cur, rates[cur])
        return message
