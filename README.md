# 🚖 Ola Ride Analysis  

## 📌 Project Overview  
The rise of ride-sharing platforms has transformed urban mobility, offering convenience and affordability to millions of users. **Ola**, a leading ride-hailing service, generates vast amounts of data related to ride bookings, driver availability, pricing, and customer preferences.  

This project focuses on analyzing Ola’s ride-sharing data to:  
- Enhance **operational efficiency**  
- Improve **customer satisfaction**  
- Optimize **business strategies**  

The solution involves:  
- Cleaning and processing raw ride data  
- Performing exploratory data analysis (EDA)  
- Building a **SQLite database** for structured querying  
- Creating a **Streamlit-based dashboard** for interactive exploration  
- Embedding **Power BI visuals** for dynamic reporting  

## 🎯 Business Use Cases  
- Identify **peak demand hours** and optimize driver allocation  
- Analyze **customer behavior** for personalized marketing strategies  
- Understand **pricing and surge patterns**  
- Detect anomalies or potential **fraudulent activities**  
- Track **ride cancellations** and reasons for operational improvements  

## 🛠️ Tech Stack  
- **Python** – Data processing & EDA  
- **Pandas, Seaborn, Matplotlib** – Data visualization  
- **SQLite3** – Database storage & queries  
- **Streamlit** – Interactive dashboard  
- **Power BI (optional)** – Advanced visualization  # Ola-ride-analysis--SQL-and-PowerBI
 OLA, a leading ride-hailing service, generates vast amounts of data related to ride bookings, driver availability, fare calculations, and customer preferences.


## ⚙️ Setup Instructions  

### 1️⃣ Clone the repository  

```bash
git clone https://github.com/yourusername/ola-ride-analysis.git
cd ola-ride-analysis

2️⃣ Install dependencies

pip install -r requirements.txt

3️⃣ Create SQLite database

python db_setup.py

This will create ola_rides.db with a bookings table.

4️⃣ Run the Streamlit dashboard

streamlit run app.py


## 📊 Dashboard Features

SQL Query Runner → Write and run custom queries

1. Interactive Filters → Filter by booking status, vehicle type, ride distance, booking value, ratings, etc.

2. Search Options → Search by customer ID, location, or keywords

3. Table View → Clean tabular display of rides (customizable)

4. Power BI embedding for richer visuals

## 📂 Project Structure  

ola project/
│── app.py
│── db_setup.py
│── ola_rides.db
│── queries.sql
│── requirements.txt
│── runtime.txt

