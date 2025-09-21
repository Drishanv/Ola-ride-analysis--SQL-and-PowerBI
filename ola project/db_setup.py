import sqlite3
import pandas as pd

#Load dataset

data = pd.read_csv(r"C:\Users\Drishan\Downloads\ola_clean.csv")

#Connect to SQLite database (or create it if it doesn't exist)

conn = sqlite3.connect('ola_rides.db')

# Save dataframe into SQL table

data.to_sql("bookings", conn, if_exists="replace", index=False)

print("✅ Database created and table 'bookings' loaded successfully!")

# Example query

query = "SELECT booking_status, COUNT(*) as count FROM bookings GROUP BY booking_status;"
result = pd.read_sql(query, conn)
print(result)

# Close connection
conn.close()