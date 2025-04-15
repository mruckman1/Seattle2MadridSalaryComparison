import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Global Compensation Converter",
    page_icon="💰",
    layout="wide"
)

def format_currency(amount, currency):
    """Format a number as currency with appropriate symbol"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f}"

def calculate_conversion(
    source_locale,
    base_salary,
    bonus,
    rsus,
    us_tax_rate=0.30,
    spain_tax_rate=0.24,
    exchange_rate=1.09,
    col_factor=0.60
):
    """
    Unified function to calculate compensation conversion between Seattle and Madrid
    
    Args:
        source_locale: "Seattle" or "Madrid"
        base_salary: Base salary in source currency
        bonus: Bonus in source currency
        rsus: RSUs in source currency
        us_tax_rate: Effective tax rate in Seattle (default 30%)
        spain_tax_rate: Effective tax rate in Madrid under Beckham's law (default 24%)
        exchange_rate: Exchange rate (1 EUR = x USD, default 1.09)
        col_factor: Cost-of-living factor (Madrid is x% of Seattle, default 60%)
    
    Returns:
        Dictionary with conversion results
    """
    # Determine which conversion to use based on source locale
    if source_locale == "Seattle":
        # Seattle to Madrid conversion
        source_currency = "USD"
        target_currency = "EUR"
        source_tax_rate = us_tax_rate
        target_tax_rate = spain_tax_rate
        
        # 1. Calculate source net income from base+bonus
        source_net = (base_salary + bonus) * (1 - source_tax_rate)
        
        # 2. Convert to target currency
        target_net_before_col = source_net / exchange_rate
        
        # 3. Adjust for cost-of-living
        target_net = target_net_before_col * col_factor
        
        # 4. Compute the gross base+bonus required in target locale
        target_gross = target_net / (1 - target_tax_rate)
        
        # 5. Convert RSUs to target currency
        target_rsus = rsus / exchange_rate

        # 6. Calculate monthly values and net after-tax amounts
        target_base_ratio = base_salary / (base_salary + bonus) if (base_salary + bonus) > 0 else 0
        target_bonus_ratio = bonus / (base_salary + bonus) if (base_salary + bonus) > 0 else 0
        
        # Distribute the target gross proportionally between base and bonus
        target_base = target_gross * target_base_ratio
        target_bonus = target_gross * target_bonus_ratio
        
    else:  # Madrid to Seattle
        # Madrid to Seattle conversion
        source_currency = "EUR"
        target_currency = "USD"
        source_tax_rate = spain_tax_rate
        target_tax_rate = us_tax_rate
        
        # 1. Calculate source net income from base+bonus
        source_net = (base_salary + bonus) * (1 - source_tax_rate)
        
        # 2. Convert to target currency
        target_net_before_col = source_net * exchange_rate
        
        # 3. Adjust for cost-of-living
        target_net = target_net_before_col / col_factor
        
        # 4. Compute the gross base+bonus required in target locale
        target_gross = target_net / (1 - target_tax_rate)
        
        # 5. Convert RSUs to target currency
        target_rsus = rsus * exchange_rate

        # 6. Calculate monthly values and net after-tax amounts
        target_base_ratio = base_salary / (base_salary + bonus) if (base_salary + bonus) > 0 else 0
        target_bonus_ratio = bonus / (base_salary + bonus) if (base_salary + bonus) > 0 else 0
        
        # Distribute the target gross proportionally between base and bonus
        target_base = target_gross * target_base_ratio
        target_bonus = target_gross * target_bonus_ratio
    
    # 7. Calculate total compensation in target locale
    target_total = target_gross + target_rsus
    
    # 8. Calculate monthly values for source (with and without taxes)
    source_monthly_base_gross = base_salary / 12
    source_monthly_bonus_gross = bonus / 12
    source_monthly_rsus_gross = rsus / 12
    source_monthly_total_gross = (base_salary + bonus + rsus) / 12
    
    source_monthly_base_net = base_salary * (1 - source_tax_rate) / 12
    source_monthly_bonus_net = bonus * (1 - source_tax_rate) / 12
    source_monthly_rsus_net = rsus / 12  # Assuming RSUs are not taxed differently for simplicity
    source_monthly_total_net = source_monthly_base_net + source_monthly_bonus_net + source_monthly_rsus_net
    
    # 9. Calculate monthly values for target (with and without taxes)
    target_monthly_base_gross = target_base / 12
    target_monthly_bonus_gross = target_bonus / 12
    target_monthly_rsus_gross = target_rsus / 12
    target_monthly_total_gross = (target_base + target_bonus + target_rsus) / 12
    
    target_monthly_base_net = target_base * (1 - target_tax_rate) / 12
    target_monthly_bonus_net = target_bonus * (1 - target_tax_rate) / 12
    target_monthly_rsus_net = target_rsus / 12  # Assuming RSUs are not taxed differently for simplicity
    target_monthly_total_net = target_monthly_base_net + target_monthly_bonus_net + target_monthly_rsus_net
    
    # Prepare detailed results for return
    results = {
        "source_locale": source_locale,
        "target_locale": "Madrid" if source_locale == "Seattle" else "Seattle",
        "source_currency": source_currency,
        "target_currency": target_currency,
        "source_base": base_salary,
        "source_bonus": bonus,
        "source_base_plus_bonus": base_salary + bonus,
        "source_rsus": rsus,
        "source_total": base_salary + bonus + rsus,
        "source_net": source_net,
        "target_net_before_col": target_net_before_col,
        "target_net": target_net,
        "target_base": target_base,
        "target_bonus": target_bonus,
        "target_gross": target_gross,
        "target_rsus": target_rsus,
        "target_total": target_total,
        "source_tax_rate": source_tax_rate,
        "target_tax_rate": target_tax_rate,
        
        # Monthly values for source locale
        "source_monthly_base_gross": source_monthly_base_gross,
        "source_monthly_bonus_gross": source_monthly_bonus_gross,
        "source_monthly_rsus_gross": source_monthly_rsus_gross,
        "source_monthly_total_gross": source_monthly_total_gross,
        "source_monthly_base_net": source_monthly_base_net,
        "source_monthly_bonus_net": source_monthly_bonus_net,
        "source_monthly_rsus_net": source_monthly_rsus_net,
        "source_monthly_total_net": source_monthly_total_net,
        
        # Monthly values for target locale
        "target_monthly_base_gross": target_monthly_base_gross,
        "target_monthly_bonus_gross": target_monthly_bonus_gross,
        "target_monthly_rsus_gross": target_monthly_rsus_gross,
        "target_monthly_total_gross": target_monthly_total_gross,
        "target_monthly_base_net": target_monthly_base_net,
        "target_monthly_bonus_net": target_monthly_bonus_net,
        "target_monthly_rsus_net": target_monthly_rsus_net,
        "target_monthly_total_net": target_monthly_total_net
    }
    
    return results

# App title and description
st.title("Global Compensation Converter")
st.markdown("""
This tool helps you compare compensation packages between Seattle (USD) and Madrid (EUR), 
accounting for exchange rates, cost-of-living differences, and tax treatments.
""")

# Create tabs for main app, multi-year projection, and advanced settings
tab1, tab2, tab3, tab4 = st.tabs(["Quick Calculator", "Monthly Breakdown", "Multi-Year Projection", "Advanced Settings"])

# Initialize session state for source_locale if it doesn't exist
if 'source_locale' not in st.session_state:
    st.session_state['source_locale'] = "Seattle"

# Create sidebar for inputs that apply to all tabs
with st.sidebar:
    st.header("Compensation Inputs")
    
    # Source locale selection with session state
    source_locale = st.radio(
        "Select your current/offer location:",
        options=["Seattle", "Madrid"],
        horizontal=True,
        key="source_locale"  # This ties the radio button to session state
    )
    
    # Currency symbol based on locale from session state
    currency = "USD" if st.session_state['source_locale'] == "Seattle" else "EUR"
    currency_symbol = "$" if currency == "USD" else "€"
    
    # Input fields for compensation components
    st.subheader("Compensation Components")
    base_salary = st.number_input(
        f"Base Salary ({currency_symbol})",
        min_value=0.0,
        value=100000.0,
        step=1000.0,
        format="%.2f"
    )
    
    bonus = st.number_input(
        f"Bonus ({currency_symbol})",
        min_value=0.0,
        value=20000.0,
        step=1000.0,
        format="%.2f"
    )
    
    rsus = st.number_input(
        f"RSUs ({currency_symbol})",
        min_value=0.0,
        value=30000.0,
        step=1000.0,
        format="%.2f"
    )
    
    # Display total input compensation
    total_input = base_salary + bonus + rsus
    st.info(f"**Total Compensation: {currency_symbol}{total_input:,.2f}**")
    
    # Add a button to calculate
    calculate_button = st.button("Calculate", type="primary")

# Advanced settings tab
with tab4:
    st.subheader("Advanced Settings")
    
    col1_adv, col2_adv = st.columns([1, 1])
    
    with col1_adv:
        us_tax_rate = st.slider(
            "Seattle Effective Tax Rate (%)",
            min_value=10.0,
            max_value=50.0,
            value=30.0,
            step=0.5
        ) / 100
        
        spain_tax_rate = st.slider(
            "Madrid Effective Tax Rate (%) - Beckham Law",
            min_value=10.0,
            max_value=50.0,
            value=24.0,
            step=0.5
        ) / 100
    
    with col2_adv:
        exchange_rate = st.number_input(
            "Exchange Rate (1 EUR = x USD)",
            min_value=0.5,
            max_value=2.0,
            value=1.09,
            step=0.01,
            format="%.4f"
        )
        
        col_factor = st.slider(
            "Cost of Living Factor (Madrid as % of Seattle)",
            min_value=30.0,
            max_value=100.0,
            value=60.0,
            step=1.0
        ) / 100
        
    st.markdown("""
    ### Notes:
    - Seattle's default effective tax rate is set at 30%
    - Madrid's default effective tax rate under the Beckham Law is 24%
    - The default exchange rate is the 6-month average: 1 EUR ≈ 1.09 USD
    - By default, Madrid's cost of living is estimated at 60% of Seattle's
    """)
    
    # Detailed calculation explanation
    with st.expander("See Detailed Calculation Steps"):
        if 'results' in st.session_state:
            results = st.session_state['results']
            source_locale = results["source_locale"]
            target_locale = results["target_locale"]
            
            st.markdown(f"""
            ### Calculation Steps
            
            1. **Starting Compensation in {source_locale}**:
               - Base + Bonus (Gross): {format_currency(results['source_base_plus_bonus'], results['source_currency'])}
               - RSUs: {format_currency(results['source_rsus'], results['source_currency'])}
               - Total: {format_currency(results['source_total'], results['source_currency'])}
            
            2. **Calculate Net Income from Base + Bonus**:
               - Tax Rate in {source_locale}: {results['source_tax_rate']*100:.1f}%
               - Net Income: {format_currency(results['source_net'], results['source_currency'])}
            
            3. **Convert Net Income to {target_locale} Currency**:
               - Exchange Rate: 1 EUR = {exchange_rate} USD
               - Net Income in {results['target_currency']}: {format_currency(results['target_net_before_col'], results['target_currency'])}
            
            4. **Adjust for Cost of Living**:
               - Madrid is {col_factor*100:.0f}% of Seattle's cost of living
               - Adjusted Net Income: {format_currency(results['target_net'], results['target_currency'])}
            
            5. **Gross-Up to Pre-Tax Amount in {target_locale}**:
               - Tax Rate in {target_locale}: {results['target_tax_rate']*100:.1f}%
               - Required Gross Base + Bonus: {format_currency(results['target_gross'], results['target_currency'])}
            
            6. **Convert RSUs to {target_locale} Currency**:
               - RSUs in {results['target_currency']}: {format_currency(results['target_rsus'], results['target_currency'])}
            
            7. **Calculate Total Compensation in {target_locale}**:
               - Total: {format_currency(results['target_total'], results['target_currency'])}
               
            8. **Monthly Compensation Calculations**:
               - Monthly Base Salary (after tax): {format_currency(results['target_monthly_base_net'], results['target_currency'])}
               - Monthly Total Compensation (after tax): {format_currency(results['target_monthly_total_net'], results['target_currency'])}
            """)
        else:
            st.info("Enter compensation details in the sidebar and click Calculate to see detailed steps.")

# Quick calculator tab
with tab1:
    st.subheader("Quick Compensation Comparison")
    
    # Use the source_locale from session state for calculations
    source_locale_calc = st.session_state['source_locale']
    
    # Calculate the conversion
    if calculate_button or 'results' in st.session_state:
        # Calculate the results using source_locale from session state
        results = calculate_conversion(
            source_locale_calc,
            base_salary,
            bonus,
            rsus,
            us_tax_rate,
            spain_tax_rate,
            exchange_rate,
            col_factor
        )
        
        # Store in session state
        st.session_state['results'] = results
    else:
        # Use default values for initial display with source_locale from session state
        results = calculate_conversion(
            source_locale_calc,
            base_salary,
            bonus,
            rsus,
            us_tax_rate,
            spain_tax_rate,
            exchange_rate,
            col_factor
        )
        st.session_state['results'] = results
    
    # Display target locale
    results = st.session_state['results']
    target_locale = results["target_locale"]
    target_currency = results["target_currency"]
    target_symbol = "$" if target_currency == "USD" else "€"
    source_symbol = "$" if results["source_currency"] == "USD" else "€"
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    # Source locale summary
    with col1:
        st.markdown(f"### {results['source_locale']} ({results['source_currency']})")
        
        # Create metrics for source locale
        st.metric(
            "Annual Base + Bonus",
            format_currency(results["source_base_plus_bonus"], results["source_currency"])
        )
        st.metric(
            "Annual RSUs",
            format_currency(results["source_rsus"], results["source_currency"])
        )
        st.metric(
            "Annual Total",
            format_currency(results["source_total"], results["source_currency"])
        )
    
    # Target locale summary
    with col2:
        st.markdown(f"### {target_locale} ({results['target_currency']})")
        
        # Create metrics for key results
        st.metric(
            "Annual Base + Bonus",
            format_currency(results["target_gross"], target_currency)
        )
        st.metric(
            "Annual RSUs",
            format_currency(results["target_rsus"], target_currency)
        )
        st.metric(
            "Annual Total",
            format_currency(results["target_total"], target_currency)
        )
    
    # Visualization section
    st.markdown("### Compensation Breakdown")
    
    # Create data for visualization
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    
    # Source locale data
    source_data = [
        results["source_base_plus_bonus"] * (1 - results["source_tax_rate"]),  # Net Base+Bonus
        results["source_base_plus_bonus"] * results["source_tax_rate"],  # Tax on Base+Bonus
        results["source_rsus"]  # RSUs
    ]
    
    # Target locale data
    target_data = [
        results["target_gross"] * (1 - results["target_tax_rate"]),  # Net Base+Bonus
        results["target_gross"] * results["target_tax_rate"],  # Tax on Base+Bonus
        results["target_rsus"]  # RSUs
    ]
    
    # Labels for the segments
    labels = ['Net Income', 'Taxes', 'RSUs']
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # Create bar charts
    ax[0].bar(range(len(source_data)), source_data, color=colors)
    ax[0].set_title(f"{results['source_locale']} ({results['source_currency']})")
    ax[0].set_xticks(range(len(labels)))
    ax[0].set_xticklabels(labels)
    ax[0].set_ylabel(results["source_currency"])
    
    ax[1].bar(range(len(target_data)), target_data, color=colors)
    ax[1].set_title(f"{target_locale} ({results['target_currency']})")
    ax[1].set_xticks(range(len(labels)))
    ax[1].set_xticklabels(labels)
    ax[1].set_ylabel(results["target_currency"])
    
    plt.tight_layout()
    st.pyplot(fig)
            
    # Simple explanation
    with st.expander("See Calculation Details"):
        st.markdown(f"""
        ### Key Adjustments
        
        - **Exchange Rate**: 1 EUR = {exchange_rate} USD
        - **Cost of Living**: Madrid is {col_factor*100:.0f}% of Seattle's cost
        - **Tax Rates**: Seattle {us_tax_rate*100:.0f}%, Madrid {spain_tax_rate*100:.0f}% (Beckham Law)
        
        For detailed calculation steps, see the Advanced Settings tab.
        """)

# Monthly breakdown tab        
with tab2:
    st.subheader("Monthly Compensation Breakdown")

    if 'results' not in st.session_state:
        st.warning("Please enter your compensation details and click Calculate in the sidebar.")
    else:
        results = st.session_state['results']
        
        # Tax toggle
        show_after_tax = st.toggle("Show After-Tax Values", value=True)
        
        # Get locale information
        source_locale = results["source_locale"]
        target_locale = results["target_locale"]
        source_currency = results["source_currency"]
        target_currency = results["target_currency"]
        source_symbol = "$" if source_currency == "USD" else "€"
        target_symbol = "$" if target_currency == "USD" else "€"
        
        # Determine which values to show based on toggle
        if show_after_tax:
            # After-tax values
            source_monthly_base = results["source_monthly_base_net"]
            source_monthly_bonus = results["source_monthly_bonus_net"]
            source_monthly_rsus = results["source_monthly_rsus_net"]
            source_monthly_total = results["source_monthly_total_net"]
            
            target_monthly_base = results["target_monthly_base_net"]
            target_monthly_bonus = results["target_monthly_bonus_net"]
            target_monthly_rsus = results["target_monthly_rsus_net"]
            target_monthly_total = results["target_monthly_total_net"]
            
            tax_status = "(After Tax)"
        else:
            # Before-tax values (gross)
            source_monthly_base = results["source_monthly_base_gross"]
            source_monthly_bonus = results["source_monthly_bonus_gross"]
            source_monthly_rsus = results["source_monthly_rsus_gross"]
            source_monthly_total = results["source_monthly_total_gross"]
            
            target_monthly_base = results["target_monthly_base_gross"]
            target_monthly_bonus = results["target_monthly_bonus_gross"]
            target_monthly_rsus = results["target_monthly_rsus_gross"]
            target_monthly_total = results["target_monthly_total_gross"]
            
            tax_status = "(Before Tax)"
        
        # Create comparison table for monthly values
        st.markdown(f"### Monthly Breakdown {tax_status}")
        
        data = {
            "Component": ["Base Salary", "Bonus", "RSUs", "Total"],
            f"{source_locale} ({source_currency})": [
                format_currency(source_monthly_base, source_currency),
                format_currency(source_monthly_bonus, source_currency),
                format_currency(source_monthly_rsus, source_currency),
                format_currency(source_monthly_total, source_currency)
            ],
            f"{target_locale} ({target_currency})": [
                format_currency(target_monthly_base, target_currency),
                format_currency(target_monthly_bonus, target_currency),
                format_currency(target_monthly_rsus, target_currency),
                format_currency(target_monthly_total, target_currency)
            ]
        }
        
        # Convert to DataFrame and display
        monthly_df = pd.DataFrame(data)
        st.table(monthly_df)
        
        # Create visual comparison
        st.markdown("### Monthly Breakdown Visualization")
        
        # Data for stacked bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        components = ["Base", "Bonus", "RSUs"]
        source_values = [source_monthly_base, source_monthly_bonus, source_monthly_rsus]
        target_values = [target_monthly_base, target_monthly_bonus, target_monthly_rsus]
        
        x = np.arange(2)  # the label locations
        width = 0.5  # the width of the bars
        
        # Plot bars
        bottom_source = 0
        bottom_target = 0
        colors = ['#3498db', '#e74c3c', '#2ecc71']
        
        for i, (component, source_val, target_val, color) in enumerate(zip(components, source_values, target_values, colors)):
            ax.bar(0, source_val, width, bottom=bottom_source, label=component if i == 0 else "", color=color)
            ax.bar(1, target_val, width, bottom=bottom_target, color=color)
            bottom_source += source_val
            bottom_target += target_val
        
        # Add text labels on the bars
        ax.text(0, source_monthly_total * 1.02, f"{source_symbol}{source_monthly_total:.2f}", ha='center')
        ax.text(1, target_monthly_total * 1.02, f"{target_symbol}{target_monthly_total:.2f}", ha='center')
        
        # Labels and formatting
        ax.set_xticks(x)
        ax.set_xticklabels([f"{source_locale}", f"{target_locale}"])
        ax.set_ylabel(f"Monthly Amount {tax_status}")
        ax.set_title(f"Monthly Compensation Comparison {tax_status}")
        ax.legend()
        
        st.pyplot(fig)
        
        # Monthly take-home highlights
        st.subheader("Monthly Highlights")
        
        # Percentage comparison
        if source_monthly_total > 0:
            percentage_diff = ((target_monthly_total / source_monthly_total) - 1) * 100
            if percentage_diff > 0:
                st.success(f"In {target_locale}, your monthly take-home would be **{percentage_diff:.1f}% higher** than in {source_locale}.")
            elif percentage_diff < 0:
                st.error(f"In {target_locale}, your monthly take-home would be **{abs(percentage_diff):.1f}% lower** than in {source_locale}.")
            else:
                st.info(f"Your monthly take-home would be approximately the same in both locations.")

# Multi-year projection tab
with tab3:
    st.subheader("Multi-Year Compensation Projection")
    
    # Projection settings
    col1_proj, col2_proj = st.columns([1, 1])
    
    with col1_proj:
        st.markdown("### Projection Settings")
        
        num_years = st.slider(
            "Number of Years to Project",
            min_value=1,
            max_value=10,
            value=5,
            step=1
        )
        
        # Input fields for annual growth rates
        st.markdown("### Annual Growth Rates (%)")
        base_growth_rate = st.slider(
            "Base Salary Growth Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.5
        ) / 100
        
        bonus_growth_rate = st.slider(
            "Bonus Growth Rate (%)",
            min_value=0.0,
            max_value=15.0,
            value=3.0,
            step=0.5
        ) / 100
        
        rsu_growth_rate = st.slider(
            "RSU Growth Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.5
        ) / 100
        
        # Advanced projection options
        with st.expander("Advanced Projection Options"):
            exchange_rate_trend = st.slider(
                "Annual Exchange Rate Change (%)",
                min_value=-5.0,
                max_value=5.0,
                value=0.0,
                step=0.1
            ) / 100
            
            col_trend = st.slider(
                "Annual Cost of Living Gap Change (%)",
                min_value=-2.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                help="Positive values mean Madrid is becoming relatively more expensive compared to Seattle"
            ) / 100
    
    # Use the current compensation values from the calculator tab
    if 'results' not in st.session_state:
        # Calculate the results with default values if not already calculated
        # Use source_locale from session state
        results = calculate_conversion(
            st.session_state['source_locale'],
            base_salary,
            bonus,
            rsus,
            us_tax_rate,
            spain_tax_rate,
            exchange_rate,
            col_factor
        )
    else:
        results = st.session_state['results']
    
    source_locale = results["source_locale"]
    target_locale = results["target_locale"]
    source_currency = results["source_currency"]
    target_currency = results["target_currency"]
    
    # Calculate multi-year projections
    def calculate_projections(num_years):
        source_projections = []
        target_projections = []
        
        # Store initial values
        current_base = base_salary
        current_bonus = bonus
        current_rsus = rsus
        current_exchange_rate = exchange_rate
        current_col_factor = col_factor
        
        # Year 0 (current year)
        source_total = current_base + current_bonus + current_rsus
        current_results = calculate_conversion(
            source_locale,
            current_base,
            current_bonus,
            current_rsus,
            us_tax_rate,
            spain_tax_rate,
            current_exchange_rate,
            current_col_factor
        )
        target_total = current_results["target_total"]
        
        source_projections.append({
            "year": 0,
            "base": current_base,
            "bonus": current_bonus,
            "rsus": current_rsus,
            "total": source_total,
            "currency": source_currency
        })
        
        target_projections.append({
            "year": 0,
            "total": target_total,
            "currency": target_currency,
            "exchange_rate": current_exchange_rate,
            "col_factor": current_col_factor
        })
        
        # Calculate for each subsequent year
        for year in range(1, num_years + 1):
            # Update source values with growth rates
            current_base *= (1 + base_growth_rate)
            current_bonus *= (1 + bonus_growth_rate)
            current_rsus *= (1 + rsu_growth_rate)
            
            # Update rate factors
            current_exchange_rate *= (1 + exchange_rate_trend)
            current_col_factor *= (1 + col_trend)
            
            # Calculate source total for this year
            source_total = current_base + current_bonus + current_rsus
            
            # Calculate target conversion for this year
            current_results = calculate_conversion(
                source_locale,
                current_base,
                current_bonus,
                current_rsus,
                us_tax_rate,
                spain_tax_rate,
                current_exchange_rate,
                current_col_factor
            )
            target_total = current_results["target_total"]
            
            # Add to projections
            source_projections.append({
                "year": year,
                "base": current_base,
                "bonus": current_bonus,
                "rsus": current_rsus,
                "total": source_total,
                "currency": source_currency
            })
            
            target_projections.append({
                "year": year,
                "total": target_total,
                "currency": target_currency,
                "exchange_rate": current_exchange_rate,
                "col_factor": current_col_factor
            })
        
        return source_projections, target_projections
    
    # Calculate projections
    source_proj, target_proj = calculate_projections(num_years)
    
    # Convert projections to DataFrames
    source_df = pd.DataFrame(source_proj)
    target_df = pd.DataFrame(target_proj)
    
    # Calculate cumulative totals
    source_df["cumulative"] = source_df["total"].cumsum()
    target_df["cumulative"] = target_df["total"].cumsum()
    
    # Display projection results
    with col2_proj:
        st.markdown("### Projection Results")
        
        # Create metrics for cumulative values
        st.metric(
            f"Cumulative {source_locale} Compensation ({num_years} years)",
            format_currency(source_df["cumulative"].iloc[-1], source_currency)
        )
        
        st.metric(
            f"Cumulative {target_locale} Compensation ({num_years} years)",
            format_currency(target_df["cumulative"].iloc[-1], target_currency)
        )
        
        # Create toggle for viewing total per year vs. cumulative
        view_option = st.radio(
            "View Option:",
            ["Annual Compensation", "Cumulative Compensation"],
            horizontal=True
        )
    
    # Visualization of projections
    st.markdown("### Compensation Projection Over Time")
    
    # Create line chart of projections
    fig, ax = plt.subplots(figsize=(10, 6))
    
    years = source_df["year"].tolist()
    
    if view_option == "Annual Compensation":
        source_values = source_df["total"].tolist()
        target_values = target_df["total"].tolist()
        y_label = "Annual Compensation"
    else:
        source_values = source_df["cumulative"].tolist()
        target_values = target_df["cumulative"].tolist()
        y_label = "Cumulative Compensation"
    
    # Plot lines
    ax.plot(years, source_values, marker='o', linewidth=2, label=f"{source_locale} ({source_currency})")
    ax.plot(years, target_values, marker='s', linewidth=2, label=f"{target_locale} ({target_currency})")
    
    # Add labels and legend
    ax.set_xlabel("Year")
    ax.set_ylabel(y_label)
    ax.set_title(f"{view_option} Over {num_years} Years")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Set x-ticks to integers
    ax.set_xticks(years)
    
    # Format y-axis with currency
    from matplotlib.ticker import FuncFormatter
    
    def currency_formatter(x, pos):
        if x >= 1e6:
            return f'{x*1e-6:.1f}M'
        elif x >= 1e3:
            return f'{x*1e-3:.0f}K'
        else:
            return f'{x:.0f}'
    
    formatter = FuncFormatter(currency_formatter)
    ax.yaxis.set_major_formatter(formatter)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Display detailed yearly breakdown
    st.markdown("### Yearly Breakdown")
    
    # Format DataFrame columns for display
    source_display = source_df.copy()
    target_display = target_df.copy()
    
    # Format currency columns
    for col in ["base", "bonus", "rsus", "total", "cumulative"]:
        if col in source_display.columns:
            source_display[col] = source_display.apply(
                lambda x: format_currency(x[col], x["currency"]) if pd.notnull(x[col]) else "", 
                axis=1
            )
    
    for col in ["total", "cumulative"]:
        if col in target_display.columns:
            target_display[col] = target_display.apply(
                lambda x: format_currency(x[col], x["currency"]) if pd.notnull(x[col]) else "", 
                axis=1
            )
    
    # Create tabs for viewing different breakdowns
    breakdown_tabs = st.tabs([f"{source_locale} Details", f"{target_locale} Details", "Comparison"])
    
    with breakdown_tabs[0]:
        # Source locale detailed breakdown
        st.dataframe(
            source_display[["year", "base", "bonus", "rsus", "total", "cumulative"]]
            .rename(columns={
                "year": "Year",
                "base": "Base Salary",
                "bonus": "Bonus",
                "rsus": "RSUs",
                "total": "Annual Total",
                "cumulative": "Cumulative"
            }),
            use_container_width=True
        )
    
    with breakdown_tabs[1]:
        # Target locale detailed breakdown
        # Format the exchange rate and col_factor before selecting columns
        exchange_rate_formatted = target_display["exchange_rate"].apply(
            lambda x: f"{float(x):.4f}" if pd.notnull(x) else ""
        )
        
        col_factor_formatted = target_display["col_factor"].apply(
            lambda x: f"{float(x)*100:.1f}%" if pd.notnull(x) else ""
        )
        
        # Create a new DataFrame with the formatted columns
        target_display_df = pd.DataFrame({
            "year": target_display["year"],
            "total": target_display["total"],
            "cumulative": target_display["cumulative"],
            "exchange_rate": exchange_rate_formatted,
            "col_factor": col_factor_formatted
        })
        
        st.dataframe(
            target_display_df[["year", "total", "cumulative", "exchange_rate", "col_factor"]]
            .rename(columns={
                "year": "Year",
                "total": "Annual Total",
                "cumulative": "Cumulative",
                "exchange_rate": "Exchange Rate",
                "col_factor": "COL Factor"
            }),
            use_container_width=True
        )
    
    with breakdown_tabs[2]:
        # Side-by-side comparison
        comparison_df = pd.DataFrame({
            "Year": years,
            f"{source_locale} Annual": source_display["total"],
            f"{target_locale} Annual": target_display["total"],
            f"{source_locale} Cumulative": source_display["cumulative"],
            f"{target_locale} Cumulative": target_display["cumulative"]
        })
        
        st.dataframe(comparison_df, use_container_width=True)
        
        # Calculate and display relative difference
        st.markdown(f"### Relative Advantage Analysis")
        st.markdown(f"This analysis shows which location provides better compensation over time")
        
        # Convert string currency values back to numeric for calculation
        source_totals = source_df["total"].tolist()
        target_totals = target_df["total"].tolist()
        source_cum = source_df["cumulative"].tolist()
        target_cum = target_df["cumulative"].tolist()
        
        # Create comparison metrics
        advantage_df = pd.DataFrame({
            "Year": years,
            "Annual Difference (%)": [
                f"{((t / s - 1) * 100):.1f}%" if s > 0 and t > 0 else "N/A"
                for s, t in zip(source_totals, target_totals)
            ],
            "Cumulative Difference (%)": [
                f"{((t / s - 1) * 100):.1f}%" if s > 0 and t > 0 else "N/A"
                for s, t in zip(source_cum, target_cum)
            ]
        })
        
        st.dataframe(advantage_df, use_container_width=True)
        
        # Provide a summary based on the final year
        if source_totals[-1] > 0 and target_totals[-1] > 0:
            final_annual_diff = (target_totals[-1] / source_totals[-1] - 1) * 100
        else:
            final_annual_diff = 0
            
        if source_cum[-1] > 0 and target_cum[-1] > 0:
            final_cum_diff = (target_cum[-1] / source_cum[-1] - 1) * 100
        else:
            final_cum_diff = 0
        
        if final_cum_diff > 5:
            st.success(f"Over {num_years} years, working in {target_locale} provides approximately {final_cum_diff:.1f}% more in cumulative compensation compared to {source_locale}.")
        elif final_cum_diff < -5:
            st.error(f"Over {num_years} years, working in {target_locale} provides approximately {-final_cum_diff:.1f}% less in cumulative compensation compared to {source_locale}.")
        else:
            st.info(f"Over {num_years} years, the cumulative compensation is roughly equivalent between {source_locale} and {target_locale} (within 5% difference).")

# Add scenario comparison functionality
st.markdown("---")
with st.expander("Compare Multiple Scenarios"):
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    
    # Save current scenario
    if st.button("Save Current Scenario"):
        current = {
            "id": len(st.session_state.scenarios) + 1,
            "source_locale": st.session_state['source_locale'],  # Use source_locale from session state
            "base": base_salary,
            "bonus": bonus,
            "rsus": rsus,
            "target_total": results["target_total"],
            "source_currency": results["source_currency"],
            "target_currency": results["target_currency"],
            "target_locale": results["target_locale"]
        }
        st.session_state.scenarios.append(current)
        st.success(f"Scenario {current['id']} saved!")
    
    # Clear scenarios
    if st.button("Clear All Scenarios"):
        st.session_state.scenarios = []
        st.success("All scenarios cleared!")
    
    # Display saved scenarios if any
    if st.session_state.scenarios:
        st.subheader("Saved Scenarios")
        
        # Create DataFrame from scenarios
        scenarios_df = pd.DataFrame(st.session_state.scenarios)
        
        # Format the currencies
        scenarios_df["source_comp"] = scenarios_df.apply(
            lambda x: format_currency(x["base"] + x["bonus"] + x["rsus"], x["source_currency"]), 
            axis=1
        )
        scenarios_df["target_comp"] = scenarios_df.apply(
            lambda x: format_currency(x["target_total"], x["target_currency"]), 
            axis=1
        )
        
        # Display the comparison table
        display_cols = [
            "id", "source_locale", "source_comp", "target_locale", "target_comp"
        ]
        st.table(scenarios_df[display_cols].rename(columns={
            "id": "Scenario #",
            "source_locale": "Source Location",
            "source_comp": "Source Total Comp",
            "target_locale": "Target Location",
            "target_comp": "Target Total Comp"
        }))

# Add footer
st.markdown("---")
st.markdown("### Notes")
st.markdown("""
- This tool provides a rough estimate and should not be considered financial advice
- Tax rates are simplified and don't account for progressive tax brackets or deductions
- Actual cost of living may vary based on lifestyle and personal circumstances
- The Beckham Law in Spain is a special tax regime that allows qualifying foreign workers to pay a flat rate on their Spanish income
- Multi-year projections assume consistent growth rates and do not account for potential lifestyle changes or career progression
""")