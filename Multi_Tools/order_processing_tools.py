import pandas as pd
import os
import random
import numpy as np
from datetime import datetime, timedelta

from langchain_core.tools import tool

df_2 = pd.read_csv(r"GroceryDataset.csv")

import requests
from math import radians, sin, cos, sqrt, atan2

# Replace with your OpenCage API key
OPENCAGE_API_KEY = "df7db606d9c94d19aa13971041ac96e7"

def get_coordinates(pincode):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={OPENCAGE_API_KEY}"
    response = requests.get(url).json()
    
    if response["results"]:
        lat = response["results"][0]["geometry"]["lat"]
        lon = response["results"][0]["geometry"]["lng"]
        return lat, lon
    else:
        raise ValueError("Invalid Pincode or API limit exceeded")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

@tool
def calculate_distance(pincode1, pincode2):
    """
    Calculate distance between Seller Pincode and Customer pincode.

    Parameters:
    - pincode_1 (int) : Pincode of loacation 1
    - pincode_2 (int) : Pincode of loacation 2

    returns:
    - float: Geographical distance between 2 pincodes
    """
    lat1, lon1 = get_coordinates(pincode1)
    lat2, lon2 = get_coordinates(pincode2)
    # print(f"{lat1 = } {lon1 = } | {lat2 = } {lon2 = }")
    # print()
    
    return haversine(lat1, lon1, lat2, lon2)

@tool 
def calculate_delivery_charge(distance_km: float, delivery_speed: str) -> float:
    """
    Calculates the delivery charge based on distance and user's delivery speed preference.

    Parameters:
    - distance_km (float): The distance in kilometers for delivery.
    - delivery_speed (str): The user's preferred delivery speed. 
      Options: ["standard", "express", "same_day", "instant"].

    Returns:
    - float: The total delivery charge in INR.

    Delivery Speed & Charges:
    - Standard (4-7 days): ₹5 per km, Minimum charge ₹50
    - Express (2-3 days): ₹10 per km, Minimum charge ₹100
    - Same-Day (Within 24 hrs): ₹20 per km, Minimum charge ₹150
    - Instant (Few hours): ₹40 per km, Minimum charge ₹250
    """
    
    # Define pricing per km and minimum base charges
    delivery_rates = {
        "standard": {"per_km": 5, "min_charge": 50},
        "express": {"per_km": 10, "min_charge": 100},
        "same_day": {"per_km": 20, "min_charge": 150},
        "instant": {"per_km": 40, "min_charge": 250},
    }
    
    # Convert delivery speed to lowercase to avoid case sensitivity issues
    delivery_speed = delivery_speed.lower()
    
    if delivery_speed not in delivery_rates:
        raise ValueError("Invalid delivery speed. Choose from: 'standard', 'express', 'same_day', 'instant'.")

    rate_info = delivery_rates[delivery_speed]
    
    # Calculate charge based on distance and apply minimum charge if needed
    total_charge = max(rate_info["per_km"] * distance_km, rate_info["min_charge"])
    
    return total_charge
    
@tool
def calculate_delivery_time(delivery_speed: str) -> datetime:
    """
    Calculates the estimated delivery date and time.

    Parameters:
    - delivery_speed (str): The user's preferred delivery speed. 
      Options: ["standard", "express", "same_day", "instant"].

    Returns:
    - datetime: The estimated delivery date and time.

    Delivery Speed Estimates:
    - Standard (4-7 days)
    - Express (2-3 days)
    - Same-Day (1 day)
    - Instant (within hours)
    """

    order_time = datetime.now()

    # Define estimated delivery durations
    delivery_estimates = {
        "standard": (4, 7),  # Min & Max days
        "express": (2, 3),
        "same_day": (1, 1),
        "instant": (0, 0),  # Within a few hours
    }
    
    # Normalize input
    delivery_speed = delivery_speed.lower()
    
    if delivery_speed not in delivery_estimates:
        raise ValueError("Invalid delivery speed. Choose from: 'standard', 'express', 'same_day', 'instant'.")

    min_days, max_days = delivery_estimates[delivery_speed]

    if delivery_speed == "instant":
        estimated_delivery = order_time + timedelta(hours=3)  # Assume delivery in ~3 hours
    else:
        estimated_delivery = order_time + timedelta(days=max_days)  # Use max duration for safer estimate

    return estimated_delivery

