# test_sniffer.py
import pandas as pd
import sys
import io

# --- 1. SIMULATE THE DATA ENGINEER'S WORK ---
# We create a dataframe inside a function to ensure it's in 'locals()', 
# or at the top level to be in 'globals()', just like real life.
def generate_data():
    data = {
        'age': [25, 30, 35],
        'bmi': [22.5, 26.0, 30.1],
        'diabetes': [0, 1, 0]
    }
    # Notice we give it a weird name like 'df_final' to prove the sniffer works
    df_final = pd.DataFrame(data)
    return df_final

# Create the variable in the global scope
my_random_variable_name = generate_data()

# --- 2. THE SNIFFER CODE (Copy-Pasted from main.py) ---
introspection_code = """
import pandas as pd

# COMBINED SCOPE SEARCH (The Fix)
search_space = {**globals(), **locals()}
target_df = None

print("🔍 Scanning memory for DataFrames...", flush=True)

for var_name, var_val in list(search_space.items()):
    # Ignore internal python variables
    if var_name.startswith('_'): 
        continue
        
    if isinstance(var_val, pd.DataFrame):
        print(f"✅ FOUND DataFrame! Variable name: '{var_name}'", flush=True)
        target_df = var_val
        break

if target_df is not None:
    print('DATA_SCHEMA_LOCKED:' + str(list(target_df.columns)), flush=True)
else:
    print('DATA_SCHEMA_ERROR: No DataFrame found', flush=True)
"""

# --- 3. EXECUTE THE TEST ---
print("--- STARTING UNIT TEST ---")
# We use exec() because that is exactly what the Browser Agent does
exec(introspection_code)
print("--- TEST FINISHED ---")