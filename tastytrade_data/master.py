import asyncio
import subprocess
import os
from datetime import datetime


async def run_complete_analysis():
    print("🤖 MASTER TRADING ROBOT - BLACK-SCHOLES EDITION")
    print("=" * 80)
    print("🚀 Running complete Black-Scholes analysis in 5 steps...")
    print("⏰ This will take about 5-7 minutes total")
    print("🧮 Using sophisticated mathematical models for option pricing")
    print("=" * 80)

    steps = [
        ("stock_prices.py", "Getting current stock prices"),
        ("options_chains.py", "Finding options contracts"),
        ("risk_analysis.py", "Analyzing risk with Greeks"),
        ("market_prices.py", "Getting real-time market prices"),
        ("find_tendies.py", "Black-Scholes credit spread analysis")
    ]

    start_time = datetime.now()

    for i, (script, description) in enumerate(steps, 1):
        print(f"\n🎯 STEP {i}/5: {description}")
        print(f"🏃‍♂️ Running {script}...")

        try:
            # Run the script and wait for it to finish
            result = subprocess.run(['python3', script],
                                    capture_output=True,
                                    text=True,
                                    timeout=300)  # 5 minute timeout

            if result.returncode == 0:
                print(f"   ✅ Step {i} completed successfully!")
                # Print some of the output so we can see progress
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    # Show last few lines for progress indication
                    for line in lines[-4:]:  # Show last 4 lines
                        if line.strip():  # Only non-empty lines
                            print(f"      {line}")
            else:
                print(f"   ❌ Step {i} failed!")
                print(f"   Error: {result.stderr}")
                if result.stdout:
                    print(f"   Output: {result.stdout}")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Step {i} took too long (over 5 minutes)")
            return False
        except Exception as e:
            print(f"   ❌ Error running step {i}: {e}")
            return False

    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    print(f"\n🎉 ALL STEPS COMPLETED!")
    print("=" * 80)
    print(f"⏰ Total time: {total_time / 60:.1f} minutes")
    print(f"📁 Files created:")
    print(f"   📊 step1_stock_prices.json")
    print(f"   🎰 step2_options_contracts.json")
    print(f"   🧮 step3_risk_analysis.json")
    print(f"   💰 step4_market_prices.json")
    print(f"   🏆 step5_delta_analysis.json (Black-Scholes results)")

    # Show final summary from the Black-Scholes analysis
    try:
        import json
        with open('step5_delta_analysis.json', 'r') as f:
            final_data = json.load(f)

        print(f"\n🏆 BLACK-SCHOLES ANALYSIS RESULTS:")
        print(f"   🧮 Model used: Black-Scholes with real market data")
        print(f"   📊 Filters applied: ROI > 10%, Probability > 66%")
        print(f"   💡 Found {final_data['total_opportunities']} trading opportunities!")

        if final_data.get('best_deals') and len(final_data['best_deals']) > 0:
            best_deal = final_data['best_deals'][0]
            print(f"   🥇 BEST DEAL: {best_deal['company']} Bear Call Spread")
            print(f"      📈 Probability of Profit: {best_deal['probability_of_profit']:.1f}%")
            print(f"      💰 ROI: {best_deal['roi_percent']:.1f}%")
            print(f"      💵 Credit: ${best_deal['credit_collected']:.2f}")
            print(f"      🎯 Delta: {best_deal['spread_delta']:.3f} (Market Neutral)")
            print(f"      📝 {best_deal['explanation']}")

            # Show top 3 companies
            companies_shown = set()
            top_companies = []
            for deal in final_data['best_deals'][:10]:
                if deal['company'] not in companies_shown:
                    companies_shown.add(deal['company'])
                    top_companies.append(deal)
                if len(top_companies) >= 3:
                    break

            if len(top_companies) > 1:
                print(f"\n   🏢 TOP COMPANIES FOR CREDIT SPREADS:")
                for i, deal in enumerate(top_companies, 1):
                    print(
                        f"      {i}. {deal['company']}: {deal['probability_of_profit']:.1f}% PoP, {deal['roi_percent']:.1f}% ROI")

        # Show delta analysis summary
        if 'delta_analysis' in final_data:
            delta_info = final_data['delta_analysis']
            print(f"\n   📊 DELTA ANALYSIS:")
            print(f"      🎯 All {delta_info['no_delta_filter']} trades are market-neutral")
            print(f"      ✅ No delta filtering needed - spreads naturally neutral")

    except Exception as e:
        print(f"   ⚠️ Could not load final summary: {e}")
        print(f"   📄 Check step5_delta_analysis.json for detailed results")

    print(f"\n🎯 TRADING SYSTEM SUMMARY:")
    print(f"   🔬 Mathematical Model: Black-Scholes option pricing")
    print(f"   📊 Data Sources: Real-time tastytrade market data")
    print(f"   🎲 Strategy: Bear call credit spreads")
    print(f"   🛡️ Risk Management: Greeks analysis with delta neutrality")
    print(f"   💡 Probability Calculations: Log-normal distribution assumptions")

    return True


if __name__ == "__main__":
    # Run the complete Black-Scholes analysis system
    asyncio.run(run_complete_analysis())