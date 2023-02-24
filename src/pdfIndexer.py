import pickle

from ai import use_key
from model import index_file

api_key = ""
use_key(api_key)
# Index the PDF file and store the result in the "out" variable
out = index_file("FAR.pdf")


# Save the "out" variable to a file
with open("index.pkl", "wb") as f:
    pickle.dump(out, f)