import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import scipy.stats as stats 
import numpy as np 


sheet = pd.read_csv("merged_df.csv").convert_dtypes()
print(sheet.describe())

# Total Sales per chip company and customer type over the full period
grouped = sheet.groupby(['lifestage', 'product_name'])
sales = grouped['total_sales'].sum().reset_index()
plt.figure(figsize=(12, 8))
sns.catplot(data=sales, x='product_name', y='total_sales', hue='lifestage', kind="bar", height=8, aspect=1.5)
plt.title('Total Sales of Chip Product per Customer Category')
plt.xlabel('Product Name')
plt.ylabel('Total Sales')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()


# # Understanding customer segments
# # Are there more customer than chip purchases - multi-pack purchases
grouped = sheet.groupby(['lifestage', 'premium_customer'])
average_quantity = grouped['product_quantity'].mean().reset_index()
average_quantity.columns = ['lifestage', 'premium_customer', 'average_quantity']
print(average_quantity)
plt.figure(figsize=(12,8))
sns.barplot(data=average_quantity, x='lifestage', y='average_quantity', hue='premium_customer', errorbar=None, palette='muted')
plt.xlabel('Lifestage')
plt.ylabel('Average Quantity')
plt.title('Average Quantity of Chips Spent by Customer Type')
plt.legend(title='Customer Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Older and younger families buy more chip packs on average per purchase, however it is differences in average quantities aren't large, we can check if this difference is significant

# Welch t-test on quantities between sales from mainstream young singles/couples and mainstream midage singles/couples
young_single_couple = sheet[(sheet['lifestage'] == 'YOUNG SINGLES/COUPLES') & (sheet['premium_customer'] == 'Mainstream')]

midage_singles_couple = sheet[(sheet['lifestage'] == 'MIDAGE SINGLES/COUPLES') & (sheet['premium_customer'] == 'Mainstream')]

print(stats.ttest_ind(young_single_couple['product_quantity'], midage_singles_couple['product_quantity'], equal_var = False))

# Yes all customers are spending on average more than one chip purchase per transaction
# - Who spends the most on chips (Average sales), describing customers by lifestage and purchasing power
grouped = sheet.groupby(['lifestage', 'premium_customer'])
average_sales = grouped['total_sales'].mean().reset_index()
average_sales.columns = ['lifestage', 'premium_customer', 'average_sales']
print(average_sales)
plt.figure(figsize=(12,8))
sns.barplot(data=average_sales, x='lifestage', y='average_sales', hue='premium_customer', errorbar=None, palette='muted')
plt.xlabel('Lifestage')
plt.ylabel('Average Sales')
plt.title('Average Sales Grouped by Customer Type')
plt.legend(title='Customer Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Average chip count purchase 
grouped = sheet.groupby(['lifestage', 'premium_customer'])
average_pack_size = grouped['pack_size'].mean().reset_index()
average_pack_size.columns = ['lifestage', 'premium_customer', 'pack_size']

# print(average_pack_size)
plt.figure(figsize=(12,8))
# plt.gca().yaxis.set_major_locator(MultipleLocator(0.05))  # Set the interval between major ticks
# plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Format tick labels to two decimal places
# plt.ylim(0, max(average_quantity['average_quantity']) * 1.2)
sns.barplot(data=average_pack_size, x='lifestage', y='pack_size', hue='premium_customer', errorbar=None, palette='muted')
plt.xlabel('Lifestage')
plt.ylabel('Average Pack Size')
plt.title('Average Pack Size of Chips Spent by Customer Type')
plt.legend(title='Customer Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
# Mainstream young and midage singles/couples are leading the sales of chip purchases
# How premium their general purchasing behaviour is
# How many customers are in each segment
total_cust = sheet.groupby(['lifestage', 'premium_customer']).size().reset_index(name='counts')

# Sort the results
total_cust = total_cust.sort_values(by=['lifestage', 'premium_customer']).reset_index(drop=True)

print(total_cust)
# - How many chips are bought per customer by segment
grouped = sheet.groupby(['lifestage', 'premium_customer'])
total_sales = grouped['total_sales'].sum().reset_index(name='Revenue')
total_sales = total_sales.sort_values(by=['lifestage', 'premium_customer']).reset_index(drop=True)
print(total_sales)

sheet['date'] = pd.to_datetime(sheet['date'])
sheet['month'] = sheet['date'].dt.strftime('%Y%m')
# mainstream retirees, young singles and budget older families are driving sales

# Customer spending type, how do they track in terms of spending per month
grouped = sheet.groupby(['premium_customer', 'month'])
sales = grouped['total_sales'].sum().reset_index()
sales.to_csv("sales_customer_spending_type.csv", index=False)
plt.figure(figsize=(12, 8))
sns.lineplot(data=sales, x='month', y='total_sales', hue='premium_customer', marker='o')
plt.title('Total Monthly Sales based on Spending Type')
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.legend(title='Lifestage', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.legend(title='Customer Spending Type')
plt.tight_layout()
plt.show()


# Customer spending based on lifestage, how much is spent per month
grouped = sheet.groupby(['lifestage', 'month'])
sales = grouped['total_sales'].sum().reset_index()
sales.to_csv("sales_lifestage.csv", index=False)
plt.figure(figsize=(12, 8))
sns.lineplot(data=sales, x='month', y='total_sales', hue='lifestage', marker='o')
plt.title('Total Monthly Sales based on Lifestage of the Customer')
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.legend(title='Lifestage', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
# On average older singles, families, couples and retirees are spending more on chips across the month

# Customer spending based on lifestage and spending type per month
grouped = sheet.groupby(['lifestage', 'premium_customer', 'month'])
sales = grouped['total_sales'].sum().reset_index()
sales['cust_type'] = sales['lifestage'] + ' - ' + sales['premium_customer'].astype(str)
sales.to_csv("sales_lifestage.csv", index=False)
plt.figure(figsize=(12, 8))
sns.lineplot(data=sales, x='month', y='total_sales', hue='cust_type', marker='o')
plt.title('Total Monthly Sales based on Lifestage of the Customer')
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.legend(title='Lifestage', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

