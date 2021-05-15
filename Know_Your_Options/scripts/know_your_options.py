import pandas as pd
pd.options.display.float_format = '{:,.6f}'.format
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
from pandas.tseries.offsets import BDay
end = pd.datetime.today().date()
start = end - 252 * BDay() * 1 # One year historical data
import yfinance as yf

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

def filter_by_moneyness(df, pct_cutoff=0.2):
    crit1 = (1-pct_cutoff)*df.Strike < df.Underlying
    crit2 = df.Underlying< (1+pct_cutoff)*df.Strike
    return (df.loc[crit1 & crit2].reset_index(drop=True)) 

def know_your_options(ticker, option="Call"):
    import datetime
    import re
    import utils 
    import QuantLib as ql 
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from yahoo_fin.stock_info import get_quote_table
    plt.style.use('dark_background')
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    info = get_quote_table(ticker)
    current_price = info["Quote Price"]
    yield_re = re.compile(r"\((?P<value>(\d+\.\d+))%\)")
    try:
        dividend_rate = float(yield_re.search(info["Forward Dividend & Yield"])["value"])
    except (KeyError, ValueError, TypeError):
        dividend_rate = 0.0      
        
    stk_sigma = np.std(np.log(Stock(ticker, start, end).df.Close.pct_change() + 1)) * 252 ** 0.5  

    def create_call(row):
        calculation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = calculation_date 
        risk_free_rate = 0.0001
        sigma = ql.SimpleQuote(stk_sigma)
        day_count = ql.Actual365Fixed()
        settlement = calculation_date
        calendar = ql.UnitedStates()
        exercise = ql.AmericanExercise(settlement, ql.Date(expiration.day, expiration.month, expiration.year))
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, row["strike"])
        american_option = ql.VanillaOption(payoff,exercise)
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(current_price))
        flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
        dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
        flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, ql.QuoteHandle(sigma), day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts) 
        american_option.setPricingEngine(ql.FdBlackScholesVanillaEngine(bsm_process, 1000, 1000))
        return {"Underlying": current_price,
                "Ticker": ticker,
                "Type": row["type"],
                "Expiration": row['expirationDate'],
                "YTE": row["yte"],
                "DTE": row["dte"],
                "Strike": row["strike"],
                "Last": row["lastPrice"],
                "Bid": row["bid"],
                "Ask": row["ask"],
                "Midpoint": (row['bid'] + row['ask']) / 2,
                "Spread": row['ask'] - row['bid'],
                "IV": row["impliedVolatility"],  
                "NPV": american_option.NPV(),
                "Delta": american_option.delta(),
                "Gamma": american_option.gamma(),
                "Theta": american_option.theta() / 365,
                "AKA": row["contractSymbol"]}        
        
    def create_put(row):
        calculation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = calculation_date
        risk_free_rate = 0.0001
        sigma = ql.SimpleQuote(stk_sigma)
        day_count = ql.Actual365Fixed()
        settlement = calculation_date
        calendar = ql.UnitedStates()
        exercise = ql.AmericanExercise(settlement, ql.Date(expiration.day, expiration.month, expiration.year))
        payoff = ql.PlainVanillaPayoff(ql.Option.Put, row["strike"])
        american_option = ql.VanillaOption(payoff,exercise)   
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(current_price))
        flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, risk_free_rate, day_count))
        dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(calculation_date, dividend_rate, day_count))
        flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(calculation_date, calendar, ql.QuoteHandle(sigma), day_count))
        bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)           
        american_option.setPricingEngine(ql.FdBlackScholesVanillaEngine(bsm_process, 1000, 1000))
        return {"Underlying": current_price,
                "Ticker": ticker,
                "Type": row["type"],
                "Expiration": row['expirationDate'],
                "YTE": row["yte"],
                "DTE": row["dte"],
                "Strike": row["strike"],
                "Last": row["lastPrice"],
                "Bid": row["bid"],
                "Ask": row["ask"],
                "Midpoint": (row['bid'] + row['ask']) / 2,
                "Spread": row['ask'] - row['bid'],
                "IV": row["impliedVolatility"],  
                "NPV": american_option.NPV(),
                "Delta": american_option.delta(),
                "Gamma": american_option.gamma(),
                "Theta": american_option.theta() / 365,
                "AKA": row["contractSymbol"]}                  
        
    options_= pd.DataFrame()       
    
    if option == "Call":
        
        tk = yf.Ticker(ticker)
        exps = tk.options
        
        for e in exps:
            opt = tk.option_chain(e)
            calls = pd.DataFrame().append(opt.calls)
            calls['expirationDate'] = e
            expiration =  pd.to_datetime(e) + datetime.timedelta(days = 1)
            calls['expirationDate'] = expiration
            calls['yte'] = (calls['expirationDate'] - datetime.datetime.today()).dt.days / 365
            calls['dte'] = (calls['expirationDate'] - datetime.datetime.today()).dt.days
            calls[['bid', 'ask', 'strike']] = calls[['bid', 'ask', 'strike']].apply(pd.to_numeric)
            calls['type'] = "Call"
            calls = calls.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate'])
            options = calls.apply(create_call, axis=1, result_type="expand")
            options_ = options_.append(options, ignore_index=True) 
    else:    
        
        tk = yf.Ticker(ticker)
        exps = tk.options
        
        for e in exps:
            opt = tk.option_chain(e)
            puts = pd.DataFrame().append(opt.puts)
            puts['expirationDate'] = e
            expiration =  pd.to_datetime(e) + datetime.timedelta(days = 1)
            puts['expirationDate'] = expiration
            puts['yte'] = (puts['expirationDate'] - datetime.datetime.today()).dt.days / 365
            puts['dte'] = (puts['expirationDate'] - datetime.datetime.today()).dt.days
            puts[['bid', 'ask', 'strike']] = puts[['bid', 'ask', 'strike']].apply(pd.to_numeric)
            puts['type'] = "Put"
            puts = puts.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate'])
            options = puts.apply(create_put, axis=1, result_type="expand")
            options_ = options_.append(options, ignore_index=True) 
    return  options_