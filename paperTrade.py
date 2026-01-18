def PaperTrade(df, buy, lotSize):
    """Practice trading updating only the last row (no history added)"""

    if buy:
        # Calculate cost of purchase
        price = lotSize * df["close"].iloc[-1]

        # Check that we have enough money to buy
        if price <= df["Balance"].iloc[-1]:
            # Deduct cost from balance
            df.loc[df.index[-1], "Balance"] -= price
            # Add coins to our holdings
            df.loc[df.index[-1], "Amount"]  += lotSize

    else:
        # Check that we have enough coins to sell
        if df["Amount"].iloc[-1] >= lotSize:
            # Calculate proceeds of sale
            price = lotSize * df["close"].iloc[-1]
            # Add money to balance
            df.loc[df.index[-1], "Balance"] += price
            # Subtract coins from holdings
            df.loc[df.index[-1], "Amount"]  -= lotSize
    return df