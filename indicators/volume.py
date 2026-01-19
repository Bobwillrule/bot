def volume(df, lookback=20):
    """returns a score based on volume and adds zVolume to df""" 
    if len(df) < lookback:
        df.loc[df.index[-1], "zVolume"] = 0
        return df
    
    vol = df["volume"].astype(float)
    mu = vol.iloc[-lookback:].mean()
    sigma = vol.iloc[-lookback:].std()

    if sigma == 0:
        zVolume = 0
    else:
        zVolume = (vol.iloc[-1] - mu) / sigma

    df.loc[df.index[-1], "zVolume"] = zVolume
    return df