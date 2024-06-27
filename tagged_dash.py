import streamlit as st
import plotly.graph_objs as go
from collections import Counter

import pandas as pd
def dataframe_lolist(csv):
    df=pd.read_csv(csv)
    return df.values.tolist()


hmkidsl=dataframe_lolist('output_hmkids.csv')
zarakidsl=dataframe_lolist('output_zarakids.csv')
mothercarel=dataframe_lolist('output_mothercare.csv')
# brandhmkidsl=dataframe_lolist('output_brandhmkids.csv')
# brandzarakidsl=dataframe_lolist('output_brandzarakids.csv')
# brandmothercarel=dataframe_lolist('output_brandmothercare.csv')

import json
def cleanup(nested_list):
    final=[]
    for row in nested_list:
        try:
            response=json.loads(row[1])
            if response["classification"] != "others":
                final.append(row)
        except:
             continue
    return final


finalhmkidsl=cleanup(hmkidsl)
finalzarakidsl=cleanup(zarakidsl)
finalmothercarel=cleanup(mothercarel)
# finalbrandhmkidsl=cleanup(brandhmkidsl)
# finalbrandzarakidsl=cleanup(brandzarakidsl)
# finalbrandmothercarel=cleanup(brandmothercarel)


color_map = {
    'Aqua': '#00FFFF',
    'Beige': '#F5F5DC',
    'Black': '#000000',
    'Blue': '#0000FF',
    'Brown': '#A52A2A',
    'Camo': '#78866B',
    'Charcoal': '#36454F',
    'Coral': '#FF7F50',
    'Cyan': '#00FFFF',
    'Gold': '#FFD700',
    'Green': '#008000',
    'Grey': '#808080',  
    'Ivory': '#FFFFF0',
    'Khaki': '#F0E68C',
    'Lavender': '#E6E6FA',
    'Light Blue': '#ADD8E6',
    'Magenta': '#FF00FF',
    'Maroon': '#800000',
    'Mint': '#98FF98',
    'Multi': '#FF6347',  
    'Multicolor': '#FF6347',  
    'Mustard': '#FFDB58',
    'Navy': '#000080',
    'Olive': '#808000',
    'Orange': '#FFA500',
    'Peach': '#FFDAB9',
    'Pink': '#FFC0CB',
    'Purple': '#800080',
    'Red': '#FF0000',
    'Rose Gold': '#B76E79',
    'Salmon': '#FA8072',
    'Silver': '#C0C0C0',
    'Stripe': '#D3D3D3',  
    'Turquoise': '#40E0D0',
    'White': '#FFFFFF',
    'Yellow': '#FFFF00'
}

from collections import defaultdict, Counter
def product_color_counter(final_list):
    product_colors=defaultdict(list)
    for _,row in enumerate(final_list):
        try:
            x=json.loads(row[1])
            products=x.get('fashion').keys()
            for product in products:
                colors=x.get('fashion').get(product).get('colors')
                for color in colors:
                    product_colors[product].append(color)
        except:
            continue

    product_color_count={}
    for pc in product_colors:
        product_color_count[pc]=Counter(product_colors[pc])

    return product_color_count

hmkids=product_color_counter(finalhmkidsl)
zarakids=product_color_counter(finalzarakidsl)
mothercare=product_color_counter(finalmothercarel)
# brandhmkids=product_color_counter(finalbrandhmkidsl)
# brandzarakids=product_color_counter(finalbrandzarakidsl)
# brandmothercare=product_color_counter(finalbrandmothercarel)



hm=set(hmkids.keys())
za=set(zarakids.keys())
mc=set(mothercare.keys())
intersection=hm&za&mc
common=list(intersection)
common.sort()
# hmb=set(brandhmkids.keys())
# zab=set(brandzarakids.keys())
# mcb=set(brandmothercare.keys())
# brand_common_intersection=hmb&zab&mcb
# brand_common=list(brand_common_intersection)
# brand_common.sort()

def colors(datasets):
    cols=set()
    for dataset in datasets:
        for product in dataset:
            for color in dataset[product].keys():
                cols.add(color)
    return cols
            
        
colours=colors([hmkids,zarakids,mothercare])
#brand_colours=colors([brandhmkids,brandzarakids,brandmothercare])


def reduce_labels(counter, max_labels=10):
    total = sum(counter.values())
    top_items = counter.most_common(max_labels)
    others_count = total - sum(count for _, count in top_items)
    if others_count > 0:
        top_items.append(('Other', others_count))
    return Counter(dict(top_items))

def create_pie_charts(products):
    fig = go.Figure()
    annotations = []

    def create_pie(counter, name, domain_x):
        reduced_counter = reduce_labels(counter)
        total_count = sum(counter.values())
        pie_chart = go.Pie(
            labels=list(reduced_counter.keys()),
            values=list(reduced_counter.values()),
            name=name,
            textinfo='label+percent',
            hoverinfo='label+value+percent',
            marker=dict(
                colors=[color_map.get(color, '#CCCCCC') for color in reduced_counter.keys()],
                line=dict(color='black', width=1)
            ),
            hole=0.4,
            domain={'x': domain_x, 'y': [0, 1]}
        )
        annotations.append(
            dict(
                x=sum(domain_x)/2, y=0.5,
                text=f'{name}<br>{total_count}',
                showarrow=False,
                font=dict(size=14),
                xanchor='center',
                yanchor='middle'
            )
        )
        return pie_chart

    domains = [(i / len(products), (i + 1) / len(products)) for i in range(len(products))]
    for i, product in enumerate(products):
        if product in hmkids and product in zarakids and product in mothercare:
            fig.add_trace(create_pie(hmkids[product], f'H&M Kids', [domains[i][0], domains[i][0] + 0.33]))
            fig.add_trace(create_pie(zarakids[product], f'Zara Kids', [domains[i][0] + 0.33, domains[i][0] + 0.66]))
            fig.add_trace(create_pie(mothercare[product], f'Mothercare', [domains[i][0] + 0.66, domains[i][1]]))
        else:
            annotations.append(
                dict(
                    x=sum(domains[i])/2, y=0.5,
                    text=f"No data available for {product}.",
                    showarrow=False,
                    font=dict(size=14),
                    xanchor='center',
                    yanchor='middle'
                )
            )
    fig.update_layout(
        title='Color Distribution for Selected Products',
        margin=dict(l=0, r=0, t=50, b=50),
        showlegend=False,
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=600,  # Adjust the height as needed
        annotations=annotations
    )
    return fig

# Streamlit App
st.title("Distribution in tagged posts")
selected_products = st.multiselect('Select products:', common, default=common[:1])

if selected_products:
    fig = create_pie_charts(selected_products)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please select at least one product.")
