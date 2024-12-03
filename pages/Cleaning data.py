#imports
import kagglehub
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

"""
This script uses Streamlit to visualize and analyze a cleaned dataset of car sales from eBay Germany.
Future improvements:
- Refactor the code for better readability and maintainability.
- Add markdown sections for better explanations and context.
- Enhance data visualizations and add more graphs.
- Optimize performance by using pre-downloaded data instead of downloading from Kaggle.
- Provide detailed explanations for numerical data correlations with categorical variables to improve readability.
"""

# Function to map categorical columns to numerical values
def map_column(df, column_name):
    mapping = {i: idx for idx, i in enumerate(df[column_name].unique())}
    df[column_name] = df[column_name].map(mapping)
    return mapping

# Prepare data for further interactions
@st.cache_resource
def load_clean_data():
    path = kagglehub.dataset_download("shaunoilund/auto-sales-ebay-germany-random-50k-cleaned")
    df = pd.read_csv(f"{path}/autos_random_50k_cleaned.csv")
    # Drop irrelevant columns
    irrelevant_columns = ['ab_test', 'date_crawled', 'last_seen', 'ad_created', 'car_name', 'registration_month', 'Unnamed: 0']
    df = df.drop(columns=irrelevant_columns)
    # From postal codes, drop everything except the region
    df['postal_code'] = df['postal_code'].astype(str).apply(lambda x: int(x[0]) if len(x) == 5 else 10)
    # Map categorical columns to numerical values
    categorical_columns = ['vehicle_type', 'transmission', 'model', 'fuel_type', 'brand', 'unrepaired_damage']
    mappings = {col: map_column(df, col) for col in categorical_columns}
    # List of categorical code columns to exclude
    categorical_code_columns = ['vehicle_type', 'fuel_type', 'brand', 'unrepaired_damage', 'transmission', 'model', 'postal_code']

    # Exclude these columns, leaving only quantitative features
    df_quantitative = df.drop(columns=categorical_code_columns)

    return df, df_quantitative

# Load and clean data
df, df_quantitative  = load_clean_data()

st.write(df.head())
# Streamlit sidebar for user inputs
st.sidebar.header("Graph Parameters")

# Correlation Heatmap
st.sidebar.subheader("Correlation Heatmap")
heatmap_fig_width = st.sidebar.slider("Heatmap Figure Width", 4, 12, 6)
heatmap_fig_height = st.sidebar.slider("Heatmap Figure Height", 4, 12, 4)
plt.figure(figsize=(heatmap_fig_width, heatmap_fig_height))
sns.heatmap(df_quantitative.corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation Heatmap")
st.pyplot(plt)

# Remove top 1% of the most expensive cars for easier visualization of quantitative parameters
upper_bound_99 = df['price_EUR'].quantile(0.99)
st.write(f"99th percentile upper bound for prices: {upper_bound_99}")
df_filtered = df[df['price_EUR'] <= upper_bound_99]

# Boxplot of Car Prices
st.sidebar.subheader("Boxplot of Car Prices")
boxplot_fig_width = st.sidebar.slider("Boxplot Figure Width", 4, 12, 5)
boxplot_fig_height = st.sidebar.slider("Boxplot Figure Height", 4, 12, 3)
plt.figure(figsize=(boxplot_fig_width, boxplot_fig_height))
sns.boxplot(data=df_filtered, x='price_EUR')
plt.title("Boxplot of Car Prices")
plt.xlabel("Price (EUR)")
st.pyplot(plt)

# Distribution of Car Prices
st.sidebar.subheader("Distribution of Car Prices")
histplot_bins = st.sidebar.slider("Number of Bins", 10, 100, 50)
histplot_fig_width = st.sidebar.slider("Histogram Figure Width", 4, 12, 5)
histplot_fig_height = st.sidebar.slider("Histogram Figure Height", 4, 12, 3)
plt.figure(figsize=(histplot_fig_width, histplot_fig_height))
sns.histplot(df_filtered['price_EUR'], bins=histplot_bins, kde=True)
plt.title("Distribution of Car Prices")
plt.xlabel("Price (EUR)")
plt.ylabel("Frequency")
st.pyplot(plt)

# Price vs Power
st.sidebar.subheader("Price vs Power")
scatter_power_fig_width = st.sidebar.slider("Scatter Plot Figure Width (Power)", 4, 12, 5)
scatter_power_fig_height = st.sidebar.slider("Scatter Plot Figure Height (Power)", 4, 12, 3)
plt.figure(figsize=(scatter_power_fig_width, scatter_power_fig_height))
plt.scatter(df_filtered['power_ps'], df_filtered['price_EUR'], alpha=0.5)
plt.xlabel('Power (PS)')
plt.ylabel('Price (EUR)')
plt.title('Price vs Power')
st.pyplot(plt)

# Price vs Registration Year
st.sidebar.subheader("Price vs Registration Year")
scatter_year_fig_width = st.sidebar.slider("Scatter Plot Figure Width (Year)", 4.0, 12.0, 4.8)
scatter_year_fig_height = st.sidebar.slider("Scatter Plot Figure Height (Year)", 4.0, 12.0, 3.0)
plt.figure(figsize=(scatter_year_fig_width, scatter_year_fig_height))
plt.scatter(df_filtered['registration_year'], df_filtered['price_EUR'], alpha=0.5)
plt.xlabel('Registration Year')
plt.ylabel('Price (EUR)')
plt.title('Price vs Registration Year')
st.pyplot(plt)

# Average Price by Odometer Range
st.sidebar.subheader("Average Price by Odometer Range")
odometer_bins = st.sidebar.slider("Number of Odometer Bins", 5, 20, 10)
df['odometer_bins'] = pd.cut(df['odometer_km'], bins=odometer_bins)
avg_price_per_bin = df.groupby('odometer_bins', observed=False)['price_EUR'].mean()

plt.figure()
avg_price_per_bin.plot(kind='bar')
plt.xlabel("Odometer (KM)")
plt.ylabel("Average Price (EUR)")
plt.title("Average Price by Odometer Range")
st.pyplot(plt)
