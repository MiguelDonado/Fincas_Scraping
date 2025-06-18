# Save to a pickle file
with open("data.pkl", "wb") as pkl_file:
    pickle.dump(data, pkl_file)

# Load it later
with open("data.pkl", "rb") as pkl_file:
    loaded_data = pickle.load(pkl_file)