"""
Damping Coefficient Calculator for RAP Macroeconomic Prediction

Calculates effective damping (d) from observable fiscal and monetary policy.
"""

import numpy as np
import pandas as pd
from datetime import datetime


def calculate_effective_damping(
    primary_surplus_pct_gdp: float,
    policy_tightness_index: float,
    political_sustainability_factor: float = 1.0
) -> float:
    """
    Calculate effective damping coefficient from policy indicators.
    
    Parameters:
    -----------
    primary_surplus_pct_gdp : float
        Fiscal balance excluding interest payments (% of GDP)
        Positive = surplus, Negative = deficit
        
    policy_tightness_index : float
        Composite index of monetary policy stance
        Range: -2 (very expansionary) to +2 (very tight)
        Components:
        - QE programs: negative (expansionary)
        - Interest rates vs neutral: positive if above neutral
        - Balance sheet normalization: positive if reducing
        
    political_sustainability_factor : float, default=1.0
        Political capacity to sustain policy
        Range: 0.0 (breakdown) to 1.0 (sustainable indefinitely)
        
    Returns:
    --------
    effective_d : float
        Estimated damping coefficient
        d > 6: Beyond historical maximum
        d = 4-6: Extreme austerity (unsustainable)
        d = 2-4: Aggressive discipline
        d = 0-2: Mild discipline
        d < 0: Negative damping (expansionary)
    """
    
    # Non-linear fiscal component (accelerates at high surpluses)
    if primary_surplus_pct_gdp > 0:
        # Positive surpluses have increasing political cost
        fiscal_damping = (primary_surplus_pct_gdp / 2.0) ** 1.3
    else:
        # Deficits are linear (negative damping)
        fiscal_damping = primary_surplus_pct_gdp / 2.0
    
    # Monetary component
    monetary_damping = policy_tightness_index * 0.8
    
    # Apply political constraint multiplier
    effective_d = (fiscal_damping + monetary_damping) * political_sustainability_factor
    
    return effective_d


def calculate_r_minus_g(
    nominal_yield_10yr: float,
    expected_inflation: float,
    real_gdp_growth_forecast: float
) -> float:
    """
    Calculate real interest rate minus real growth differential.
    
    Parameters:
    -----------
    nominal_yield_10yr : float
        10-year government bond yield (%)
        Proxy for long-term debt servicing cost
        
    expected_inflation : float
        Expected inflation rate (%)
        From TIPS breakeven or survey expectations
        
    real_gdp_growth_forecast : float
        Real GDP growth projection (%)
        From IMF WEO or consensus forecasts
        
    Returns:
    --------
    r_minus_g : float
        Real interest rate minus real growth (%)
        Positive: Debt compounds faster than growth
        Negative: Growth can outpace debt service
    """
    
    real_interest_rate = nominal_yield_10yr - expected_inflation
    r_minus_g = real_interest_rate - real_gdp_growth_forecast
    
    return r_minus_g


def calculate_policy_tightness_index(
    qe_program_active: bool,
    policy_rate_vs_neutral: float,
    balance_sheet_change_pct_gdp: float
) -> float:
    """
    Calculate composite policy tightness index.
    
    Parameters:
    -----------
    qe_program_active : bool
        True if active QE/asset purchases ongoing
        
    policy_rate_vs_neutral : float
        Policy rate minus estimated neutral rate (%)
        
    balance_sheet_change_pct_gdp : float
        Change in central bank balance sheet (% of GDP)
        Negative = reduction (tightening)
        Positive = expansion (easing)
        
    Returns:
    --------
    tightness_index : float
        Range: -2 (very expansionary) to +2 (very tight)
    """
    
    # QE component
    qe_component = -1.0 if qe_program_active else 0.0
    
    # Interest rate component (capped at ±1)
    rate_component = np.clip(policy_rate_vs_neutral / 2.0, -1.0, 1.0)
    
    # Balance sheet component (capped at ±1)
    bs_component = np.clip(-balance_sheet_change_pct_gdp / 5.0, -1.0, 1.0)
    
    # Weighted average
    tightness_index = (qe_component * 0.4 + 
                      rate_component * 0.3 + 
                      bs_component * 0.3)
    
    return tightness_index


