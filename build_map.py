import folium


RESTAURANTS = (
    ("Thai Canteen", [38.5424669, -121.7409905]),
    ("Sophia's Thai Kitchen", [38.542746, -121.741362]),
    ("Guads Tacos & Beer", [38.543935, -121.745829]),
)


def main():
    fig = folium.Figure(width=800, height=600)
    m = folium.Map(location=[38.5434, -121.7413], zoom_start=15)
    fig.add_child(m)
    # A saved Figure renders directly into the document body.
    fig.header.add_child(
        folium.Element(
            "<style>html > body { width: 800px; height: 600px; }</style>"
        )
    )

    for name, location in RESTAURANTS:
        folium.Marker(location=location, popup=name, tooltip=name).add_to(m)

    fig.save("map.html")


if __name__ == "__main__":
    main()
