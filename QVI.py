# Removing outliers
# Who spends on chips and what chip brand
# What drives spending for each customer segment

import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from scipy.stats import ttest_ind

QVI_purchase = pd.read_csv("QVI_purchase_behaviour.csv").convert_dtypes()
QVI_transaction_data = pd.read_excel("QVI_transaction_data.xlsx").convert_dtypes()

new_QVI_purchase_names = {
    "LYLTY_CARD_NBR": "loyalty_card_number",
    "LIFESTAGE": "lifestage",
    "PREMIUM_CUSTOMER": "premium_customer"
}

new_QVI_transaction_names = {
    "DATE": "date",
    "STORE_NBR": "store_number",
    "LYLTY_CARD_NBR": "loyalty_card_number",
    "TXN_ID": "transaction_id",
    "PROD_NBR": "product_number",
    "PROD_NAME": "product_name",
    "PROD_QTY": "product_quantity",
    "TOT_SALES": "total_sales"
}
QVI_purchase = QVI_purchase.rename(columns=new_QVI_purchase_names)
QVI_transaction_data = QVI_transaction_data.rename(columns=new_QVI_transaction_names).drop_duplicates(ignore_index=True)

QVI_purchase.info()
QVI_transaction_data.info()
# From here, I saw an outlier of a customer purchasing 200 packets of chips in a single purchase - implying it could be a business purchase
#print(QVI_transaction_data.describe())
# Removing 200 packet chip purchase product quantity outlier
QVI_transaction_data = QVI_transaction_data.drop(QVI_transaction_data[QVI_transaction_data.product_quantity == 200.0].index)
#print(QVI_transaction_data.describe())
# Check for duplicates
#print(QVI_purchase.loc[QVI_purchase.duplicated(keep=False)])
#print(QVI_transaction_data.loc[QVI_transaction_data.duplicated(keep=False)])

# Convert DATE column to a date format
QVI_transaction_data['date'] = pd.to_datetime(QVI_transaction_data['date'], origin='1899-12-30', unit='D')

# Display the first few rows to check the conversion
#print(QVI_transaction_data.head())

# Examine unique product names
unique_product_names = QVI_transaction_data['product_name'].unique()
#print(f"Number of unique product names: {len(unique_product_names)}")
# Count the frequency of each product name
product_name_counts = QVI_transaction_data['product_name'].value_counts()
#print(product_name_counts.head(114))  # Display the top 20 most common product names

# remove rows in substring salsa from product name
substring = 'Salsa'
filter = QVI_transaction_data['product_name'].str.contains(substring)
QVI_transaction_data_filtered = QVI_transaction_data[~filter]
# print(QVI_transaction_data_filtered)

# Count the number of dates
num_dates = QVI_transaction_data["date"].unique()
print(f"There are {num_dates} unique dates")
# There are 364 days so therefore there is a missing date
# create graph of number of transactions with respect to the dates
transaction_counts = QVI_transaction_data['date'].value_counts().sort_index()
transaction_counts = transaction_counts.reset_index()
transaction_counts.columns = ['dates', 'transaction_count']
plt.figure(figsize=(12,6))
sns.lineplot(data=transaction_counts, x='dates', y='transaction_count', marker='o')
plt.xlabel('Date')
plt.ylabel('Number of Transactions')
plt.title('Number of Transactions per Date')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Zoom in on December as high volume of transactions occur there
december_data = transaction_counts[(transaction_counts['dates'] >= '2018-12-01') & (transaction_counts['dates'] <= '2018-12-31')]
plt.figure(figsize=(12,6))
sns.lineplot(data=december_data, x='dates', y='transaction_count', marker='o')
plt.xlabel('Date')
plt.ylabel('Number of Transactions')
plt.title('Transactions in December 2018')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Christmas Day is missing - Implying a public holiday so shops are closed
# Create pack size variable
QVI_transaction_data_filtered['pack_size'] = QVI_transaction_data_filtered['product_name'].str.extract(r'(\d+)').astype(float)
print(QVI_transaction_data_filtered['pack_size'].describe())

# Amend brand names
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.split().str.get(0)
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Red', 'RRD')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Smith', 'Smiths')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Smithss', 'Smiths')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Dorito', 'Doritos')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Doritoss', 'Doritos')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Snbts', 'Sunbites')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Infzns', 'Infuzions')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('WW', 'Woolworths')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('NCC', 'Natural')
QVI_transaction_data_filtered['product_name'] = QVI_transaction_data_filtered['product_name'].str.replace('Grain', 'GrnWves')



# Change options to display more rows
pd.set_option('display.max_rows', 120)  # or a higher number if necessary
product_name_counts = QVI_transaction_data_filtered['product_name'].value_counts()
print(product_name_counts.head(114))  # Display the top 20 most common product names


# merge transaction and purchase transaction on the relationship loyalty card number
merged_df = pd.merge(QVI_purchase, QVI_transaction_data_filtered, on='loyalty_card_number')
merged_df.to_csv("merged_df.csv", index=False)
QVI_purchase.to_csv("QVI_purchase_cleansed.csv", index=False)
QVI_transaction_data.to_excel("QVI_transaction_data_cleansed.xlsx", index=False)


# Finished data cleansing
# Data Summaries


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

