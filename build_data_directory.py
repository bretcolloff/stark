from src.helpers.populate_data import *

import os

# Create the default Data base directory, and a Test folder to put
# our default test data in.
os.makedirs("Data/Test", exist_ok=True)

# Download ETHBTC, with the default 1 hour intervals to our folder.
get_symbol_history("Data/Test", "ETHBTC")
