import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# Generate base datetime for sample data
base_date = datetime(2025, 5, 24, 7, 35, 42)  # Using your current UTC time

# Create sample matter data
matters_data = {
    'Matter_ID': [f'M{str(i).zfill(5)}' for i in range(1, 11)],
    'Client_Name': [
        'Smith & Co Ltd', 'John Davidson', 'Emma Wilson', 'Tech Solutions Inc',
        'Robert Brown', 'Sarah Parker', 'Green Enterprises', 'Michael Thompson',
        'Anderson Family Trust', 'Claire Williams'
    ],
    'Matter_Type': [
        'Commercial Contract', 'Property Settlement', 'Civil Litigation',
        'Corporate Advisory', 'Family Law', 'Conveyancing', 'Commercial Lease',
        'Estate Planning', 'Employment Law', 'Intellectual Property'
    ],
    'Responsible_Solicitor': [
        'James Wilson', 'Sarah Chen', 'Michael Roberts', 'Emma Thompson',
        'David Miller', 'Lisa Wong', 'Robert Smith', 'Jennifer Davis',
        'Andrew Johnson', 'Michelle Lee'
    ],
    'Date_Opened': [
        (base_date - timedelta(days=x)).strftime('%Y-%m-%d %H:%M:%S')
        for x in range(0, 100, 10)
    ],
    'Status': [
        'Active', 'Active', 'Pending', 'Active', 'Closed',
        'On Hold', 'Active', 'Pending', 'Closed', 'Active'
    ],
    'Billable_Amount': [
        15750.00, 8500.00, 12300.00, 25000.00, 9800.00,
        7500.00, 18900.00, None, 11200.00, 16400.00
    ],
    'Time_Recorded_Hours': [
        45.5, 22.0, 35.75, 68.25, 28.5,
        20.0, 52.25, None, 32.0, 47.75
    ],
    'Priority_Level': [
        'High', 'Medium', 'High', 'Urgent', 'Low',
        'Medium', 'High', 'Medium', 'Low', 'High'
    ],
    'Last_Activity_Date': [
        (base_date - timedelta(days=x)).strftime('%Y-%m-%d %H:%M:%S')
        for x in range(0, 50, 5)
    ]
}

# Create DataFrame
df = pd.DataFrame(matters_data)

# Check test directory exists and create if it doesn't
directory = "test_data"
if not os.path.exists(directory):
    os.makedirs(directory)

# Save as CSV
df.to_csv('test_data/sample.csv', index=False)

# For Excel, create multiple sheets
with pd.ExcelWriter('test_data/sample.xlsx') as writer:
    # Matters sheet
    df.to_excel(writer, sheet_name='Matters', index=False)

    # Time entries sheet
    time_entries = pd.DataFrame({
        'Entry_ID': [f'T{str(i).zfill(5)}' for i in range(1, 21)],
        'Matter_ID': np.random.choice(matters_data['Matter_ID'], 20),
        'Date': [(base_date - timedelta(days=x)).strftime('%Y-%m-%d %H:%M:%S')
                 for x in range(0, 40, 2)],
        'Activity_Code': ['PREP', 'CALL', 'MEET', 'DRFT', 'REVW'] * 4,
        'Description': [
            'Document preparation', 'Client phone call', 'Client meeting',
            'Draft agreement', 'Document review', 'Court appearance',
            'Research task', 'Client consultation', 'Contract review',
            'Settlement negotiation', 'Filing preparation', 'Status update',
            'Brief preparation', 'Court attendance', 'Client correspondence',
            'Title search', 'Property inspection', 'Mediation session',
            'Expert consultation', 'Final review'
        ],
        'Duration_Hours': np.random.uniform(0.5, 4.0, 20).round(2),
        'Billable': [True] * 15 + [False] * 5,
        'Rate': [350.00] * 20,
        'Staff_Member': np.random.choice(matters_data['Responsible_Solicitor'], 20)
    })
    time_entries.to_excel(writer, sheet_name='Time_Entries', index=False)

    # Trust accounting sheet
    trust_entries = pd.DataFrame({
        'Trust_ID': [f'TR{str(i).zfill(5)}' for i in range(1, 16)],
        'Matter_ID': np.random.choice(matters_data['Matter_ID'], 15),
        'Transaction_Date': [(base_date - timedelta(days=x)).strftime('%Y-%m-%d %H:%M:%S')
                             for x in range(0, 30, 2)],
        'Description': [
            'Trust Deposit', 'Settlement Funds', 'Disbursement Payment',
            'Client Funds', 'Court Filing Fee', 'Settlement Payout',
            'Initial Retainer', 'Property Deposit', 'Registration Fee',
            'Expert Witness Fee', 'Document Service Fee', 'Search Fee',
            'Stamp Duty', 'Agency Fee', 'Filing Cost'
        ],
        'Debit': [None, None, 1500.00, None, 850.00, 25000.00, None, None,
                  750.00, 2000.00, 150.00, 200.00, 3500.00, 450.00, 350.00],
        'Credit': [10000.00, 50000.00, None, 25000.00, None, None, 5000.00,
                   100000.00, None, None, None, None, None, None, None],
        'Balance': None,  # To be calculated
        'Reference': [f'REF{str(i).zfill(6)}' for i in range(1, 16)]
    })

    # Calculate running balance
    balance = 0
    balances = []
    for _, row in trust_entries.iterrows():
        if pd.notnull(row['Credit']):
            balance += row['Credit']
        if pd.notnull(row['Debit']):
            balance -= row['Debit']
        balances.append(balance)
    trust_entries['Balance'] = balances

    trust_entries.to_excel(writer, sheet_name='Trust_Accounting', index=False)