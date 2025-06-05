import pandas as pd
import numpy as np
import os

from langchain_core.tools import tool

os.environ["TAVILY_API_KEY"] = "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"

df_2 = pd.read_csv(r"GroceryDataset.csv")

from langchain_community.tools.tavily_search import TavilySearchResults


@tool
def get_order_details(order_id):
    
    """
    Retrieve order details from a CSV file based on the provided order ID.

    Parameters:
    order_id (str): The order ID to search for.
   
    Returns:
    str: A JSON-formatted string containing all rows with the specified order ID."""

    filename="delivery_details.csv"
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Filter rows with the given order_id
    filtered_df = df[df['order_id'] == order_id]
    
    # Convert the filtered rows to JSON format
    result_json = filtered_df.to_json(orient='records')
    
    return result_json


@tool
def modify_order_quantities(order_id: str, product_ids: list, quantities: list):
    """
    Modifies the quantity of specific products in an existing order in 'delivery_details.csv',
    and updates the total_order_value using MRPs from 'product_info.csv'.

    Parameters:
    - order_id (str): ID of the order to modify
    - product_ids (list): List of product IDs to update
    - quantities (list): List of corresponding new quantities

    Returns:
    - str: Success or error message
    """

    if len(product_ids) != len(quantities):
        return "Error: The number of product IDs must match the number of quantities."

    delivery_file = "delivery_details.csv"
    product_info_file = r"D:\Lessons\AWS_Learn\File_Resp_ChatBot\CSVs\GroceryDataset.csv"

    if not os.path.exists(delivery_file):
        return f"Error: '{delivery_file}' not found."
    if not os.path.exists(product_info_file):
        return f"Error: '{product_info_file}' not found."

    # Load CSVs
    delivery_df = pd.read_csv(delivery_file)
    product_df = pd.read_csv(product_info_file)

    # Filter rows matching order_id
    order_rows = delivery_df[delivery_df["order_id"] == order_id]
    if order_rows.empty:
        return f"Error: No rows found for order_id '{order_id}'."

    # Assume delivery_charge is the same across all rows of the order
    try:
        delivery_charge = order_rows["delivery_charge"].iloc[0]
    except:
        return "Error: Could not extract delivery charge."

    # Start computing total value
    total_product_value = 0

    for pid, qty in zip(product_ids, quantities):
        # Find matching row in delivery_details
        row_idx = delivery_df[
            (delivery_df["order_id"] == order_id) & 
            (delivery_df["product_id"] == pid)
        ].index

        if row_idx.empty:
            return f"Error: Product ID {pid} not found in order ID {order_id}."

        # Find MRP from product_info
        product_row = product_df[product_df["product_id"] == pid]
        if product_row.empty:
            return f"Error: Product ID {pid} not found in product_info.csv."

        mrp = product_row["MRP"].iloc[0]

        # Update quantity
        delivery_df.at[row_idx[0], "quantity"] = qty

        # Accumulate total cost
        total_product_value += mrp * qty

    total_order_value = total_product_value + delivery_charge

    # Update total_order_value in all rows of the order
    delivery_df.loc[delivery_df["order_id"] == order_id, "total_order_value"] = total_order_value

    # Save changes
    delivery_df.to_csv(delivery_file, index=False)

    return f"Order ID {order_id} has been successfully updated with new quantities and total order value."

@tool
def cancel_order(order_id: str):
    """
    Cancels an order by setting the delivery_status to "Canceled" in delivery_details.csv.

    Parameters:
    - order_id (str): The ID of the order to cancel.

    Returns:
    - str: Success or error message.
    """

    delivery_file = "delivery_details.csv"

    if not os.path.exists(delivery_file):
        return f"Error: '{delivery_file}' not found."

    df = pd.read_csv(delivery_file)

    # Check if order_id exists
    if order_id not in df["order_id"].values:
        return f"Error: Order ID '{order_id}' not found in the file."

    # Update delivery_status to "Canceled"
    df.loc[df["order_id"] == order_id, "delivery_status"] = "Canceled"

    # Save back to file
    df.to_csv(delivery_file, index=False)

    return f"Order ID '{order_id}' has been successfully canceled."

tavily_tool = TavilySearchResults(max_results= 5)

tools = [get_order_details, modify_order_quantities, cancel_order, tavily_tool]