import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
from PIL import Image
import plotly.express as px
import random
import webbrowser

pd.set_option('display.max_columns', 2000)
pd.set_option('display.max_rows', 2000)
pd.set_option('display.width', 2000)

def setRadius(zFactor = 3):
    if zFactor == 3:
        cRadius = 80000
    elif zFactor == 4:
        cRadius = 40000
    elif zFactor == 5:
        cRadius = 20000
    elif zFactor == 6:
        cRadius = 10000
    elif zFactor == 7:
        cRadius = 5000
    elif zFactor == 8:
        cRadius = 2500
    return cRadius

# Not required any more
#MAPKEY = "pk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DApk.eyJ1IjoiY2hlY2ttYXJrIiwiYSI6ImNrOTI0NzU3YTA0azYzZ21rZHRtM2tuYTcifQ.6aQ9nlBpGbomhySWPF98DA"

# Read data in from csv file into a Pandas DataFrame
df = pd.read_csv('volcanoes.csv', encoding = 'Latin-1')

# Create a new DataFrame called DF1 to pull out
# only the columns of data I want to use.
DF1 = pd.DataFrame(df, columns=['Country','VolcanoName','PrimaryVolcanoType','Elevation','Latitude','Longitude','Link'])

# Sort the data in the data frame by the Country and
# Volcano Name columns in the DF1 dataframe
DF1 = DF1.sort_values(by = ['Country', 'VolcanoName'])

# Create a list using the Pandas unique function
# of all the unique country names
countryList = sorted(DF1.Country.unique())

volcanoType = sorted(DF1.PrimaryVolcanoType.unique())

# Get the index value from the countryList
# for the country called Indonesia, will be
# used to set the default SelectBox value
defaultCountry = countryList.index('Indonesia')
defaultType = volcanoType.index('Stratovolcano')
# Create a Sidebar with the Header "Input"
st.sidebar.header('Inputs')
countrySelection = st.sidebar.selectbox("Select a Country: ", list(countryList), index = defaultCountry)
DF1 = DF1.sort_values(by = ['Country', 'VolcanoName'])

# Add a SelectBox with all the volcano countries
# with the country Indonesia selected.

#typeSelection = st.sidebar.selectbox("Select a Volcano Type: ", list(volcanoType), index = defaultType)
# Create a Slider in the Sidebar that is used
# to control the Zoom factor (0 - 6), the default is 3
DF2 = DF1[DF1['Country'] == countrySelection] 
volcanoList = sorted(DF2.VolcanoName.unique())
volcanoSelection = st.sidebar.selectbox("Select a Volcano: ", list(volcanoList))
z2 = st.sidebar.slider('Map: Zoom Factor',min_value = 3, max_value = 8, value = 4)

DF3 = DF2[DF2['VolcanoName'] == volcanoSelection]


# Create a new Pandas DataFrame called DF2
# that be used to plot the volcanos from the
# selected country from SelectBox

lat = DF3.iloc[0]['Latitude']
long = DF3.iloc[0]['Longitude']
url = DF3.iloc[0]['Link']
print(DF3)
print(lat)
print(long)
# Build name values and data values into
# lists that are used to create the Pie
# Chart for the volcano types in a country.
d = DF2.groupby(["PrimaryVolcanoType"])["PrimaryVolcanoType"].count()
type_dict = d.to_dict()
keyslist = []
for key in type_dict.keys():
    keyslist.append(key)
valueslist = list(type_dict.values())

#DF3 = DF2[DF2['PrimaryVolcanoType'] == typeSelection]
# Create a Streamlit title item and
# and an image called volcanoes.jpg
# with a caption at the bottom of the image.
st.title("Volcanoes")
image = Image.open('volcanoes.jpg')
st.image(image, caption = 'Anak Krakatau volcano, Sunda Strait, Indonesia')

# Add a Streamlit Subheader and
# printout the DF2 dataframe into the webpage
st.subheader(f"Volcano Eruption Data for {countrySelection}")
st.dataframe(DF1[DF1['Country'] == countrySelection])

# Add another Subheader for the Volcano mapped
# locations
st.subheader(f"Volcano Eruption Mapping in {countrySelection}")

# Define the ViewState for the map
# that will displayed on the webpage
# Used in the pyDeck Deck function
view_state = pdk.ViewState(
    latitude = lat, #DF2["Latitude"].mean(),
    longitude = long, #DF2["Longitude"].mean(),
    zoom = z2)

# Define the Layer as a ScatterplotLayer
# and define what dataset that has the
# lat and long values, the radius size
# and radius color. Used pyDeck Deck function
layer1 = pdk.Layer('ScatterplotLayer',
                  data = DF2,
                  pickable = True,
                  opacity = 0.10,
                  get_position = '[Longitude,Latitude]',
                  get_radius = setRadius(z2),
                  get_color=[0,128,255],
                  )