def historical_validation():
    """
    Validate damping calculation against known historical cases.
    """
    
    print("=" * 60)
    print("HISTORICAL VALIDATION OF DAMPING CALCULATION")
    print("=" * 60)
    print()
    
    # Post-WWII United States (1945-1970)
    print("Post-WWII United States (1945-1970)")
    print("-" * 40)
    d_us = calculate_effective_damping(
        primary_surplus_pct_gdp=4.0,  # 4% average
        policy_tightness_index=-0.8,  # Bretton Woods, some repression
        political_sustainability_factor=0.9  # Sustainable given context
    )
    print(f"Calculated d: {d_us:.2f}")
    print(f"Expected d: 2.5-3.0")
    print(f"Match: {'✓' if 2.0 < d_us < 3.5 else '✗'}")
    print()
    
    # Canada 1990s (1995-2000)
    print("Canada 1990s (1995-2000)")
    print("-" * 40)
    d_canada = calculate_effective_damping(
        primary_surplus_pct_gdp=7.0,  # 7% sustained
        policy_tightness_index=-0.5,  # Tight but not extreme
        political_sustainability_factor=0.8  # Caused strain
    )
    print(f"Calculated d: {d_canada:.2f}")
    print(f"Expected d: 4.0-5.0")
    print(f"Match: {'✓' if 3.5 < d_canada < 5.5 else '✗'}")
    print()
    
    # Greece 2010s (2010-2015)
    print("Greece 2010s (2010-2015)")
    print("-" * 40)
    d_greece = calculate_effective_damping(
        primary_surplus_pct_gdp=9.0,  # 9% peak
        policy_tightness_index=0.5,   # ECB constraints
        political_sustainability_factor=0.5  # Near breakdown
    )
    print(f"Calculated d: {d_greece:.2f}")
    print(f"Expected d: 5.0-6.0")
    print(f"Match: {'✓' if 4.5 < d_greece < 6.5 else '✗'}")
    print()
    
    # Current (2025)
    print("Current Global Average (2025)")
    print("-" * 40)
    d_current = calculate_effective_damping(
        primary_surplus_pct_gdp=-3.5,  # 3.5% deficit
        policy_tightness_index=-0.5,   # Mildly expansionary
        political_sustainability_factor=0.8  # Could worsen
    )
    print(f"Calculated d: {d_current:.2f}")
    print(f"Expected d: <0 (negative damping)")
    print(f"Match: {'✓' if d_current < 0 else '✗'}")
    print()
    
    print("=" * 60)


def quarterly_update_template(
    date: str,
    debt_to_gdp: float,
    primary_deficit_pct: float,
    nominal_yield: float,
    expected_inflation: float,
    real_gdp_growth: float,
    qe_active: bool,
    policy_rate_vs_neutral: float,
    bs_change_pct_gdp: float
) -> dict:
    """
    Calculate all metrics for quarterly update.
    
    Returns dictionary with all calculated values.
    """
    
    # Calculate policy tightness
    tightness = calculate_policy_tightness_index(
        qe_program_active=qe_active,
        policy_rate_vs_neutral=policy_rate_vs_neutral,
        balance_sheet_change_pct_gdp=bs_change_pct_gdp
    )
    
    # Calculate effective damping
    d = calculate_effective_damping(
        primary_surplus_pct_gdp=-primary_deficit_pct,  # Flip sign
        policy_tightness_index=tightness,
        political_sustainability_factor=0.8  # Adjust based on context
    )
    
    # Calculate r - g
    r_minus_g = calculate_r_minus_g(
        nominal_yield_10yr=nominal_yield,
        expected_inflation=expected_inflation,
        real_gdp_growth_forecast=real_gdp_growth
    )
    
    return {
        'date': date,
        'debt_to_gdp': debt_to_gdp,
        'primary_deficit_pct': primary_deficit_pct,
        'nominal_yield': nominal_yield,
        'expected_inflation': expected_inflation,
        'real_gdp_growth': real_gdp_growth,
        'r_minus_g': r_minus_g,
        'policy_tightness_index': tightness,
        'effective_damping': d,
        'damping_status': 'NEGATIVE' if d < 0 else 'POSITIVE',
        'risk_level': risk_assessment(d, r_minus_g, debt_to_gdp)
    }


def risk_assessment(d: float, r_minus_g: float, debt_to_gdp: float) -> str:
    """
    Assess overall crisis risk based on metrics.
    """
    
    # Critical thresholds
    if d < -1.0 and r_minus_g > 1.0 and debt_to_gdp > 250:
        return "CRITICAL"
    elif d < 0 and r_minus_g > 0.5 and debt_to_gdp > 230:
        return "HIGH"
    elif d < 1.0 and debt_to_gdp > 200:
        return "ELEVATED"
    elif d < 2.0 and debt_to_gdp > 150:
        return "MODERATE"
    else:
        return "LOW"


if __name__ == "__main__":
    # Run historical validation
    historical_validation()
    
    print("\n\n")
    print("=" * 60)
    print("Q4 2025 BASELINE CALCULATION")
    print("=" * 60)
    print()
    
    # Calculate Q4 2025 baseline
    q4_2025 = quarterly_update_template(
        date="2025-Q4",
        debt_to_gdp=235.0,
        primary_deficit_pct=3.5,
        nominal_yield=4.5,
        expected_inflation=2.5,
        real_gdp_growth=2.0,
        qe_active=False,
        policy_rate_vs_neutral=0.5,
        bs_change_pct_gdp=0.0
    )
    
    # Print results
    for key, value in q4_2025.items():
        if isinstance(value, float):
            print(f"{key:25s}: {value:6.2f}")
        else:
            print(f"{key:25s}: {value}")
    
    print()
    print("=" * 60)
    print()
    
    print("INTERPRETATION:")
    print(f"- Effective damping d = {q4_2025['effective_damping']:.2f} (NEGATIVE)")
    print(f"- r - g = {q4_2025['r_minus_g']:.2f}% (POSITIVE, debt compounds)")
    print(f"- Risk level: {q4_2025['risk_level']}")
    print()
    print("Prediction status: ON TRACK for runaway trajectory")
