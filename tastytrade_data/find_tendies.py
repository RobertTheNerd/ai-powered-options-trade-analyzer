import json
import pandas as pd
import numpy as np
from datetime import datetime
import math
from scipy.stats import norm


class BlackScholesCalculator:
    """Black-Scholes option pricing and probability calculations"""

    def __init__(self, risk_free_rate=0.05):
        self.risk_free_rate = risk_free_rate

    def black_scholes_call(self, S, K, T, r, sigma):
        """Calculate Black-Scholes call option price"""
        if T <= 0:
            return max(S - K, 0)

        if sigma <= 0:
            return max(S - K, 0)

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return max(call_price, 0)

    def probability_otm(self, S, K, T, sigma, option_type='call'):
        """Calculate probability that option expires out-of-the-money"""
        if T <= 0:
            return 1.0 if (option_type == 'call' and S < K) or (option_type == 'put' and S > K) else 0.0

        if sigma <= 0:
            return 1.0 if (option_type == 'call' and S < K) or (option_type == 'put' and S > K) else 0.0

        d2 = (np.log(S / K) + (self.risk_free_rate - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

        if option_type == 'call':
            prob_otm = norm.cdf(-d2)
        else:
            prob_otm = norm.cdf(d2)

        return prob_otm

    def calculate_greeks(self, S, K, T, r, sigma, option_type='call'):
        """Calculate option Greeks"""
        if T <= 0:
            return {'delta': 0, 'theta': 0, 'gamma': 0, 'vega': 0}

        if sigma <= 0:
            return {'delta': 0, 'theta': 0, 'gamma': 0, 'vega': 0}

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            delta = norm.cdf(d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        else:
            delta = -norm.cdf(-d1)
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100

        return {
            'delta': delta,
            'theta': theta,
            'gamma': gamma,
            'vega': vega
        }


def find_deals_with_delta_analysis():
    print("🔍 BLACK-SCHOLES WITH DELTA ANALYSIS")
    print("=" * 70)
    print("🎯 ROI > 10%, PoP > 66%, Delta Analysis...")

    # Load all data
    with open('step1_stock_prices.json', 'r') as f:
        stock_data = json.load(f)

    with open('step2_options_contracts.json', 'r') as f:
        options_data = json.load(f)

    with open('step3_risk_analysis.json', 'r') as f:
        risk_data = json.load(f)

    with open('step4_market_prices.json', 'r') as f:
        price_data = json.load(f)

    print("✅ Loaded all data!")

    bs_calc = BlackScholesCalculator()

    # Create lookups
    greek_lookup = {}
    for company, greeks_list in risk_data['risk_by_company'].items():
        for greek in greeks_list:
            greek_lookup[greek['contract_name']] = greek

    price_lookup = {}
    for company, prices_list in price_data['prices_by_company'].items():
        for price in prices_list:
            price_lookup[price['contract_name']] = price

    all_spreads_no_delta = []  # No delta filter
    all_spreads_loose_delta = []  # Loose delta filter
    all_spreads_strict_delta = []  # Strict delta filter

    delta_stats = {
        'deltas_seen': [],
        'negative_deltas': 0,
        'neutral_deltas': 0,  # -0.2 to +0.2
        'positive_deltas': 0
    }

    for company, company_options in options_data['options_by_company'].items():
        current_stock_price = company_options['current_stock_price']

        print(f"\n🏢 {company} (${current_stock_price:.2f})...")

        for exp_date, exp_data in company_options['expiration_dates'].items():
            contracts = exp_data['contracts']
            calls = [c for c in contracts if c['contract_type'] == 'CALL']
            calls_above_price = [c for c in calls if c['strike_price'] > current_stock_price]
            calls_above_price.sort(key=lambda x: x['strike_price'])

            for i in range(len(calls_above_price) - 1):
                short_call = calls_above_price[i]
                long_call = calls_above_price[i + 1]

                if long_call['strike_price'] - short_call['strike_price'] > 5:
                    continue

                short_symbol = short_call['streamer_symbol']
                long_symbol = long_call['streamer_symbol']

                if (short_symbol not in price_lookup or long_symbol not in price_lookup or
                        short_symbol not in greek_lookup or long_symbol not in greek_lookup):
                    continue

                short_price_data = price_lookup[short_symbol]
                long_price_data = price_lookup[long_symbol]
                short_greek_data = greek_lookup[short_symbol]
                long_greek_data = greek_lookup[long_symbol]

                # Get data
                short_iv = short_greek_data['implied_volatility']
                long_iv = long_greek_data['implied_volatility']
                avg_iv = (short_iv + long_iv) / 2

                days_to_exp = short_call['days_until_expires']
                time_to_exp = days_to_exp / 365.0

                if time_to_exp <= 0:
                    continue

                # Calculate market credit
                short_bid = short_price_data['what_buyers_pay']
                long_ask = long_price_data['what_sellers_want']

                if short_bid <= 0 or long_ask <= 0:
                    continue

                market_credit = short_bid - long_ask

                if market_credit <= 0:
                    continue

                # Black-Scholes probability
                prob_profit_bs = bs_calc.probability_otm(
                    current_stock_price, short_call['strike_price'],
                    time_to_exp, avg_iv, 'call'
                ) * 100

                # Calculate metrics
                strike_width = long_call['strike_price'] - short_call['strike_price']
                max_risk = strike_width - market_credit
                roi_percent = (market_credit / max_risk) * 100 if max_risk > 0 else 0

                # Calculate Greeks
                short_greeks = bs_calc.calculate_greeks(
                    current_stock_price, short_call['strike_price'],
                    time_to_exp, bs_calc.risk_free_rate, short_iv, 'call'
                )
                long_greeks = bs_calc.calculate_greeks(
                    current_stock_price, long_call['strike_price'],
                    time_to_exp, bs_calc.risk_free_rate, long_iv, 'call'
                )

                spread_delta = short_greeks['delta'] - long_greeks['delta']
                spread_theta = short_greeks['theta'] - long_greeks['theta']

                # Track delta statistics
                delta_stats['deltas_seen'].append(spread_delta)
                if spread_delta < -0.1:
                    delta_stats['negative_deltas'] += 1
                elif -0.2 <= spread_delta <= 0.2:
                    delta_stats['neutral_deltas'] += 1
                else:
                    delta_stats['positive_deltas'] += 1

                # Basic filters first
                if roi_percent <= 10 or prob_profit_bs <= 66:
                    continue

                spread = {
                    'company': company,
                    'short_strike': short_call['strike_price'],
                    'long_strike': long_call['strike_price'],
                    'days_to_expiration': days_to_exp,
                    'credit_collected': market_credit,
                    'max_risk': max_risk,
                    'roi_percent': roi_percent,
                    'probability_of_profit': prob_profit_bs,
                    'current_stock_price': current_stock_price,
                    'avg_implied_volatility': avg_iv,
                    'spread_delta': spread_delta,
                    'spread_theta': spread_theta,
                    'explanation': f"Collect ${market_credit:.2f}, {prob_profit_bs:.1f}% PoP if {company} stays below ${short_call['strike_price']:.0f}",
                    'delta_interpretation': 'Neutral' if abs(spread_delta) <= 0.2 else (
                        'Bullish' if spread_delta > 0.2 else 'Bearish')
                }

                # Add to no-delta list (already passed ROI/PoP filters)
                all_spreads_no_delta.append(spread)

                # Add to loose delta list (delta between -0.5 and +0.5)
                if -0.5 <= spread_delta <= 0.5:
                    all_spreads_loose_delta.append(spread)

                # Add to strict delta list (delta between -0.2 and +0.2)
                if -0.2 <= spread_delta <= 0.2:
                    all_spreads_strict_delta.append(spread)

    # Sort all lists by probability
    all_spreads_no_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)
    all_spreads_loose_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)
    all_spreads_strict_delta.sort(key=lambda x: x['probability_of_profit'], reverse=True)

    print(f"\n📊 DELTA ANALYSIS RESULTS:")
    print(f"   Deltas seen: min={min(delta_stats['deltas_seen']):.3f}, max={max(delta_stats['deltas_seen']):.3f}")
    print(f"   Negative deltas (<-0.1): {delta_stats['negative_deltas']}")
    print(f"   Neutral deltas (-0.2 to +0.2): {delta_stats['neutral_deltas']}")
    print(f"   Positive deltas (>+0.2): {delta_stats['positive_deltas']}")

    print(f"\n🎯 FILTER COMPARISON (ROI>10%, PoP>66%):")
    print(f"   ✅ NO Delta Filter: {len(all_spreads_no_delta)} opportunities")
    print(f"   📊 LOOSE Delta Filter (±0.5): {len(all_spreads_loose_delta)} opportunities")
    print(f"   🎯 STRICT Delta Filter (±0.2): {len(all_spreads_strict_delta)} opportunities")

    # Show top 10 from each category
    print(f"\n🏆 TOP 10 - NO DELTA FILTER:")
    print("-" * 140)
    for i, spread in enumerate(all_spreads_no_delta[:10]):
        delta_color = "🟢" if abs(spread['spread_delta']) <= 0.2 else (
            "🟡" if abs(spread['spread_delta']) <= 0.5 else "🔴")
        print(f"{i + 1:2}. {spread['company']:4} | "
              f"SELL ${spread['short_strike']:3.0f}C / BUY ${spread['long_strike']:3.0f}C | "
              f"PoP: {spread['probability_of_profit']:5.1f}% | "
              f"ROI: {spread['roi_percent']:5.1f}% | "
              f"DTE: {spread['days_to_expiration']:2d} | "
              f"Δ: {spread['spread_delta']:6.3f} {delta_color} | "
              f"Credit: ${spread['credit_collected']:.2f}")

    print(f"\n🎯 TOP 10 - WITH LOOSE DELTA FILTER (±0.5):")
    print("-" * 140)
    for i, spread in enumerate(all_spreads_loose_delta[:10]):
        print(f"{i + 1:2}. {spread['company']:4} | "
              f"SELL ${spread['short_strike']:3.0f}C / BUY ${spread['long_strike']:3.0f}C | "
              f"PoP: {spread['probability_of_profit']:5.1f}% | "
              f"ROI: {spread['roi_percent']:5.1f}% | "
              f"DTE: {spread['days_to_expiration']:2d} | "
              f"Δ: {spread['spread_delta']:6.3f} | "
              f"Credit: ${spread['credit_collected']:.2f}")

    if all_spreads_strict_delta:
        print(f"\n🎯 TOP 10 - WITH STRICT DELTA FILTER (±0.2):")
        print("-" * 140)
        for i, spread in enumerate(all_spreads_strict_delta[:10]):
            print(f"{i + 1:2}. {spread['company']:4} | "
                  f"SELL ${spread['short_strike']:3.0f}C / BUY ${spread['long_strike']:3.0f}C | "
                  f"PoP: {spread['probability_of_profit']:5.1f}% | "
                  f"ROI: {spread['roi_percent']:5.1f}% | "
                  f"DTE: {spread['days_to_expiration']:2d} | "
                  f"Δ: {spread['spread_delta']:6.3f} | "
                  f"Credit: ${spread['credit_collected']:.2f}")
    else:
        print(f"\n❌ NO TRADES passed strict delta filter (±0.2)")

    # Save the no-delta version as the main result
    result = {
        'step': 5,
        'filters_used': 'ROI > 10%, PoP > 66%, NO delta filter',
        'total_opportunities': len(all_spreads_no_delta),
        'delta_analysis': {
            'no_delta_filter': len(all_spreads_no_delta),
            'loose_delta_filter': len(all_spreads_loose_delta),
            'strict_delta_filter': len(all_spreads_strict_delta)
        },
        'best_deals': all_spreads_no_delta[:25],
        'timestamp': datetime.now().isoformat()
    }

    filename = 'step5_delta_analysis.json'
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Saved analysis to: {filename}")

    return result


if __name__ == "__main__":
    find_deals_with_delta_analysis()