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


mode = st.sidebar.selectbox("Mode: ", {"Demo", "Full"})

if mode == "Demo":
    
    st.title("Capacity & DCR Calculation for IPE-HEA-B Sections")

    """
    This application was developed to find out capacity and DCR of IPE-HE
    sections.
    
    To use the app you should choose at the following items below:
        
        1- Results type
        2- Section
        3- Steel material
        4- Design type
        5- Length
        6- Unbraced length factors
        
    Also if you want to calculate DCR of section, you can use design forces 
    end of the page. Be sure the choice correct "Result" input. 
                
    To find the more information about these parameters please check the "ANS/AISC 360-16
    Specifacation for Structural Steel Buildings". Also you can download the AISC at the following
    link: https://www.aisc.org/globalassets/aisc/publications/standards/a360-16w-rev-june-2019.pdf
            
    """
    
    st.sidebar.header("Section Properties & Design Type")
    
    
    my_sheet_main = 'Sayfa1' # change it to your sheet name
    main_file_name = 'IPE_HEB.xlsx' # change it to the name of your excel file
    # df_main = read_excel(main_file_name, sheet_name = my_sheet_main, engine='openpyxl')
    df_main = read_excel(main_file_name, sheet_name = my_sheet_main)
    # print(df_main.head()) # shows headers with top 5 rows
    # print(df_main.info())


