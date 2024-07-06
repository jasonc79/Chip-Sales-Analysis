import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from scipy.stats import pearsonr, ttest_rel
import scipy.stats as stats
import numpy as np


# total sales revenue
# total number of customers
# average number of transactions per customer

def calculate_metrics(data, store_ids):
    return data[data['store_number'].isin(store_ids)].groupby('month').agg(
        total_sales=('total_sales', 'sum'),
        total_cust=('loyalty_card_number', 'nunique'),
        avg_trans=('loyalty_card_number', lambda x: len(x) / x.nunique())
    ).reset_index()

def find_control_store(data, trial_store, potential_control, metric):
    trial_metrics = calculate_metrics(data, [trial_store])
    best_correlation = -1
    best_control_store = None
    for control in potential_control:
        control_metrics = calculate_metrics(data, [control])
        # Number of monthly data should match
        if len(trial_metrics) == len(control_metrics):
            correlation, pvalue = pearsonr(trial_metrics[metric], control_metrics[metric])
            if correlation > best_correlation: 
                best_correlation = correlation
                best_control_store = control
    return best_control_store

def perform_t_test(df, metric_trial, metric_control):
    df = df.sort_values(by='month')
    t_stat, p_value = ttest_rel(df[metric_trial], df[metric_control])
    return t_stat, p_value

# Load dataset
sheet = pd.read_csv("merged_df.csv").convert_dtypes()
# Add a month column
sheet['date'] = pd.to_datetime(sheet['date'])
sheet['month'] = sheet['date'].dt.strftime('%Y%m')
# Generate list of potential control stores + trial stores
trial_stores = [77,86,88]
potential_control_stores = sheet['store_number'].unique()
# include all stores except trial stores
potential_control_stores = [store for store in potential_control_stores if store not in trial_stores]
# Find control stores for each trial store
control_stores = {trial_store: find_control_store(sheet, trial_store, potential_control_stores, 'total_sales') for trial_store in trial_stores}
# Output of control_stores: {77: 35, 86: 231, 88: 159}

# Calculate metrics for trial and control stores
trial_metrics = {store: calculate_metrics(sheet, [store]) for store in trial_stores}
control_metrics = {store: calculate_metrics(sheet, [control_stores[store]]) for store in trial_stores}

# Compare trial and control stores by joining metrics on months
comparison_results_list = []
for store in trial_stores:
    trial_data = trial_metrics[store].set_index('month')
    control_data = control_metrics[store].set_index('month')
    comparison = trial_data.join(control_data, lsuffix='_trial', rsuffix='_control')
    comparison['store_number'] = store
    comparison_results_list.append(comparison.reset_index())
comparison_results = pd.concat(comparison_results_list, ignore_index=True)
print(comparison_results)

ttest_results = {}
for store in trial_stores:
    store_data = comparison_results[comparison_results['store_number'] == store]
    ttest_results[store] = {
        'sales_diff': perform_t_test(store_data, 'total_sales_trial', 'total_sales_control'),
        'customers_diff': perform_t_test(store_data, 'total_cust_trial', 'total_cust_control'),
        'transactions_diff': perform_t_test(store_data, 'avg_trans_trial', 'avg_trans_control')
    }
for store, results in ttest_results.items():
    print(f"Trial Store {store}")
    print(f"  Sales Difference: t-statistic = {results['sales_diff'][0]:.2f}, p-value = {results['sales_diff'][1]:.10f}")
    print(f"  Customers Difference: t-statistic = {results['customers_diff'][0]:.2f}, p-value = {results['customers_diff'][1]:.10f}")
    print(f"  Transactions Difference: t-statistic = {results['transactions_diff'][0]:.2f}, p-value = {results['transactions_diff'][1]:.10f}")
# We can see that transaction frequency isn't significantly different for store 77 with a p value of 0.3256
# Everything else is significantly different, store 86 experiences a negative decline in sales and customer frequency

# Calculate differences in metrics
comparison_results['sales_diff'] = comparison_results['total_sales_trial'] - comparison_results['total_sales_control']
comparison_results['customers_diff'] = comparison_results['total_cust_trial'] - comparison_results['total_cust_control']
comparison_results['transactions_diff'] = comparison_results['avg_trans_trial'] - comparison_results['avg_trans_control']

# print(f"Sales Diff: {stats.ttest_ind(comparison_results['total_sales_trial'], comparison_results['total_sales_control'], equal_var = False)}")
# print(f"Customer Diff: {stats.ttest_ind(comparison_results['total_cust_trial'], comparison_results['total_cust_control'], equal_var = False)}")
# print(f"Transaction Diff: {stats.ttest_ind(comparison_results['avg_trans_trial'], comparison_results['avg_trans_control'], equal_var = False)}")


# Plot results
plt.figure(figsize=(12, 8))
sns.lineplot(data=comparison_results, x='month', y='sales_diff', hue='store_number', marker='o')
plt.title('Difference in Total Sales Between Trial and Control Stores')
plt.xlabel('Month')
plt.ylabel('Sales Difference')
plt.legend(title='Trial Store Number')
plt.show()

plt.figure(figsize=(12, 8))
sns.lineplot(data=comparison_results, x='month', y='customers_diff', hue='store_number', marker='o')
plt.title('Difference in Total Customers Between Trial and Control Stores')
plt.xlabel('Month')
plt.ylabel('Customers Difference')
plt.legend(title='Trial Store Number')
plt.show()

plt.figure(figsize=(12, 8))
sns.lineplot(data=comparison_results, x='month', y='transactions_diff', hue='store_number', marker='o')
plt.title('Difference in Average Transactions per Customer Between Trial and Control Stores')
plt.xlabel('Month')
plt.ylabel('Transactions Difference')
plt.legend(title='Trial Store Number')
plt.show()

# Save the results to a PDF
import matplotlib.backends.backend_pdf
pdf = matplotlib.backends.backend_pdf.PdfPages("store_trial_analysis.pdf")
figs = [plt.figure(n) for n in plt.get_fignums()]
for fig in figs:
    fig.savefig(pdf, format='pdf')
pdf.close()

# # Analysis:
# Total sales is significantly different for stores 77 and 88, Total customer is significantly different for stores 77 and 88.
# Average Transactions is significantly different for store 86 and 88.

# The results for trial stores 77 and 88 show a significant difference in at least two of the three trials months. 88 for all three trials and 76 for two trials The trial overall 
# showed a significant increase in sales, however not reflected in trial store 86, which we must reconvene with the client on that regard

