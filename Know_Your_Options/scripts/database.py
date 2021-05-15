import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

class Stock:
    def __init__(self, ticker, start=None, end=None):

        self.ticker = ticker

        try:
            self._ticker = yf.Ticker(self.ticker)

            if not (start or end):
                self.df = self.df_ = self._ticker.history(period='max', auto_adjust=True)
                
            else:
                self.df = self.df_ = self._ticker.history(start=start, end=end, auto_adjust=True)

        except Exception as err:
            print(err)
    
    
def options_chain(symbol):
    import pandas as pd
    import numpy as np
    import yfinance as yf
    info = get_quote_table(symbol)
    current_price = info["Quote Price"]
    tk = yf.Ticker(symbol)
    exps = tk.options
    options = pd.DataFrame()
    for e in exps:
        opt = tk.option_chain(e)
        opt = pd.DataFrame().append(opt.calls).append(opt.puts)
        opt['expirationDate'] = e
        options = options.append(opt, ignore_index=True)
    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days = 1)
    options['yte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days
    
    # Boolean column if the option is a CALL
    options['CALL'] = options['contractSymbol'].str[4:].apply(
        lambda x: "C" in x)
    
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options['midpoint'] = (options['bid'] + options['ask']) / 2 # Calculate the midpoint of the bid-ask
    options['spread'] =  (options['ask'] - options['bid'])
    options['spread_pct'] = (options['ask'] - options['bid'])/options['ask'] 
    options['Underlying'] = current_price 
    # Drop unnecessary and meaningless columns
    options = options.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate'])

    return pd.DataFrame({
            "Underlying": current_price,
            "Ticker": symbol,
            "Expiry": options["expirationDate"],
            "YTE": options["yte"],
            "DTE": options["dte"],
            "Call": options["CALL"],
            "IV": options["impliedVolatility"],        
            "Strike": options["strike"],
            "Last": options["lastPrice"],
            "Bid": options["bid"],
            "Ask": options["ask"],
            "Midpoint": options['midpoint'],
            "Spread": options['spread'],
            "Spread_Pct": options['spread_pct'],
            "AKA": options["contractSymbol"]})    