# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 20:12:48 2021

@author: hakan
"""

import numpy as np
import streamlit as st
from bokeh.plotting import figure
from pandas import read_excel
from numpy import arange
import pandas as pd
import pydeck as pdk
import math
from PIL import Image

st.title("Axial Capacity Calculation for IPE-HE Sections")

"""
This application was developed to find out axial compression capacity of IPE-HE
sections.

To use the app you should choose at the following steps below:
    
    1- Steel section
    2- Design type
    3- Steel material
    4- Length
    5- Case for web & flange parts.
    3- Ductility of structure
        
To find the more information about these parameters please check the "TBEC 2018
Chapter 2, 3 & 4." You can download the "TBEC 2018 in Turkish format at the following
link: https://www.imo.org.tr/resimler/dosya_ekler/89227ad223d3b7a_ek.pdf"
    
After these choices this app will give the design point for fundamental period of the structure.

"""

st.sidebar.header("Section Properties & Design Type")


my_sheet_main = 'Sayfa1' # change it to your sheet name
main_file_name = 'IPE_HEB.xlsx' # change it to the name of your excel file
df_main = read_excel(main_file_name, sheet_name = my_sheet_main, engine='openpyxl')
# print(df_main.head()) # shows headers with top 5 rows
# print(df_main.info())


# Lets choice the section

section_select = st.sidebar.selectbox("Type of Structure: ", df_main["Sections"])
section = df_main.loc[df_main['Sections']==section_select]
case_flange = "Will define"
steel_material = st.sidebar.selectbox("Steel Material: ", {"S235", "S275", "S355"})
if steel_material == "S235":
    fy = 235
    fu = 350
elif steel_material == "S275":
    fy = 275
    fu = 350
else:
    fy = 355
    fu = 510
E = 200000
design_type = st.sidebar.selectbox("Design Type: ", {"LRFD", "ASD"})
Length = st.sidebar.number_input("Section Length (mm): ", value=3000, step=100)

st.header("Characteristic Axial Compression Capacity")

# Local Buckling Control
# Flange

b = section['b'].iloc[0]
tf = section['t2'].iloc[0]

lambda_1 = b/(2*tf)

lambda1_ = "Will Define"

# Web

h = section['h'].iloc[0] - 2*section['t2'].iloc[0]-2*section['R1'].iloc[0]
tw = section['t1'].iloc[0]
lambda_2 = h/tw
lambda_r = "Will Define"

# Local Buckling Control

kx = st.sidebar.number_input("Kx (Unbraced Length Factor (Major): ", value=1.0, step=0.1)
ky = st.sidebar.number_input("Ky (Unbraced Length Factor (Minor): ", value=1.0, step=0.1)


Lx = Length
Lcx = Length * kx
Ly = Length
Lcy = Length * ky
    
ix = section['ix'].iloc[0]*10
iy = section['iy'].iloc[0]*10
lambda_ksi = Lcx/ix
lambda_phi = Lcy/iy
lambda_max = max(lambda_ksi,lambda_phi)
lambda_check = 4.71*math.sqrt(E/fy)

if lambda_max <= lambda_check:
    print("Section is okay")
else:
    print("Section is not suitable")

Fcx = (3.1415926**2*E/((Lcx/ix)*(Lcx/ix)))
Fcy = (3.1415926**2*E/((Lcy/iy)*(Lcy/iy)))
Fcrx = 0.658**(fy/Fcx)*fy
Fcry = 0.658**(fy/Fcy)*fy

Pnx = Fcrx*section['A'].iloc[0]*100*10**-3
Pny = Fcry*section['A'].iloc[0]*100*10**-3

Pg = 20
Pq = 40
st.subheader("Axial Capacity")

Ag = section['A'].iloc[0]*100
Pn = fy*Ag*10**-3

if design_type == "LRFD":
    fi = 0.9
    Pcx = Pnx*fi
    Pcy = Pny*fi
    Pc = Pn*fi
    Pu = 1.2*Pg +1.6*Pq
    Pd = min(Pcx,Pcy)
    Ratio = Pu/Pd
    
else:
    fi = 1.67
    Pcx = Pnx/fi
    Pcy = Pny/fi
    Pc = Pn/fi
    Pu = Pg +Pq
    Pd = min(Pcx,Pcy)
    Ratio = Pu/Pd

if Ratio >= 1:
    st.markdown("DCR is " + str(format(Ratio, ".2f")) + " - Overstress!")
else:
    st.markdown("DCR is " + str(format(Ratio, ".2f"))) 
    
st.markdown("Axial Compression Capacity - X: " + str(format(Pcx, ".2f")) + "kN")
st.markdown("Axial Compression Capacity - Y: " + str(format(Pcy, ".2f")) + "kN")
st.markdown("Axial Tension Capacity: " + str(format(Pc, ".2f")) + "kN")



st.header("Characteristic Bending Moment Capacity")

# Local Buckling Check - Table 5.18
# Web

lambda_r_1 = 0.38*math.sqrt(E/fy)

# Flange

lambda_r_2 = 3.76*math.sqrt(E/fy)

# Lateral Torsional Buckling Limit State (9.2.2)

Lp =1.76*iy*math.sqrt(E/fy)
Iy = section['Iy'].iloc[0]
Wex = section['Wel.x'].iloc[0]
Wpx = section['Wpl.x'].iloc[0]
Wey = section['Wel.y'].iloc[0]
Wpy = section['Wpl.y'].iloc[0]
Cw =section['Iw'].iloc[0]
i_ts_2 = math.sqrt(math.sqrt(Iy*10**4*Cw*10**6)/(Wex*10**3))
J = section['It'].iloc[0]
ho = section['h'].iloc[0] - tf
c = 1 # we will check what is this constant

Lr = 1.95*i_ts_2*E/(0.7*fy)*math.sqrt(J*10**4*1/(Wex*10**3*ho)+math.sqrt((J*10**4*c/(Wex*10**3*ho))**2+6.76*(0.7*fy/E)**2))

co1, co2, co3 = st.columns(3)
with co2:
    img_1 = Image.open("Cb.png")
    img_2 = Image.open("Cb_Dist.png")
    st.image([img_1,img_2], width = 500,caption=["Moment Constants for Different Load Types"]*2 )


st.image(img_1, caption = "Moment Points for Point Load", width = 500)

st.image(img_2, caption = "Moment Points for Distrubited Load", width = 500)

col1, col2, col3 = st.columns(3)
with col1:
    Mmax = st.number_input("Maximum Moment: ", value=360.0, step=1.0)
    Ma = st.number_input("Ma: ", value=180.0, step=1.0)
    
with col3:
    Mb = st.number_input("Mb: ", value=360.0, step=1.0)
    Mc = st.number_input("Mc: ", value=180.0, step=1.0)

Cb = 12.5*Mmax/(2.5*Mmax+3*Ma+4*Mb+3*Mc)
Mp = fy*10**-6*Wpx*10**3

if Lp >= Length:
    Mn = Mp
elif Length > Lp and Lr >= Length:
    if Cb*(Mp-(Mp-0.7*fy*Wex*10**-3)*(((Length-Lp)/1000)/((Lr-Lp)/1000))) <= Mp:
        Mn = Cb*(Mp-(Mp-0.7*fy*Wex*10**-3)*(((Length-Lp)/1000)/((Lr-Lp)/1000)))
    else:
        Mn = Mp
elif Length > Lr:
    if Fcrx*Wex > Mp:
        Mn = Fcrx*Wex
    else:
        Mn = Mp
else:
    Mn = "Hata"
    
if design_type == "LRFD":
    fi = 0.9
    Mdx = Mn*fi
    
else:
    fi = 1.67
    Mdx = Mn/fi
 
Mdy = min(min(Wpx,Wpy)*10**-3*fy,1.6*min(Wex,Wey)*10**-3*fy)
st.markdown("Major Moment Capacity: " + str(format(Mdx, ".2f")) + "kNm")
st.markdown("Minor Moment Capacity: " + str(format(Mdy, ".2f")) + "kNm")