# Lets choice the section

    result_type = st.sidebar.selectbox("Result: ", {"Only Capacities", "Capacities and DCR"})
    section_select = st.sidebar.selectbox("Section: ", df_main["Sections"])

    section = df_main.loc[df_main['Sections']==section_select]
    case_flange = "Will define"
    steel_material = st.sidebar.selectbox("Steel Material: ", {"S235", "S275", "S355"})
    if steel_material == "S235":
        fy = 235.0
        fu = 350.0
    elif steel_material == "S275":
        fy = 275.0
        fu = 350.0
    elif steel_material == "S355":
        fy = 355.0
        fu = 510.0

    E = 210000
    design_type = st.sidebar.selectbox("Design Type: ", {"LRFD", "ASD"})
    Lb = st.sidebar.number_input("Section Length (mm): ", value=3000, step=100)
    
    
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
    
    
    Lx = Lb
    Lcx = Lb * kx
    Ly = Lb
    Lcy = Lb * ky
        
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
    if Lcx/ix <= 4.71*math.sqrt(E/fy):
        Fcrx = 0.658**(fy/Fcx)*fy
    else:
        Fcrx = 0.877*Fcx
    if Lcy/iy <= 4.71*math.sqrt(E/fy):
        Fcry = 0.658**(fy/Fcy)*fy
    else:
        Fcry = 0.877*Fcy
    
    Pnx = Fcrx*section['A'].iloc[0]*100*10**-3
    Pny = Fcry*section['A'].iloc[0]*100*10**-3
        
    
    st.markdown(section_select + " Pc & Pt capacities are calculated according to " + design_type + ":")
    
    Ag = section['A'].iloc[0]*100
    Pn = fy*Ag*10**-3
    print(Pn)
    
    if design_type == "LRFD":
        fi = 0.9
        Pcx = Pnx*fi
        Pcy = Pny*fi
        Pc = Pn*fi
        Pd = min(Pcx,Pcy)
        print("PD:" + str(Pd))
        
    else:
        fi = 1.67
        Pcx = Pnx/fi
        Pcy = Pny/fi
        Pc = Pn/fi
        Pd = min(Pcx,Pcy)
    
    # if Ratio >= 1:
    #     st.markdown("DCR is " + str(format(Ratio, ".2f")) + " - Overstress!")
    # else:
    #     st.markdown("DCR is " + str(format(Ratio, ".2f"))) 

    st.markdown("Pc: " + str(format(Pd, ".2f")) + "kN")
    st.markdown("Pt: " + str(format(Pc, ".2f")) + "kN")
    
    st.subheader("Bending Capacity")
    
    """
    Before to calculate the major and minor moment capacity of section please
    select your loading type for Cb.
    
    """
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
    
    # co1, co2, co3 = st.columns(3)
    # with co2:
    #     img_1 = Image.open("Cb.png")
    #     img_2 = Image.open("Cb_Dist.png")
    #     st.image([img_1,img_2], width = 500,caption=["Moment Constants for Different Load Types"]*2 )
    
    
    img_1 = Image.open("Cb_Case.png")
    col1, col2, col3 = st.columns([1,1,1])
    col1.image(img_1, width = 500, caption = "Values of Cb for Simpyle Supported Beams")
    
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     Mmax = st.number_input("Maximum Moment: ", value=360.0, step=1.0)
    #     Ma = st.number_input("Ma: ", value=180.0, step=1.0)
        
    # with col3:
    #     Mb = st.number_input("Mb: ", value=360.0, step=1.0)
    #     Mc = st.number_input("Mc: ", value=180.0, step=1.0)
    buff, col, buff2 = st.columns([1,3,1])
    
    with col:
        Cb_Case = st.selectbox("Case: ", {1,2,3,4,5,6,7,8,9,10,11})
    
    if Cb_Case ==1:
        Cb =1.32
    elif Cb_Case ==2:
        Cb =1.67
    elif Cb_Case == 3:
        Cb = 1.14
    elif Cb_Case == 4:
        Cb = 1.00
    elif Cb_Case == 5:
        Cb = 1.14
    elif Cb_Case == 6:
        Cb = 1.11
    elif Cb_Case ==7:
        Cb = 1.14
    elif Cb_Case == 8:
        Cb = 1.30
    elif Cb_Case == 9:
        Cb = 1.01
    elif Cb_Case == 10:
        Cb = 1.06
    else:
        Cb = 1.00
        
    # Cb = 12.5*Mmax/(2.5*Mmax+3*Ma+4*Mb+3*Mc)
    Mp = fy*10**-6*Wpx*10**3
    
    if Lp >= Lb:
        Mn = Mp
    elif Lb > Lp and Lr >= Lb:
        if Cb*(Mp-(Mp-0.7*fy*Wex*10**-3)*(((Lb-Lp)/1000)/((Lr-Lp)/1000))) <= Mp:
            Mn = Cb*(Mp-(Mp-0.7*fy*Wex*10**-3)*(((Lb-Lp)/1000)/((Lr-Lp)/1000)))
        else:
            Mn = Mp
    elif Lb > Lr:
        Fcr = (Cb*3.14**2*E/(Lb/i_ts_2)**2)*math.sqrt(1+(0.078*J*10**4/(Wex*10**3*ho))*(Lb/i_ts_2)**2)
        if Fcr*Wex*10**-3 <= Mp:
            Mn = Fcr*Wex*10**-3
        else:
            Mn = Mp
    else:
        Mn = "Hata"
        
    if design_type == "LRFD":
        fi = 0.9
        Mdx = Mn*fi
        Mdy = min(min(Wpx,Wpy)*10**-3*fy,1.6*min(Wex,Wey)*10**-3*fy)*fi
        
    else:
        fi = 1.67
        Mdx = Mn/fi
        Mdy = min(min(Wpx,Wpy)*10**-3*fy,1.6*min(Wex,Wey)*10**-3*fy)*fi
     
    st.markdown(section_select + " moment capacities for major and minor are calculated according to " + design_type + ":")
    print(Mdx)
    
    st.markdown("Major Moment Capacity: " + str(format(Mdx, ".2f")) + "kNm")
    
    st.markdown("Minor Moment Capacity: " + str(format(Mdy, ".2f")) + "kNm")
    
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    if result_type == "Capacities and DCR":
        input_for_design = st.selectbox("Design Forces: ", {"Compression", "Tension", "Axial Compression - Bending", "Axial Tension - Bending"})
        if input_for_design == "Compression":
          axial_force = st.number_input("Design Axial Compression Force: ")  
          st.markdown("DCR for Axial Force " + str(axial_force/min(Pcx,Pcy)))
        elif input_for_design == "Tension":
          axial_force = st.number_input("Design Axial Tension Force: ")  
          dcr = axial_force/min(Pcx,Pcy)
          st.markdown("DCR for Axial Force " + str(format(dcr, ".2f")))
        elif input_for_design == "Axial Compression - Bending":
           axial_force = st.number_input("Design Axial Compression Force: ")
           major_bending = st.number_input("Design Major Bending Moment: ")
           minor_bending = st.number_input("Design Minor Bending Moment: ")
           axial_ratio = axial_force/min(Pcx,Pcy)
           if axial_ratio < 0.2:
               dcr = (axial_force/(2*min(Pcx,Pcy)))+(major_bending/Mdx + minor_bending/Mdy)
               st.markdown("DCR for Combined Forces: " + str(format(dcr, ".2f")))
           else:
               dcr = (axial_force/(min(Pcx,Pcy)))+(8/9)*(major_bending/Mdx + minor_bending/Mdy)
               st.markdown("DCR for Combined Forces: " + str(format(dcr, ".2f")))     
        elif input_for_design == "Axial Tension - Bending":
           axial_force = st.number_input("Design Axial Tension Force: ")
           major_bending = st.number_input("Design Major Bending Moment: ")
           minor_bending = st.number_input("Design Minor Bending Moment: ")
           axial_ratio = axial_force/Pn
           if axial_ratio < 0.2:
               dcr = (axial_force/(2*Pn))+(major_bending/Mdx + minor_bending/Mdy)
               st.markdown("DCR for Combined Forces: " + str(format(dcr, ".2f")))
           else:
               dcr = (axial_force/(Pn))+(8/9)*(major_bending/Mdx + minor_bending/Mdy)
               st.markdown("DCR for Combined Forces: " + str(format(dcr, ".2f")))  
else:
    
    st.title("Capacity & DCR Calculation for Steel Sections")
    """
    e-mail: hakan.keskiin@outlook.com
    
    Linkedin: https://www.linkedin.com/in/hakan-keskin-b9669b61/
    
    """



