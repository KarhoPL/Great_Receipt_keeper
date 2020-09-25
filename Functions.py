from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import csv
import json
import numpy as np
import sys
import codecs
import datetime as dt
from math import floor, fabs
import datetime as dt

#function helping with entering product data
def input_to_float(imputing_value, old_value):
    return float(imputing_value.replace(",",".")) if imputing_value else float(old_value)

def input_old_if_not_new(imputing_value, old_value):
    return imputing_value if imputing_value else old_value


pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kharacz\AppData\Local\Tesseract-OCR\tesseract.exe'
#Function updating storage file
def Creating_Dicts_from_image(receipt_image,json_storage_file):
    products_list_to_df = {}
    products_names = []
    im = Image.open(receipt_image) # the second one 
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    im.save('unnamed2.jpg')
    lines =  (pytesseract.image_to_string(Image.open('unnamed2.jpg'),config = '-c tessedit_char_whitelist="01234567890ABCDEFGHIJKLMNOPRSTUVWXYZabcdefghijklmnopqrstuvwxyz-*,. " --psm 6' )).split("\n")
    first_product = 0
    last_product = 0
    for line in lines:
        if line[0:4] == "2020" or line[0:4] == '2820' or line[0:4] == '2028' or line[0:4] == '2828': first_product = lines.index(line) + 1
        if line[0:5] == "PTU A" : last_product = lines.index(line)
        #print(line)
    bought_products = []
    for i in range(first_product,last_product):
        bought_products.append(lines[i])
    for product_line in bought_products:
        if "*" in product_line and "rabat" not in product_line and "RABAT" not in product_line:
            splited_prod = product_line.split(" ") 
            for word in splited_prod:
                if "*" in word: star_index = splited_prod.index(word)
            # handling errors when the star didn't get separeted from price or quantity
            if len(splited_prod[star_index])>1:
                #when star and price got together:
                if splited_prod[star_index][0] == "*":
                    price_per_unit = float(splited_prod[star_index][1:].replace(",","."))     
                    amount = float(splited_prod[:-1].replace(",","."))
                    name = " ".join(splited_prod[:star_index - 1])
                #when star and quantity got together:
                elif splited_prod[star_index][-1] == "*":
                    price_per_unit = float(splited_prod[star_index+1].replace(",","."))
                    amount = float(splited_prod[star_index][:-1].replace(",","."))
                    name = " ".join(splited_prod[:star_index])
            else: 
                amount = float(splited_prod[star_index - 1].replace(",","."))
                if amount > 6 and len(str(amount)) > 3 :
                    amount = (round((amount - 6)*1000))/1000
                price_per_unit = float(splited_prod[star_index + 1].replace(",","."))
                name = " ".join(splited_prod[:star_index - 1])
            # handling if one of valueas was wrongly recognized 
            final_charge_counted = (round((amount * price_per_unit)*100))/100 if (amount * price_per_unit)%0.01>=0.0065 else (floor((amount * price_per_unit)*100))/100
            final_charge = float(splited_prod[-2].replace(",","."))
            if final_charge != final_charge_counted:
                if fabs(((price_per_unit-(price_per_unit%0.1))*amount) - final_charge)<0.01:
                    price_per_unit = (int((price_per_unit-(price_per_unit%0.1))*100))/100
                else:
                    print(f'{name} | {price_per_unit} | {amount} | {final_charge} | {final_charge_counted}')
                    print(f"Error in recognition of product, please write correct values for {name}")
                    amount = input_to_float(input("Amount: "), amount)
                    price_per_unit = input_to_float(input("Price per unit of:"), price_per_unit)
            if name not in products_names:
              products_list_to_df[name] ={"Price": price_per_unit, "Amount" : amount}
              products_names.append(name)
            else:
              products_list_to_df[name]['Amount'] += amount
    df = json.dumps(products_list_to_df, indent = 4)
    products_dict = json.loads(df)
    with open(json_storage_file, 'r') as json_file:
        storage_dict = json.load(json_file)
    for prdct_name in products_dict:
        if prdct_name in storage_dict:
            storage_dict[prdct_name]['Price'] =(storage_dict[prdct_name]['Price']*storage_dict[prdct_name]['Amount']+products_dict[prdct_name]['Amount']*products_dict[prdct_name]['Price'])/(storage_dict[prdct_name]['Amount']+products_dict[prdct_name]['Amount'])
            storage_dict[prdct_name]['Amount'] += products_dict[prdct_name]['Amount']
            print("Zmieniono ilość  ", prdct_name)
        else :
            storage_dict[prdct_name] = {
                "Price": products_dict[prdct_name]['Price'],
                "Amount": products_dict[prdct_name]['Amount']
                }
            print('Dodano produkt ', prdct_name)
    with open(storage_file, 'w') as json_file:
        json.dump(storage_dict,json_file , indent=4)
    return df

#Function to manually add products
def To_Storage_manually(storage_file):
    with open(storage_file, 'r') as json_file:
        storage_dict = json.load(json_file)
    prod_names = [name for name in storage_dict]
    print(prod_names)
    contin = 'y'
    while contin == 'y' or contin == 'Y':
        name = input("Product name:  ")
        amount = float(input("Product amount:  "))
        if name.lower() in map(lambda x: x.lower(), prod_names):
            price = input_to_float(input(f"Product price per unit (defoult: %.2f ): " %(storage_dict[name]['Price'])),(storage_dict[name]['Price']))
            storage_dict[name] = {
                "Price": (storage_dict[name]['Price']* float(storage_dict[name]['Amount'])+amount*price)/(storage_dict[name]['Amount']+amount),
                "Amount": storage_dict[name]['Amount'] + amount
                }
        else:
            price = input_to_float(input("Product price per unit: "),0)
            storage_dict[name] = {
                "Price": price,
                "Amount": amount
                }
        contin = input_old_if_not_new(input('Add next product? '), contin)
    with open(storage_file, 'w') as json_file:
        json.dump(storage_dict,json_file , indent=4)
    print('Adding completed.')

#Funcion to remove produkts from storage and add to list in consumed file
def Consumed(storage_file, consumed_file, date = dt.date.today().strftime("%d.%m.%Y")):
    with open(storage_file, 'r') as json_file:
        storage_dict = json.load(json_file)
    with open(consumed_file, 'r') as consumed_fl:
        consumed_dict = json.load(consumed_fl)
    prod_names = [name for name in storage_dict]
    print(prod_names)
    contin = 'y'
    while contin == 'y' or contin == 'Y':
        name = input("Product name:  ")
        if name.lower() in map(lambda x: x.lower(), prod_names):
            print("%f of %s left in storage." %(storage_dict[name]["Amount"], name))
            amount = input_to_float(input("Product amount:  "), 1)
            storage_dict[name]["Amount"] = storage_dict[name]["Amount"] - amount
            price = storage_dict[name]["Price"]
        else:
            price = input_to_float(input("There isn't %s in your storage.\n Please enter it's price: "), 0)
            amount = float(input("Product amount:  "))
        name_dict = 1
        consumed_dict[date].update({name : {
            "Amount" : amount,
            "Price" : price,
            "Portion price" : amount*price    
        }})
        contin = input_old_if_not_new(input('Add next product? '), contin)
    with open(consumed_file, 'w') as json_file:
        json.dump(consumed_dict,json_file , indent=4)
    print('Adding completed.')
    


