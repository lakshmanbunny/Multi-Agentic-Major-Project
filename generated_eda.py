import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"

try:
    df = pd.read_csv(url)
except Exception as e:
    print(f"Error loading dataset: {e}")
    exit()

df['TotalCharges'] = df['TotalCharges'].replace(' ', np.nan)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'])

numeric_cols = df.select_dtypes(include=np.number).columns
categorical_cols = df.select_dtypes(include='object').columns

for col in numeric_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].mean(), inplace=True)

for col in categorical_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].mode()[0], inplace=True)

print("Dataset Info:")
df.info()
print("\nDataset Shape:")
print(df.shape)
print("\nSummary Statistics:")
print(df.describe(include='all'))

numeric_features_for_plot = [col for col in numeric_cols if col != 'customerID']

if numeric_features_for_plot:
    fig, axes = plt.subplots(nrows=len(numeric_features_for_plot), ncols=1, figsize=(8, 4 * len(numeric_features_for_plot)))
    if len(numeric_features_for_plot) == 1:
        axes = [axes]
    for i, col in enumerate(numeric_features_for_plot):
        sns.histplot(df[col], kde=True, ax=axes[i])
        axes[i].set_title(f'Distribution of {col}')
    plt.tight_layout()
    plt.savefig('numerical_features_histograms.png')
    plt.close()

df_corr = df.copy()
if 'Churn' in df_corr.columns and df_corr['Churn'].dtype == 'object':
    df_corr['Churn'] = df_corr['Churn'].map({'Yes': 1, 'No': 0})

numeric_for_corr = df_corr.select_dtypes(include=np.number).drop(columns=['customerID'], errors='ignore')
correlation_matrix = numeric_for_corr.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Matrix of Numerical Features')
plt.savefig('correlation_matrix_heatmap.png')
plt.close()