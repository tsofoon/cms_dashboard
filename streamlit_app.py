import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import requests
import streamlit as st
import pydeck as pdk
import gdown

def movecol(df, cols_to_move=[], ref_col='', place='After'):

    cols = df.columns.tolist()
    if place == 'After':
        seg1 = cols[:list(cols).index(ref_col) + 1]
        seg2 = cols_to_move
    if place == 'Before':
        seg1 = cols[:list(cols).index(ref_col)]
        seg2 = cols_to_move + [ref_col]

    seg1 = [i for i in seg1 if i not in seg2]
    seg3 = [i for i in cols if i not in seg1 + seg2]

    return(df[seg1 + seg2 + seg3])

@st.experimental_memo()
def load_data():
    google_dr_dict = dict()
    google_dr_dict['Timely_and_Effective_Care'] = 'https://drive.google.com/file/d/1h82JBQapUD1zi1HVSJe3I2Vw5ofHvlOH/view?usp=sharing'
    google_dr_dict['Complications_and_Deaths'] = 'https://drive.google.com/file/d/1x_ZJlgBsn2d_BbY9bioDofQys7rnDVu3/view?usp=sharing'
    google_dr_dict['HCAHPS'] = 'https://drive.google.com/file/d/1z9bRVkal1S2WqL8c7DOtwLKpM8bF_LtG/view?usp=sharing'
    google_dr_dict['Healthcare_Associated_Infections'] = 'https://drive.google.com/file/d/1TKryKkpVlVCzHqzRfjo0INS37oAmvv_1/view?usp=sharing'
    google_dr_dict['Medicare_Hospital_Spending_Per_Patient'] = 'https://drive.google.com/file/d/1uyvMzW27XOq8qXB1VopKaczZfSOHj57-/view?usp=sharing'
    google_dr_dict['Payment_and_Value_of_Care'] = 'https://drive.google.com/file/d/1ipoCesJhBAWm-tvwQLrcSMtDj1JduqFO/view?usp=sharing'
    google_dr_dict['Unplanned_Hospital_Visits'] = 'https://drive.google.com/file/d/13txPt9NecBfDcPvNriLXRLvCzMu9a0Y3/view?usp=sharing'
    
    data = dict()
    for k in google_dr_dict.keys():
        path = 'https://drive.google.com/uc?export=download&id=' + google_dr_dict[k].split('/')[-2]
        data[k] = pd.read_csv(gdown.download(url= path, quiet=False), index_col= 0)
        
    return data


