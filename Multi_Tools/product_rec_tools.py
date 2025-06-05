import pandas as pd
import random
import numpy as np

from langchain_core.tools import tool

df_2 = pd.read_csv(r"GroceryDataset.csv")


# check_sub_cat_list = ['Snacks', 'Coffee',"Organic","Poultry"]
# check_prod_id_list = [33,44,55,11]

@tool 
def explore_options(check_sub_cat_list:list) -> str:
    """
    Show random products from the provided list of sub-categories.

    Parameters:
    check_sub_cat_list (list): List of sub-categories to filter products.
    The fixed sub-categories are: 
        'Bakery & Desserts', 'Beverages & Water', 'Breakfast', 'Candy',
       'Cleaning Supplies', 'Coffee', 'Deli', 'Floral', 'Gift Baskets',
       'Household', 'Kirkland Signature Grocery',
       'Laundry Detergent & Supplies', 'Meat & Seafood', 'Organic',
       'Pantry & Dry Goods', 'Paper & Plastic Products', 'Poultry',
       'Seafood', 'Snacks'

    Returns:
    str : DataFrame containing information of randomly selected products from the specified sub-categories.
    
    The function selects 5 random products from each sub-category in the provided list and returns their details.
    """
    index_list_1 = list()

    for cat in check_sub_cat_list:
        cat_index = df_2[df_2['Sub Category'] == cat].index
        cat_index = random.sample(cat_index.tolist(), k= 5)
        index_list_1.extend(cat_index)
    json_str = df_2.loc[index_list_1].to_json(orient='records')
    # print(type(json_str))
    # print()

    return json_str


@tool 
def explore_options_with_price(check_sub_cat_list: list, price_lower_limit:float = False, price_upper_limit:float = False, asked_max: bool = False, asked_min: bool = False) -> str:
    """
    Explore product options within specified price ranges or find top/bottom priced products in given sub-categories.
    
    Parameters:
    check_sub_cat_list (list): List of sub-categories to filter products.
    price_lower_limit (float, optional): Lower limit of the price range. Defaults to False.
    price_upper_limit (float, optional): Upper limit of the price range. Defaults to False.
    asked_max (bool, optional): If True, returns top 3 most expensive products in each sub-category. Defaults to False.
    asked_min (bool, optional): If True, returns top 3 least expensive products in each sub-category. Defaults to False.

    Returns:
    str : DataFrame containing products that match the specified criteria.
    
    The function filters products based on the provided sub-categories and price limits. 
    It can also return the top 3 most or least expensive products in each sub-category if specified.
    """

    index_list_1 = list()

    if (price_lower_limit & price_upper_limit):    
        for cat in check_sub_cat_list:
            cat_index = df_2[(df_2['Sub Category'] == cat) & (df_2["Price"]<= price_upper_limit) & (df_2["Price"] >= price_lower_limit)].index
            index_list_1.extend(cat_index)
        return df_2.loc[index_list_1]
        
    elif price_upper_limit:
        for cat in check_sub_cat_list:
            cat_index = df_2[(df_2['Sub Category'] == cat) & (df_2["Price"]<= price_upper_limit)].index
            index_list_1.extend(cat_index)
        return df_2.loc[index_list_1]
    
    elif price_lower_limit:
        for cat in check_sub_cat_list:
            cat_index = df_2[(df_2['Sub Category'] == cat) & (df_2["Price"]<= price_upper_limit)].index
            index_list_1.extend(cat_index)
        return df_2.loc[index_list_1]    
    
    if asked_max:
        for cat in check_sub_cat_list:
            cat_index = df_2[(df_2['Sub Category'] == cat)].sort_values(by= ['Price'],ascending = False).index[:3]
            index_list_1.extend(cat_index)
        return df_2.loc[index_list_1]    
    
    if asked_min:
        for cat in check_sub_cat_list:
            cat_index = df_2[(df_2['Sub Category'] == cat)].sort_values(by= ['Price'],ascending = True).index[:3]
            index_list_1.extend(cat_index)
        return df_2.loc[index_list_1].to_json(orient='records')
    
@tool
def retrieve_with_prd_id(check_prod_id_list:list) -> pd.DataFrame:
    """
    Retrieve product information based on a list of product IDs.

    Parameters:
    check_prod_id_list (list of integers): List of product IDs to filter products.

    Returns:
    str : DataFrame containing information of products that match the specified product IDs.
    
    The function filters products based on the provided list of product IDs and returns their details.
    """
    index_list_2 = list()
    for prd in check_prod_id_list:
        prd_index = df_2[df_2['ProductID'] == prd].index
        index_list_2.extend(prd_index)
    return df_2.loc[index_list_2].to_json(orient='records')

@tool
def retrieve_with_pincode(nearest_seller_pincode: int) -> pd.DataFrame:
    """
    Retrieve product information based on a pincode of the nearest seller to user

    Parameters:
    nearest_seller_pincode (int): Pincode of the seller

    Returns:
    str : DataFrame containing information of products that match the specified product IDs.
    
    The function filters products based on the provided list of product IDs and returns their details.
    """

    prd_idx_list = df_2[df_2['Seller Pincode'] == nearest_seller_pincode].index
        
    return df_2.loc[prd_idx_list].to_json(orient='records')


tools = [explore_options, explore_options_with_price, retrieve_with_prd_id, retrieve_with_pincode]


