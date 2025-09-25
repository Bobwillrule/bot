def RSI(df, period=14):
    """Calculate RSI with Wilder's Smoothing/exponential moving average"""
    delta = df['close'].diff()
    gain = delta.clip(lower=0) # pos values
    loss = -delta.clip(upper=0)
    period = 14 # Change this to change RSI length
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean() #ewm for exp moving average
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss # RSI calculation
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def StochRSI(df, period=14):
    """ REQUIRES: df with RSI (RSI function call first), non-zero period
    EFFECTS: Calculates the stochastic RSI based on RSI"""
    rsi = df['RSI']
    min_rsi = rsi.rolling(window=period).min()
    max_rsi = rsi.rolling(window=period).max()
    df['stochRSI'] = ((rsi - min_rsi) / (max_rsi - min_rsi))*100
    return df