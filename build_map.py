import folium


RESTAURANTS = (
    ("Burgers and Brew", [38.544405, -121.743482]),
    ("Sophia's Thai Kitchen", [38.542746, -121.741362]),
    ("Guads Tacos & Beer", [38.543935, -121.745829]),
)


def main():
    fig = folium.Figure(width=800, height=600)
    m = folium.Map(location=[38.5434, -121.7413], zoom_start=15)
    fig.add_child(m)

    for name, location in RESTAURANTS:
        folium.Marker(location=location, popup=name, tooltip=name).add_to(m)

    fig.save("map.html")


if __name__ == "__main__":
    main()
