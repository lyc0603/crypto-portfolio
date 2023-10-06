"""
Script to evaluate the performance
"""

from scripts.process.mean_var_opt import df_res
from environ.process.pfm_evl import cal_sharpe

# calculate the sharpe ratio
print(f"Sharpe ratio for the optimized portfolio: {cal_sharpe(df_res):.4f}")
