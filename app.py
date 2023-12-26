from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import pandas as pd
import numpy as np
from datetime import datetime
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'






def file_exists(filename):
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename))

def find_skiprows(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if 'Beneficiary name' in line and 'Amount' in line:
            return i
    return 0


def find_endrows(filename):
    error_rows = []

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if 'Beneficiary name' in line and 'Amount' in line:
                skiprows = i
                break
        else:
            skiprows = 0

        df = pd.read_csv(filename, skiprows=skiprows)

        # Check 'Type' column
        type_column_number = next((i + 1 for i, col_name in enumerate(df.columns) if 'Type' in col_name), None)
        if type_column_number:
            type_column = df.iloc[:, type_column_number - 1]
            non_empty_type_column = type_column[type_column.notna() & (type_column.astype(str).str.strip() != '')]
            valid_types = ['c', 'd', 'credit', 'debit']
            invalid_type_rows = non_empty_type_column[~non_empty_type_column.str.lower().isin(valid_types)]
            error_rows.extend(invalid_type_rows.index.tolist())

        # Check 'Beneficiary name' column
        beneficiary_name_column_number = next((i + 1 for i, col_name in enumerate(df.columns) if 'Beneficiary name' in col_name), None)
        if beneficiary_name_column_number:
            beneficiary_name_column = df.iloc[:, beneficiary_name_column_number - 1]
            empty_name_rows = beneficiary_name_column[beneficiary_name_column == '']
            error_rows.extend(empty_name_rows.index.tolist())

        # Check 'Amount' column
        amount_column_number = next((i + 1 for i, col_name in enumerate(df.columns) if 'Amount' in col_name), None)
        if amount_column_number:
            amount_column = df.iloc[:, amount_column_number - 1]
            non_empty_amount_column = amount_column[amount_column.notna() & (amount_column.astype(str).str.strip() != '')]
            numeric_amount_column = pd.to_numeric(non_empty_amount_column, errors='coerce')
            non_numeric_rows = numeric_amount_column[~numeric_amount_column.notnull()]
            error_rows.extend(non_numeric_rows.index.tolist())

    except pd.errors.EmptyDataError:
        print("Empty CSV file")
        return None
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred during CSV reading or column checks: {e}")
        return None

    endrows = sorted(set(error_rows))
    return endrows[0] if endrows else None

def add_to_dynamic_mapping(dynamic_mapping, name1, name2):
    standardized_name1 = name1.replace(" ", "").lower()
    standardized_name2 = name2.replace(" ", "").lower()

    if standardized_name1 == standardized_name2:
        dynamic_mapping[name1] = name2
    
    return dynamic_mapping


@app.route('/')
def index():
    current_year = datetime.now().year
    return render_template('index.html', current_year=current_year)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    if file_exists(file.filename):
        os.remove(filename)

    file.save(filename)
    return redirect(url_for('process_file', filename=file.filename))


@app.route('/<filename>')
def process_file(filename):
    current_year = datetime.now().year
    return render_template('result.html', filename=filename,current_year=current_year)


@app.route('/get_data/<filename>')
def get_data(filename):
    try:
        full_file_path = os.path.join('uploads', filename)
        skiprows = find_skiprows(full_file_path)
        end_rows = find_endrows(full_file_path)
        norows = end_rows - skiprows
        logging.info(f"End Rows: {end_rows}")
        logging.info(f"Skip Rows: {skiprows}")
        logging.info(f"No. of Rows to Read: {norows}")

        if norows > 0:
            df = pd.read_csv(full_file_path, skiprows=skiprows, nrows=norows)
        else:
            df = pd.read_csv(full_file_path, skiprows=skiprows)

        df["Beneficiary name"] = df["Beneficiary name"].replace(np.nan, "Other")
        dynamic_mapping = {}

        unique_names = df["Beneficiary name"].unique()
        for i in range(len(unique_names)):
            for j in range(i + 1, len(unique_names)):
                dynamic_mapping = add_to_dynamic_mapping(dynamic_mapping, unique_names[i], unique_names[j])

        manual_mapping = {
            "ZOMATO MEDIA PRIVATE LIMITED": "Zomato Limited",
            "Amazon Pay Balance": "Amazon Pay",
            "Dmart India": "Dmart",
        }

        category_mapping = {**dynamic_mapping, **manual_mapping}
        
        df["Beneficiary name"] = df["Beneficiary name"].replace(category_mapping)

        expenses_by_category = df[df["Type"] == "D"].groupby(["Beneficiary name"]).agg({"Amount": "sum", "Date and Time": list}).reset_index()
        expenses_by_category["SerialNumber"] = range(1, len(expenses_by_category) + 1)

        expenses_by_category["Date and Time"] = expenses_by_category["Date and Time"].apply(
            lambda dates: [datetime.strptime(date_str, "%d-%m-%Y %H:%M").strftime("%d %B") for date_str in dates])

        income = df[df['Type'] == 'C']['Amount'].sum()
        expense = expenses_by_category["Amount"].sum()

        expenses_by_category_dict = expenses_by_category.to_dict(orient='records')

        return jsonify({'income': income, 'expense': expense, 'expenses_by_category': expenses_by_category_dict}), 200

    except FileNotFoundError:
        return jsonify({'error': 'CSV file not found'}), 404
    except pd.errors.EmptyDataError:
        return jsonify({'error': 'Empty CSV file'}), 400
    except pd.errors.ParserError as e:
        return jsonify({'error': f'Error parsing CSV file: {e}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500

if __name__ == '__main__':
    
    app.run(debug=True)