layer2 = pdk.Layer('ScatterplotLayer',
                  data = DF3,
                  pickable = True,
                  opacity = 0.25,
                  get_position = '[Longitude,Latitude]',
                  get_radius = setRadius(z2),
                  get_color=[255,255,0],
                  )

# Define a tool tip that pops up over
# a volcano location with:
# Volcano name, Volcano type, Lat and Long values
tool_tip = {"html": "<b>Volcano Name:</b> {VolcanoName} <br/>Type: {PrimaryVolcanoType} <br/>Elevation: {Elevation} meters",
            "style": { "backgroundColor": "steelblue",
                        "color": "black"}
          }

# Create the pyDeck object which
# defines the map style, layers, view state,
# and the tooltip objects.
map = pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    layers = [layer1, layer2],
    initial_view_state = view_state,
    tooltip = tool_tip
)

# Create and initalize the pydeck
# object and displays the all the
# Streamlit objects on the webpage
st.pydeck_chart(map)
st.info(f'For more information on the volcano **{volcanoSelection}**, click on the link below:')
st.markdown(url, unsafe_allow_html=True)
st.subheader(f"\nVolcano Types By Percentage in {countrySelection}")
fig = px.pie(d, values=valueslist, names=keyslist)
st.plotly_chart(fig)

st.subheader("Volcano Fun Facts")
keylistcount = len(keyslist)
previousRandomValue = -1
for i in range(0,2):
    randomValue = random.randint(0, keylistcount - 1)
    if randomValue != previousRandomValue:
        previousRandomValue = randomValue
    else:
        while randomValue == previousRandomValue:
            randomValue = random.randint(0, keylistcount - 1)
        
    #print(randomValue, keyslist)
    #print(volcanoType)
    if keyslist[randomValue] == 'Caldera' or keyslist[randomValue] == 'Explosion crater':
        st.write(f"{keyslist[randomValue]} is a large depression formed when a volcano erupts and collapses. {keyslist[randomValue]} vary in size from one to 100 kilometers (0.62 to 62 miles) in diameter.")
    elif keyslist[randomValue] == 'Complex' or keyslist[randomValue] == 'Compound' or keyslist[randomValue] == 'Stratovolcano':
        st.write(f"{keyslist[randomValue]} is a mixed landform consisting of related volcanic centers and their associated lava flows and pyroclastic rock.")
    elif keyslist[randomValue] == 'Cone' or keyslist[randomValue] == 'Tuff cone' or keyslist[randomValue] == 'Lava cone' or keyslist[randomValue] == 'Pyroclastic cone':
        st.write(f"{keyslist[randomValue]} a conical volcano with a low, steep profile, having been formed mostly by the cinders or scoria that fall from lava that has violently spewed into the air and broken into fragments.")
    elif keyslist[randomValue] == 'Crater rows':
        st.write(f"{keyslist[randomValue]} are fountains along the fissure that produce small spatter and cinder cones. The fragments that form a spatter cone are hot and plastic enough to weld together, while the fragments that form a cinder cone remain separate because of their lower temperature.")
    elif keyslist[randomValue] == 'Fissure vent':
        st.write(f"{keyslist[randomValue]} are a type of volcano in which the lava eruptions through a linear volcanic vent. Usually these eruptions do not involve an explosion. Because fissure vent volcanoes are usually only several meters wide but can range in length up to many kilometers.")
    elif keyslist[randomValue] == 'Lava cone':
        st.write(f"{keyslist[randomValue]} is a type of volcano composed primarily of viscous lava flows.")
    elif keyslist[randomValue] == 'Lava dome':
        st.write(f"{keyslist[randomValue]} is a circular mound-shaped protrusion resulting from the slow extrusion of viscous lava from a volcano.")
    elif keyslist[randomValue] == 'Maar' or keyslist[randomValue] == 'Tuff ring':
        st.write(f"{keyslist[randomValue]} is a small volcanic cone of low relief that surrounds a shallow crater. These craters are formed by explosions caused by hot magma coming in contact with cold groundwater.")
    elif keyslist[randomValue] == 'Shield' or keyslist[randomValue] == 'Pyroclastic shield':
        st.write(f"{keyslist[randomValue]} is a wide volcano with shallowly-sloping sides. Many of the largest volcanoes on Earth are shield volcanoes.")
    elif keyslist[randomValue] == 'Subglacial':
        st.write(f"{keyslist[randomValue]} is a volcanic form produced by subglacial eruptions or eruptions beneath the surface of a glacier or ice sheet which is then melted into a lake by the rising lava.")
    elif keyslist[randomValue] == 'Submarine':
        st.write(f"{keyslist[randomValue]} are underwater vents or fissures in the Earth's surface from which magma can erupt. Many submarine volcanoes are located near areas of tectonic plate formation, known as mid-ocean ridges.")
    elif keyslist[randomValue] == 'Volcanic field':
        st.write(f"{keyslist[randomValue]} is an area of the Earth's crust that is prone to localized volcanic activity. They usually consist of clusters of up to 100 volcanoes such as cinder cones.")
    if keylistcount == 1:
        break


