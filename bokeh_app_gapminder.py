## 7. CASE STUDY WITH GAPMINDER DATA  (put it all together!)
    #make a single interactive application with a plot and several controls for 
    #changing the visualization, using a subset of the gapminder data.
    #our app will include:
        #a slider to control the year
        #a dropdown menu to control the x-axis data (i.e. 'indicator on the x-axis')
        #a dropdown menu to control the y-axis data
        #the 2 indicators are plotted in a scatterplot, shaded (colored) by the 
        #region (continent) in the world they are associated with. 
        #scrubbing the slider allows to move the display data forward and backward
        #through time.        
        #(it's kind of Hans Rossling style :))                      
                                                    
    #7.1 Build the gapminder data set in the gapminder_dataset.py script:
import pandas as pd
import numpy as np

#CREATING THE GAPMINDER DATASET:   
gapminder = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')
infmort = pd.read_excel("indicator_gapminder_infant_mortality.xlsx")
infmort = infmort.iloc[:,[0,153,158,163,168,173,178,183,188,193,198,203,208]]
infmort.rename(columns={'Infant mortality rate':'country'}, inplace=True)
infmortmelt = pd.melt(frame=infmort, id_vars='country', var_name = "year", value_name='infant_mortality_rate') 
infmortmelt.year = infmortmelt.year.astype('int64')
infmortmelt.country = infmortmelt.country.apply(str.lower)
infmortmelt.country = infmortmelt.country.apply(str.strip)
gapminder.country = gapminder.country.apply(str.lower)
gapminder.country = gapminder.country.apply(str.strip)
np.setdiff1d(gapminder.country, infmortmelt.country) # array(['korea, dem. rep.', 'korea, rep.', 'yemen, rep.'], dtype=object)
            #merge gapminder and infmortmelt:
gapminder = pd.merge(left=gapminder, right=infmortmelt, on=["country","year"], how="left")

fertility = pd.read_excel("indicator_gapminder_fertility.xlsx")
fertility = fertility.iloc[:,[0,153,158,163,168,173,178,183,188,193,198,203,208]]
fertility.rename(columns={'Total fertility rate':'country'}, inplace=True)
fertilitymelt = pd.melt(frame=fertility, id_vars='country', var_name = "year", value_name='fertility') 
fertilitymelt.year = fertilitymelt.year.astype('int64')
fertilitymelt.country = fertilitymelt.country.apply(str.lower)
fertilitymelt.country = fertilitymelt.country.apply(str.strip)
np.setdiff1d(gapminder.country, fertilitymelt.country) #array(['korea, dem. rep.', 'korea, rep.', 'yemen, rep.'], dtype=object)
gapminder = pd.merge(left=gapminder, right=fertilitymelt, on=["country","year"], how="left")

        #put year as index:
gapminder.set_index("year", inplace=True)
        #change column names
gapminder.rename(columns={'pop':'population'}, inplace=True)  
#gapminder.rename(columns={'lifeExp':'life expectancy'}, inplace=True) 
#gapminder.rename(columns={'gdpPercap':'gdp per capita'}, inplace=True) 
#gapminder.rename(columns={'infant_mortality_rate':'infant mortality rate'}, inplace=True) 

    #7.2 Exploratory data analysis:
        #check out the dataframe structure
gapminder.shape   #(1704, 7)  so 1704 rows and 7 columns

gapminder.info()   
"""
    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 1704 entries, 1952 to 2007    #year as index!
    Data columns (total 7 columns):
    country                  1704 non-null object
    population               1704 non-null float64
    continent                1704 non-null object
    lifeExp                  1704 non-null float64
    gdpPercap                1704 non-null float64
    infant_mortality_rate    1420 non-null float64
    fertility                1668 non-null float64
    dtypes: float64(5), object(2)
    memory usage: 106.5+ KB
"""
gapminder.head()
"""
              country  population continent  lifeExp   gdpPercap  \
    year                                                           
    1952  afghanistan   8425333.0      Asia   28.801  779.445314   
    1957  afghanistan   9240934.0      Asia   30.332  820.853030   
    1962  afghanistan  10267083.0      Asia   31.997  853.100710   
    1967  afghanistan  11537966.0      Asia   34.020  836.197138   
    1972  afghanistan  13079460.0      Asia   36.088  739.981106   
    
          infant_mortality_rate  fertility  
    year                                    
    1952                    NaN       7.67  
    1957                    NaN       7.67  
    1962                  236.3       7.67  
    1967                  217.0       7.67  
    1972                  198.2       7.67   
"""


    #7.3 Start the application:  Build a Bokeh app around the gapminder data:
        
        #a. Create 'just a plot' with some of the data:
            #e.g. a simple plot of Life Expectancy versus Fertility 
            #for the year 1972 only:
from bokeh.io import curdoc
from bokeh.io import output_file, show
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource
curdoc().clear()

source = ColumnDataSource(data={  #make a ColumnDataSource from the relevant gapminder data
    'x'        : gapminder.loc[1972].fertility,
    'y'        : gapminder.loc[1972].lifeExp,
    'country'  : gapminder.loc[1972].country,
    'continent' : gapminder.loc[1972].continent,
    'population'      : gapminder.loc[1972].population   
})

                        #save the min and max values to use for the x_range and y_range
xmin, xmax = min(gapminder.fertility), max(gapminder.fertility)
ymin, ymax = min(gapminder.lifeExp), max(gapminder.lifeExp)

plot = figure(title='Gapminder data for 1972', x_range=(xmin, xmax), y_range=(ymin, ymax),
           plot_height=400, plot_width=700, x_axis_label="Fertility (children per woman)",
           y_axis_label="Life expectancy (years)")

        #b. Color the data point by a third variable: continent:
