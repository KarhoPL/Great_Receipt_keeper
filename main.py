from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd
import csv
import numpy as np

import sys
import codecs

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\kharacz\AppData\Local\Tesseract-OCR\tesseract.exe'
#funkcja zwracająca lisę zakupów z zdjecia paragonu
def products(receipt_image):
    products_list_to_df = []
    im = Image.open(receipt_image) # the second one 
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im.save('unnamed2.jpg')
    lines =  (pytesseract.image_to_string(Image.open('unnamed2.jpg'))).split("\n")
    first_product = 0
    last_product = 0
    for line in lines:
        if line[0:4] == "2020" : first_product = lines.index(line) + 1
        if line[0:5] == "PTU A" : last_product = lines.index(line)
    bought_products = []
    for i in range(first_product,last_product):
        bought_products.append(lines[i])
    for product_line in bought_products:
        if "*" in product_line:
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
                price_per_unit = float(splited_prod[star_index + 1].replace(",","."))
                name = " ".join(splited_prod[:star_index - 1])
            final_charge = amount * price_per_unit
            products_list_to_df.append([name, price_per_unit, amount,final_charge])
    df = pd.DataFrame(np.array(products_list_to_df), columns = ["Product Name", "Price", "Amount", "Final Charge"])
    return df


produkty = products("unnamed.jpg")
print(produkty)

#funkcja zwracająca df z listą produktów, ilościa i ceną

def df_products(products):
    products_list_to_df = []
    for product_line in products:
        if "*" in product_line:
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
                price_per_unit = float(splited_prod[star_index + 1].replace(",","."))
                name = " ".join(splited_prod[:star_index - 1])
            final_charge = amount * price_per_unit
            products_list_to_df.append([name, price_per_unit, amount,final_charge])
    df = pd.DataFrame(np.array(products_list_to_df), columns = ["Product Name", "Price", "Amount", "Final Charge"])
    return df    
#print(df_products(produkty))
    