def main():
    ### sidebar ###
    
    st.sidebar.title('About the app')
    st.sidebar.markdown(
        """
        This CMS data explorer is a [streamlit](https://streamlit.io/) web app to easily navigate and explore [CMS hospital compare data](https://www.medicare.gov/care-compare/).
        The original data set is [here](https://data.cms.gov/provider-data/search?theme=Hospitals). 
        
        **Instructions**\n
        1. Select Dataset and Measure Name to plot \n
        2. Select States for data visualization. If number of states is less than 5, you will have the option to select counties as well.\n
        3. Select Facility. The selected facility will show up as a dot in the histogram. Default selection is some of the [Lifepoint Hospitals](http://www.lifepointhealth.net/locations).\n 
        4. Histogram will show the selected data. If plot selected facility only, only data from the selected facility will be ploted. Otherwise, all facility that
           meets the location criteria will be plotted.\n
        5. A table showing data from the histogram is provided. You can use the sort values in reverse box to sort the score column. You can also click on the column header to sort any column.
        6. A map showing all facility in the table. [Interactive feature not available yet]\n
        
        **Pro Tips**\n
        1. You can enlarge the graphs, tables and maps on streamlit by pressing the icon on the top right corner. \n
        2. The histograms are built using [plotly](https://plotly.com/python/)  and are meant to be interactive. You can zoom, pan, select, hover and more! \n
        
        Created by Matt Tso 2021 DS @ Dascena \n
        [App Repo](https://github.com/tsofoon/cms_dashboard)
        """
    )
    
    
    ### main ###
    life_point_HOSP_df = pd.read_csv('Data/LIFEPOINT_HOSP.csv') 
    life_point_HOSP_df['Facility Name'] = \
        life_point_HOSP_df['Facility Name'].str.upper()

    data = load_data()


    st.markdown("<h1 style='text-align: left; color: rgb(0,117,201);'>\
        CMS Hospital Data Explorer </h1>", unsafe_allow_html=True)
    dataset_name = st.selectbox('Dataset', list(data.keys()), index = 0)
    
    measure_name = 'Measure Name'
    score_col = 'Score'
    
    if 'Payment Measure Name' in data[dataset_name].columns:
        measure_name = 'Payment Measure Name'
        score_col = 'Payment'
    elif 'HCAHPS Question' in data[dataset_name].columns:
        measure_name = 'HCAHPS Question'
        
         
    if dataset_name == 'Timely_and_Effective_Care':
        measure_name_sel = st.selectbox('Measure Name', list(data[dataset_name][measure_name].unique()), \
            index = 12)
    else:
        measure_name_sel = st.selectbox('Measure Name', list(data[dataset_name][measure_name].unique()))
    #st.write('You have selected', measure_name)

    if dataset_name == 'HCAHPS':
        if 'linear mean score' in measure_name_sel:
            score_col = 'HCAHPS Linear Mean Value'
        elif 'star rating' in measure_name_sel:
            score_col = 'Patient Survey Star Rating'
        else:
            score_col = 'HCAHPS Answer Percent'

    df = data[dataset_name]
    df = df[df[measure_name] == measure_name_sel]
    df = df[df[score_col] != 'Not Available']
    try:
        df[score_col] = df[score_col].str.replace('$','')
        df[score_col] = df[score_col].str.replace(',','')
        df[score_col] = df[score_col].replace('Not Available',np.nan)
        df[score_col] = df[score_col].astype(float)
    except ValueError:
        st.warning('non-numerical score')
    
    state = st.multiselect(
        'U.S. State',
        df['State'].unique(),
        df['State'].unique()
        )
    if st.button('All U.S. States'):
        state = df['State'].unique()
    df = df[df['State'].isin(state)]
    if len(state) <= 5:
        cty = st.multiselect(
            'County',
            sorted(df['County Name'].unique()),
            sorted(df['County Name'].unique())
        )
    else:
        cty = df['County Name'].unique()
    df = df[df['County Name'].isin(cty)]
    
    
    life_point_HOSP = life_point_HOSP_df[life_point_HOSP_df['Facility Name'].\
                        isin(df['Facility Name'])]['Facility Name'].to_list()
    if 'MEMORIAL MEDICAL CENTER' in life_point_HOSP:
        life_point_HOSP.remove('MEMORIAL MEDICAL CENTER')
    if 'COMMUNITY MEDICAL CENTER' in life_point_HOSP:
        life_point_HOSP.remove('COMMUNITY MEDICAL CENTER')
    
    sel_HOSPs = st.multiselect(
        'Select Hospitals to Highlight',
        df['Facility Name'].unique(),
        life_point_HOSP
        )
    
    sel_HOSP_IDs = df[df['Facility Name'].isin(sel_HOSPs)]['Facility ID']
    Reverse = st.checkbox("Sort values in reverse?", value = True)
    df = df.sort_values(by = score_col, ascending = not Reverse)
    agree = st.checkbox("Plot selected facility only")
    if agree:
        df = df[df['Facility ID'].isin(sel_HOSP_IDs)]

    fig1 = px.histogram(df, x=score_col, 
        title = measure_name_sel
    )

    
    for sel_HOSP_ID in sel_HOSP_IDs:
        val = df[df['Facility ID'] ==sel_HOSP_ID].iloc[0]
        
        fig1.add_trace(go.Scatter(x=[val[score_col],val[score_col]], y=[0, 0], \
            name = str(val['Facility ID']) + ' ' + val['Facility Name'] + ' ' + val['State']))

    

    st.plotly_chart(fig1)
    
    df = movecol(df, cols_to_move=[measure_name, score_col], ref_col='Facility Name', place='After')
    st.write(df.reset_index(drop = True).astype(str))
   

    df = df.dropna(subset = ['lat', 'lon'])
    df['lat'] = df['lat'].astype('float')
    df['lon'] = df['lon'].astype('float')

    
    st.map(df)
if __name__ == "__main__":
    main()