from bokeh.models import CategoricalColorMapper
from bokeh.palettes import Spectral6

continent_list = gapminder.continent.unique().tolist() #make a list of the unique values of continent

color_mapper = CategoricalColorMapper(factors=continent_list, palette=Spectral6) #make a colormapper

plot.circle(x='x', y='y', fill_alpha=0.8, source=source, #add the color mapper to the circle glyph
            color=dict(field='continent', transform=color_mapper), legend='continent')

plot.legend.location = 'top_right' #set the legend.location attribute of the plot to 'top_right'

#output_file('gapminder.html')
#show(plot)

#curdoc().add_root(plot)  #add the plot to the current document and add the title
curdoc().title = 'Gapminder'


        #c. Adding a slider with which you can select the year that is being plotted:
            #the title of the plot is also updated according to the year with plot.title.text!
                #In Python, you can format strings by specifying placeholders with
                #the % keyword. For example, if you have a string company = 'DataCamp',
                #you can use print('%s' % company) to print DataCamp. 
                #Placeholders are useful when you are printing values that are 
                #not static, such as the value of the year slider. 
                #You can specify a placeholder for a number with %d. 
                #Here, when you're updating the plot title inside your
                #callback function, you should make use of a placeholder so that 
                #the year displayed is in accordance with the value of the year slider.
from bokeh.layouts import widgetbox, row
from bokeh.models import Slider

#def update_plot(attr, old, new):   #define the callbackfunction for the slider
#    yr = slider.value
#    new_data = {
#        'x'       : gapminder.loc[yr].fertility,
#        'y'       : gapminder.loc[yr].lifeExp,
#        'country' : gapminder.loc[yr].country,
#        'continent'  : gapminder.loc[yr].continent,
#        'population'     : gapminder.loc[yr].population
#    }
#    source.data = new_data
#    plot.title.text = "Gapminder data for %d % yr"  #update title of plot with correct year
#
#slider = Slider(start=1952, end=2007, step=5, value=1952, title="Year") #make a slider
#                                                                        #value = start value
#slider.on_change('value', update_plot) #attach the callback to the 'value' property of slider

#output_file('gapminder.html')  #slider doesn't work ... maybe you NEED the ..
#show(plot)                     #..Bokeh Server to show the slider....:S

#layout = row(widgetbox(slider), plot) #make a row layout of widgetbox(slider) and plot
#curdoc().add_root(layout) #add it to the current document


        #d. Add a hovertool to the app:
            #to display more detailed information about each scatterpoint 
            #here: if you hover over a scatterpoint it shows the country name.
from bokeh.models import HoverTool

hover = HoverTool(tooltips=[('Country', '@country')]) #HoverTool tooltips accepts a list of tuples with
                                                      #('legend label','@columnname')
plot.add_tools(hover)  #this adds the hovertool to the plot after plot is already created

#layout = row(widgetbox(slider), plot)
#curdoc().add_root(layout)


        #e. Add 2 dropdown menus so users can choose which variables/columns
            #to display on the plot
from bokeh.models import Select
print("testing")
def update_plot(attr, old, new):
    print("update plot")
    yr = slider.value       #read the current value off the slider: yr
    x = x_select.value      #read the current value off dropdown menu for x_axis: x
    y = y_select.value      #read the current value off dropdown menu for y_axis: y

    plot.xaxis.axis_label = x      #label axes of plot with the chosen menu option 
    plot.yaxis.axis_label = y
 
    new_data = {        #set new_data
        'x'       : gapminder.loc[yr][x],
        'y'       : gapminder.loc[yr][y],
        'country' : gapminder.loc[yr].country,
        'continent'  : gapminder.loc[yr].continent,
        'population'     : gapminder.loc[yr].population
    }

    source.data = new_data     #assign new_data to source.data
    xrange_start =  min(source.data['x'])
    print(xrange_start)
    plot.x_range.start = xrange_start    #set the range of all axes
    plot.x_range.end = max(source.data['x'])
    plot.y_range.start = min(source.data['y'])
    plot.y_range.end = max(source.data['y'])
    plot.title.text = 'Gapminder data for {0}'.format(yr)  #add title to plot with selected year in it

slider = Slider(start=1952, end=2007, step=5, value=1952, title='Year') #create a slider widget

slider.on_change('value', update_plot) #attach the callback to the 'value' property of slider

x_select = Select( #create a dropdown menu (i.e. a Select widget) for the x data: x_select
    options=['fertility', 'lifeExp', 'infant_mortality_rate', 'gdpPercap'],
    value='fertility',  #(this is the start value)
    title='x-axis data'
)

x_select.on_change('value', update_plot) #attach the update_plot callback to the 'value' property of x_select

y_select = Select(  #create a dropdown menu (i.e. a Select widget) for the y data: y_select
    options=['fertility', 'lifeExp', 'infant_mortality_rate', 'gdpPercap'],
    value='lifeExp',   #(this is the start value)
    title='y-axis data'
)

y_select.on_change('value',update_plot) #attach the update_plot callback to the 'value' property of y_select


layout = row(widgetbox(slider, x_select, y_select), plot)  #create layout
curdoc().add_root(layout)  #add to the current document


    #7.4 EXECUTE THE APPLICATION!!! 
        # - put the code for the application in a separate python script (so here 
        #full chapter 7.) and name the script 'test.py' (or something else)
        #(i allready made test.py and it works)
        # - you also have to include the full code for building the gapminder dataset in this script! 
        # - put the script in the directory C:\\Users\\Kimberley (or specify the location in the bokeh serve command)
        # - run the following command in the Windows Command Prompt to open the application
        #in a browser: 
#bokeh serve --show bokeh_app_gapminder.py 
