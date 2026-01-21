def zVolume(df, lookback=20):
    """computes zVolume (z-score of volume) for all rows"""
    vol = df["volume"].astype(float)
    rolling_mean = vol.rolling(lookback).mean()
    rolling_std = vol.rolling(lookback).std()

    # compute z-score, avoid division by zero
    df["zVolume"] = ((vol - rolling_mean) / (rolling_std + 1e-8)).fillna(0)
    return df
