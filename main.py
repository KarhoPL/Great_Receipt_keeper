from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import csv
import numpy as np
import sys
import codecs
import datetime as dt
from math import floor

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kharacz\AppData\Local\Tesseract-OCR\tesseract.exe'
#funkcja zwracająca listę zakupów z zdjecia paragonu
def Creating_DF_from_image(receipt_image):
    products_list_to_df = []
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
        if line[0:4] == "2020" : first_product = lines.index(line) + 1
        if line[0:5] == "PTU A" : last_product = lines.index(line)
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
            input_to_float = lambda imputing_value, old_value : float(imputing_value.replace(",",".")) if imputing_value else old_value
            if final_charge != final_charge_counted:
                print(f'{name} | {price_per_unit} | {amount} | {final_charge} | {final_charge_counted}')
                print(f"Error in recognition of product, please write correct values for {name}")
                amount = input_to_float(input("Amount: "), amount)
                price_per_unit = input_to_float(input("Price per unit of:"), price_per_unit)
                final_charge = input_to_float(input("Final charge of:"), final_charge)
            products_list_to_df.append([name, price_per_unit, amount, final_charge])
    df = pd.DataFrame(np.array(products_list_to_df), columns = ["Product Name", "Price", "Amount", "Final Charge"])
    return df

print(Creating_DF_from_image('unnamed3.jpg'))