"""
RAP Interactive Explorer
========================

Interactive tool for exploring RAP fits on individual curves.

Usage:
    streamlit run explore_rap.py

Author: The Potato Researcher 🥔
Date: November 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Must import your existing modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.universal_loader import UniversalDataLoader, load_dataset
from core.fitting import fit_rap_curve

# Page config
st.set_page_config(
    page_title="RAP Explorer",
    page_icon="🥔",
    layout="wide"
)

# Title
st.title("🥔 RAP Interactive Explorer")
st.markdown("*Explore growth curves and RAP fits interactively*")

# Sidebar - Dataset Selection
st.sidebar.header("📂 Data Selection")

# Load available datasets
try:
    loader = UniversalDataLoader()
    available_datasets = list(loader.configs.keys())
    
    if not available_datasets:
        st.error("No datasets configured in config/datasets.json")
        st.stop()
    
    # Dataset selector
    dataset_id = st.sidebar.selectbox(
        "Select Dataset",
        available_datasets,
        help="Choose from configured datasets"
    )
    
    # Load button
    if 'data_loaded' not in st.session_state or st.sidebar.button("🔄 Reload Dataset"):
        with st.spinner(f"Loading {dataset_id}..."):
            data = load_dataset(dataset_id, max_files=1)  # Start with 1 file for speed
            
            st.session_state.data = data
            st.session_state.dataset_id = dataset_id
            st.session_state.data_loaded = True
            st.session_state.current_curve_idx = 0
            st.session_state.fit_results = {}  # Store fit results
            
        st.sidebar.success(f"✅ Loaded {len(data['curves'])} curves")
    
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        data = st.session_state.data
        
        # Curve selector
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔬 Curve Selection")
        
        # Show total curves
        total_curves = len(data['curves'])
        st.sidebar.info(f"Total curves: {total_curves}")
        
        # Current curve index (using session state)
        if 'current_curve_idx' not in st.session_state:
            st.session_state.current_curve_idx = 0
        
        # Navigation buttons
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("◀ Previous"):
                if st.session_state.current_curve_idx > 0:
                    st.session_state.current_curve_idx -= 1
                    st.rerun()
        
        with col2:
            if st.button("Next ▶"):
                if st.session_state.current_curve_idx < total_curves - 1:
                    st.session_state.current_curve_idx += 1
                    st.rerun()
        
        # Direct curve selector
        curve_name = st.sidebar.selectbox(
            "Or select directly:",
            data['curves'],
            index=st.session_state.current_curve_idx,
            key='curve_selector'
        )
        
        # Update index if manually selected
        st.session_state.current_curve_idx = data['curves'].index(curve_name)
        
        # RAP Fitting Section
        st.sidebar.markdown("---")
        st.sidebar.subheader("🚀 RAP Fitting")
        
        # Fit button
        if st.sidebar.button("Run RAP Fit", type="primary"):
            with st.spinner("Fitting RAP model..."):
                time_data = data['time']
                od_data = data['data'][curve_name].dropna().values
                aligned_time = time_data[:len(od_data)]
                
                result = fit_rap_curve(aligned_time, od_data, curve_name=curve_name, verbose=False)
                
                # Store result in session state
                if 'fit_results' not in st.session_state:
                    st.session_state.fit_results = {}
                st.session_state.fit_results[curve_name] = result
                
            if result['success']:
                st.sidebar.success("✅ Fit complete!")
            else:
                st.sidebar.error(f"❌ Fit failed: {result.get('error', 'Unknown error')}")
        
        # Show fit results if available
        if 'fit_results' in st.session_state and curve_name in st.session_state.fit_results:
            result = st.session_state.fit_results[curve_name]
            
            if result['success']:
                st.sidebar.markdown("### 📊 Fit Results")
                
                # Parameters
                st.sidebar.markdown("**Parameters:**")
                st.sidebar.text(f"r (growth):  {result['r']:.3f}")
                st.sidebar.text(f"d (damping): {result['d']:.3f}")
                st.sidebar.text(f"K (capacity):{result['K']:.3f}")
                
                # Convergence
                st.sidebar.markdown("**Convergence:**")
                st.sidebar.text(f"Final util: {result['final_util']:.3f}")
                st.sidebar.text(f"Distance:   {result['distance']:.3f}")
                
                if result['converged']:
                    st.sidebar.success("✅ Locked to 85%")
                else:
                    st.sidebar.warning("⚠️ Not converged")
                
                # Model comparison
                st.sidebar.markdown("**Model Quality:**")
                st.sidebar.text(f"SSE (RAP):  {result['sse_rap']:.4f}")
                st.sidebar.text(f"SSE (Log):  {result['sse_logistic']:.4f}")
                
                if result['rap_better']:
                    st.sidebar.success("✅ RAP superior")
                else:
                    st.sidebar.info("ℹ️ Logistic better")
        
        # Main content area
        st.markdown("---")
        
        # Show current curve info
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📊 {curve_name}")
        
        with col2:
            st.metric("Curve #", f"{st.session_state.current_curve_idx + 1} / {total_curves}")
        
        with col3:
            st.metric("Time Points", len(data['time']))
        
        # Get curve data
        time_data = data['time']
        od_data = data['data'][curve_name].values
        
        # Plot with fits if available
        st.markdown("### 📈 Growth Curve")
        
        fig = go.Figure()
        
        # Raw data points
        fig.add_trace(go.Scatter(
            x=time_data,
            y=od_data,
            mode='markers',
            name='Data',
            marker=dict(size=6, color='#3498db', opacity=0.6)
        ))
        
        # Add fitted curves if available
        if 'fit_results' in st.session_state and curve_name in st.session_state.fit_results:
            result = st.session_state.fit_results[curve_name]
            
            if result['success']:
                # RAP fit
                fig.add_trace(go.Scatter(
                    x=time_data[:len(result['sim_rap'])],
                    y=result['sim_rap'],
                    mode='lines',
                    name='RAP Fit',
                    line=dict(color='#e74c3c', width=3)
                ))
                
                # Logistic fit (if available)
                if result['sim_logistic'] is not None:
                    fig.add_trace(go.Scatter(
                        x=time_data[:len(result['sim_logistic'])],
                        y=result['sim_logistic'],
                        mode='lines',
                        name='Logistic Fit',
                        line=dict(color='#f39c12', width=2, dash='dash')
                    ))
                
                # Add 85% line
                K = result['K']
                fig.add_hline(
                    y=K * 0.85,
                    line_dash="dot",
                    line_color="green",
                    annotation_text="85% Attractor",
                    annotation_position="right"
                )
        
        fig.update_layout(
            xaxis_title="Time (hours)",
            yaxis_title="OD600 / Population",
            height=500,
            hovermode='closest',
            template='plotly_white',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data summary
        st.markdown("### 📋 Data Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Initial OD", f"{od_data[0]:.3f}" if not np.isnan(od_data[0]) else "N/A")
        
        with col2:
            max_val = np.nanmax(od_data)
            st.metric("Max OD", f"{max_val:.3f}" if not np.isnan(max_val) else "N/A")
        
        with col3:
            final_val = od_data[-1]
            st.metric("Final OD", f"{final_val:.3f}" if not np.isnan(final_val) else "N/A")
        
        with col4:
            if not np.isnan(od_data[0]) and od_data[0] > 0:
                growth_ratio = final_val / od_data[0]
                st.metric("Growth Ratio", f"{growth_ratio:.1f}x" if not np.isnan(growth_ratio) else "N/A")
            else:
                st.metric("Growth Ratio", "N/A")
        
        # Detailed comparison table if fit exists
        if 'fit_results' in st.session_state and curve_name in st.session_state.fit_results:
            result = st.session_state.fit_results[curve_name]
            
            if result['success']:
                st.markdown("### 📊 Model Comparison")
                
                comparison_data = {
                    "Metric": [
                        "Final Utilization",
                        "Distance from 85%",
                        "SSE",
                        "Convergence Status"
                    ],
                    "RAP Model": [
                        f"{result['final_util']:.3f} ({result['final_util']*100:.1f}%)",
                        f"{result['distance']:.3f}",
                        f"{result['sse_rap']:.4f}",
                        "✅ CONVERGED" if result['converged'] else "❌ NOT CONVERGED"
                    ],
                    "Logistic Model": [
                        "1.000 (100%)",
                        f"{abs(1.0 - 0.85):.3f}",
                        f"{result['sse_logistic']:.4f}",
                        "N/A"
                    ]
                }
                
                st.table(pd.DataFrame(comparison_data))
                
                # Verdict
                if result['rap_better']:
                    st.success(f"🎯 **RAP model is superior** with {((result['sse_logistic'] - result['sse_rap'])/result['sse_logistic']*100):.1f}% lower error")
                else:
                    st.info("ℹ️ Logistic model has lower error for this curve")
        
        # Instructions
        st.sidebar.markdown("---")
        st.sidebar.info("""
        **How to use:**
        1. Navigate curves with ◀▶
        2. Click "Run RAP Fit"
        3. See results in sidebar
        4. Compare models in main area
        """)
    
    else:
        st.info("👆 Select a dataset from the sidebar to begin")

except Exception as e:
    st.error(f"Error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