@tool
def calculate_total_price(check_prod_id_list:list, prod_quantity_list: list, total_delivery_charges: float) -> float:
    """
    Calculate the total price of products based on their IDs and quantities.

    Parameters:
    check_prod_id_list (list of integers): List of product IDs to filter products.
    prod_quantity_list (list of integers): List of quantities corresponding to each product ID.
    total_delivery_charges (float) : Total delivery charges for all products

    Returns:
    float: Total price of the specified products.
    
    The function retrieves the prices of products based on the provided list of product IDs, multiplies each price by its corresponding quantity, and returns the total price.
    """
    index_list_2 = list()
    for prd in check_prod_id_list:
        prd_price = df_2.loc[df_2['ProductID'] == int(prd)]["Price"].tolist()[0]
        index_list_2.append(prd_price)
    
    total_price = np.sum((np.array(index_list_2) * np.array(prod_quantity_list))) 
    return total_price + total_delivery_charges




@tool
def generate_order_id():
    """Generates unique order id for placing the order 
    
    returns:
    - str : Order ID for placing the order."""
    import uuid
    return str(uuid.uuid1())

















@ tool 
def save_delivery_data(
    order_id: str, user_id: int, product_id: list[int], quantity: list[int], product_name: list[str], 
    order_date: str, delivery_speed: str, distance_km: float, 
    delivery_charge: float, estimated_delivery_date: str, 
    seller_pincode: int, buyer_pincode: int, delivery_status: str, 
    total_order_value: float, remarks: str, filename="delivery_details.csv"
) -> str:
    """
    Saves delivery details into a CSV file using Pandas.
    
    Parameters:
    - order_id (str): Unique order ID.
    - user_id (int): User ID who placed the order.
    - product_id (list[int]): list of ID of the purchased product.
    - quantity (list[int]) : list of quantity of the item
    - product_name (list[str]): list of Name of the product.
    - order_date (str): Order placement date and time (YYYY-MM-DD HH:MM).
    - delivery_speed (str): Delivery preference (standard, express, etc.).
    - distance_km (float): Distance in kilometers.
    - delivery_charge (float): Calculated delivery charge.
    - estimated_delivery_date (str): Expected delivery date (YYYY-MM-DD HH:MM).
    - seller_pincode (str): Seller’s pincode.
    - buyer_pincode (int): Buyer’s pincode.
    - delivery_status (int): Current delivery status.
    - total_order_value (float): Total order cost.
    - remarks (str): Additional instructions.
    - filename (str): CSV file to save data.

    Returns:
    - str: Success message.
    """

    for i in range(len(quantity)):
        # Create a DataFrame for the new record
        new_data = pd.DataFrame([{
            "order_id": order_id, "user_id": user_id, "product_id": product_id[i], 
            "quantity": quantity[i],
            "product_name": product_name[i], "order_date": order_date, 
            "delivery_speed": delivery_speed, "distance_km": distance_km, 
            "delivery_charge": delivery_charge, "estimated_delivery_date": estimated_delivery_date, 
            "seller_pincode": seller_pincode, "buyer_pincode": buyer_pincode, 
            "delivery_status": delivery_status, "total_order_value": total_order_value, 
            "remarks": remarks
        }])

        # Check if the CSV file exists
        if os.path.exists(filename):
            existing_data = pd.read_csv(filename)
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            updated_data = new_data

        # Save to CSV
        updated_data.to_csv(filename, index=False)

    return f"Order ID {order_id} saved successfully in {filename}!"



tools = [calculate_distance, calculate_delivery_charge, calculate_delivery_time , 
         calculate_total_price, generate_order_id, save_delivery_data]

