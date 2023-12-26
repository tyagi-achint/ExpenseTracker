# My Expense Tracker

## Introduction

This is a simple web application built using Flask, a Python web framework, to track and visualize expenses from a CSV file. The application allows users to upload a CSV file containing transaction data, performs data validation and cleaning, and presents a summary of income, expenses, and a breakdown of expenses by category. The expense data is visualized using a bar chart, and users can filter the chart based on predefined amount ranges.

## Features

- **Upload CSV File:** Users can upload a CSV file containing transaction data.
- **Data Validation:** The application performs validation checks on the CSV file to ensure it contains the required columns ('Amount', 'Type', 'Beneficiary name').
- **Data Cleaning:** Empty or invalid entries in the 'Type', 'Beneficiary name', and 'Amount' columns are handled.
- **Dynamic Mapping:** The application dynamically maps similar beneficiary names to a standardized name for better categorization.
- **Manual Mapping:** Specific beneficiary names are manually mapped for accurate categorization.
- **Expense Summary:** Provides an overview of total income, total expenses, and a breakdown of expenses by category.
- **Filtering:** Users can filter the expense chart based on predefined amount ranges.

## Usage

1. **Upload CSV File:**
   - Click on the "Upload CSV File" button on the home page.
   - Select a CSV file with the required columns ('Amount', 'Type', 'Beneficiary name') and click "Upload."

2. **View Summary:**
   - After uploading, click on the file name to view the expense summary.
   - The summary includes total income, total expenses, and a table of categorized expenses.

3. **Filter Chart:**
   - Use the dropdown menu to filter the expense chart based on predefined amount ranges.
   - The chart dynamically updates based on the selected filter.

## Prerequisites

- Python 3.x
- Flask
- Pandas
- NumPy
- Chart.js (JavaScript library)

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/tyagi-achint/expense-tracker.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:

   ```bash
   python app.py
   ```

4. Open your web browser and go to `http://localhost:5000` to use the Expense Tracker.

## File Structure

- **app.py:** Flask application code.
- **templates/:** HTML templates for the web pages.
- **static/:** Static files (CSS, JS, images).
- **uploads/:** Folder to store uploaded CSV files.

## Customization

- **Dynamic Mapping:** Adjust the `add_to_dynamic_mapping` function in `app.py` to modify dynamic mapping behavior.
- **Manual Mapping:** Update the `manual_mapping` dictionary in `app.py` to add or modify manual mappings.

## Contributors

-Achint Tyagi <achinttyagi001@gmail.com>

Feel free to contribute, report issues, or suggest improvements.

