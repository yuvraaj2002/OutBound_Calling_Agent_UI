import pandas as pd
import re

def validate_calling_file(df, success_messages, validation_messages):
    """
    Validates the uploaded file for the sequential calling module.
    Returns True if all validations pass, otherwise False.
    """
    required_columns = ["Tag Type", "Contact Number", "Contact Name", "Contact Email"]
    group1, group2, group3 = [], [], []

    # 2. Check all required columns
    if all(col in df.columns for col in required_columns):
        group1.append("All required columns present")
    else:
        validation_messages.append("Missing required columns. Please ensure the file has Tag Type, Contact Number, Contact Name, and Contact Email columns.")
        return False

    # 3. Ensure no missing values
    if not df[required_columns].isnull().any().any():
        group1.append("No missing values in required columns")
    else:
        validation_messages.append("Missing values in required columns. Please fill in all required fields.")
        return False

    # 4. Ensure no duplicate rows
    if not df.duplicated().any():
        group2.append("No duplicate rows found")
    else:
        validation_messages.append("Duplicate rows found in the file. Please remove duplicates before proceeding.")
        return False

    # 5. Ensure at most 70 rows
    if len(df) <= 70:
        group2.append(f"File contains {len(df)} rows (within 70 row limit)")
    else:
        validation_messages.append("The file contains more than 70 rows. Please reduce the number of rows to 70 or less.")
        return False

    # 6. Ensure all phone numbers follow E.164 format
    phone_pattern = re.compile(r"^\+\d{10,15}$")
    if df["Contact Number"].apply(lambda x: bool(phone_pattern.match(str(x)))).all():
        group3.append("All phone numbers follow E.164 format")
    else:
        validation_messages.append("Invalid phone number format. Please ensure all phone numbers follow E.164 format (e.g., +1234567890).")
        return False

    # 7. Ensure all emails have valid structure
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    if df["Contact Email"].apply(lambda x: bool(email_pattern.match(str(x)))).all():
        group3.append("All email addresses have valid format")
    else:
        validation_messages.append("Invalid email format. Please ensure all email addresses are valid.")
        return False

    # Add grouped success messages
    if group1:
        success_messages.append("File loaded and structure validated: " + ", ".join(group1))
    if group2:
        success_messages.append("Data quality checks passed: " + ", ".join(group2))
    if group3:
        success_messages.append("Format checks passed: " + ", ".join(group3))

    validation_messages.extend(success_messages)
    return True
