import pandas as pd
import numpy as np
from datetime import datetime

# Create sample financial data
np.random.seed(42)  # For reproducibility

# Generate dates
dates = pd.date_range(start='2025-01-01', end='2025-03-31', freq='D')
dates = np.random.choice(dates, size=50)

# Generate descriptions
descriptions = [
    "Office Rent Payment", "Client Invoice Payment", "Software Subscription",
    "Office Supplies Purchase", "Consulting Services", "Utility Bill Payment",
    "Employee Salary", "Marketing Campaign", "Travel Expenses", "Equipment Purchase",
    "Insurance Premium", "Client Retainer", "Internet Service", "Professional Development",
    "Accounting Services", "Legal Services", "Bank Fees", "Maintenance Services",
    "Printing Services", "Catering Services"
]

# Generate amounts (positive for revenue, negative for expenses)
amounts = []
for _ in range(50):
    if np.random.random() < 0.3:  # 30% chance of revenue
        amounts.append(np.random.uniform(500, 5000))
    else:  # 70% chance of expense
        amounts.append(-np.random.uniform(100, 2000))

# Create DataFrame
df = pd.DataFrame({
    'date': dates,
    'description': np.random.choice(descriptions, size=50),
    'amount': amounts
})

# Sort by date
df = df.sort_values('date')

# Format date as string
df['date'] = df['date'].dt.strftime('%Y-%m-%d')

# Save to CSV
df.to_csv('/home/ubuntu/financial_app/data/sample_financial_data.csv', index=False)

# Save to Excel
df.to_excel('/home/ubuntu/financial_app/data/sample_financial_data.xlsx', index=False)
