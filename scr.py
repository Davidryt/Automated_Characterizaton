import pandas as pd

# Assuming you have the paths to your CSV files
path_tap_0 = 'tap_0.csv'
path_tap_1 = 'tap_1.csv'

# Read the CSV files
df_tap_0 = pd.read_csv(path_tap_0, header=None)
df_tap_1 = pd.read_csv(path_tap_1, header=None)

# Drop the third column
df_tap_0 = df_tap_0.iloc[:, :2]
df_tap_1 = df_tap_1.iloc[:, :2]

# Set the second column as index
df_tap_0.set_index(1, inplace=True)
df_tap_1.set_index(1, inplace=True)

# Ensure the first column has a proper label for both DataFrames
df_tap_0.columns = ['Value']
df_tap_1.columns = ['Value']

# Perform a join operation to match rows based on the ID (index)
matched_df = df_tap_0.join(df_tap_1, lsuffix='_tap_0', rsuffix='_tap_1')

# Calculate the difference and convert from nanoseconds to milliseconds
matched_df['Difference'] = (matched_df['Value_tap_1'] - matched_df['Value_tap_0']) / 1000000

# Save the result to a CSV file, including the conversion to milliseconds
matched_df[['Difference']].to_csv('results.csv', index_label='ID')

print("Results, converted to milliseconds, have been saved to 'results.csv'.")

