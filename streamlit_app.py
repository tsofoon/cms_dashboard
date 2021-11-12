import os
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import streamlit as st
import pydeck as pdk

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



def main():
    ### sidebar ###
    
    st.sidebar.title('About the app')
    st.sidebar.markdown(
        """
        This CMS data explorer is a [streamlit](https://streamlit.io/) web app to easily navigate and explore [CMS hospital compare data](https://www.medicare.gov/care-compare/).
        The original data set is [here](https://data.cms.gov/provider-data/search?theme=Hospitals). More dataset will be added in the future.
        
        **Instructions**
        1. Select Dataset and Measure Name to plot
        2. Select States for data visualization. If number of states is less than 5, you will have the option to select counties as well.
        3. Select Facility. The selected facility will show up as a dot in the histogram. Default selection is some of the [Lifepoint Hospitals](http://www.lifepointhealth.net/locations). 
        4. Histogram will show the selected data. If plot selected facility only, only data from the selected facility will be ploted. Otherwise, all facility that
           meets the location criteria will be plotted.
        5. A table showing data from the histogram is provided. You can use the sort values in reverse box to sort the score column. You can also click on the column header to sort any column.
        6. A map showing all facility in the table. [Interactive feature not available yet]
        
        Created by Matt Tso 2021 DS @ Dascena \n
        [App Repo](https://github.com/tsofoon/cms_dashboard)
        """
    )
    
    
    ### main ###
    life_point_HOSP_df = pd.read_csv('Data/LIFEPOINT_HOSP.csv') 
    life_point_HOSP_df['Facility Name'] = \
        life_point_HOSP_df['Facility Name'].str.upper()

    data_path = 'Data/CMS_HOSP_data/add_lat_lon/'

    data = dict()
    for f in os.listdir(data_path):
        if f == 'HOSP_all.csv':
            continue
        
        data_name = f[:-13]
        data[data_name] = pd.read_csv((data_path + '/' + f), index_col= 0 )


    st.markdown("<h1 style='text-align: left; color: lightblue;'>\
        CMS Hospital Data Explorer </h1>", unsafe_allow_html=True)
    dataset_name = st.selectbox('Dataset', list(data.keys()), index = 0)
    
    if dataset_name == 'Timely_and_Effective_Care':
        measure_name = st.selectbox('Measure Name', list(data[dataset_name]['Measure Name'].unique()), \
            index = 12)
    else:
        measure_name = st.selectbox('Measure Name', list(data[dataset_name]['Measure Name'].unique()))
    #st.write('You have selected', measure_name)

    

    df = data[dataset_name]
    df = df[df['Measure Name'] == measure_name]
    df = df[df['Score'] != 'Not Available']
    try:
        df['Score'] = df['Score'].astype(float)
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

    life_point_HOSP.remove('MEMORIAL MEDICAL CENTER')
    life_point_HOSP.remove('COMMUNITY MEDICAL CENTER')
    
    sel_HOSPs = st.multiselect(
        'Select Hospitals to Highlight',
        df['Facility Name'].unique(),
        life_point_HOSP
        )
    
    sel_HOSP_IDs = df[df['Facility Name'].isin(sel_HOSPs)]['Facility ID']
    Reverse = st.checkbox("Sort values in reverse?", value = True)
    df = df.sort_values(by = 'Score', ascending = not Reverse)
    agree = st.checkbox("Plot selected facility only")
    if agree:
        df = df[df['Facility ID'].isin(sel_HOSP_IDs)]

    fig1 = px.histogram(df, x="Score", 
        title = measure_name
    )

    
    for sel_HOSP_ID in sel_HOSP_IDs:
        val = df[df['Facility ID'] ==sel_HOSP_ID]['Score'].iloc[0]
        fig1.add_trace(go.Scatter(x=[val,val], y=[0, 0], \
            name = (df[df['Facility ID'] ==sel_HOSP_ID]['Facility ID'].iloc[0] \
                + ' ' +df[df['Facility ID'] ==sel_HOSP_ID]['Facility Name'].iloc[0]\
                + ' ' +df[df['Facility ID'] ==sel_HOSP_ID]['State'].iloc[0]    )))

    

    st.plotly_chart(fig1)
    df = movecol(df, cols_to_move=['Measure ID', 'Score'], ref_col='Facility Name', place='After')
    st.write(df.reset_index(drop = True))
   

    df = df.dropna(subset = ['lat', 'lon'])
    df['lat'] = df['lat'].astype('float')
    df['lon'] = df['lon'].astype('float')

    
    st.map(df)
if __name__ == "__main__":
    main()
