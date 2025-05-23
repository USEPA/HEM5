window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const square = L.icon({
                iconUrl: `/assets/greensquare.png`,
                iconSize: [10, 10]
            });

            return L.marker(latlng, {
                icon: square
            });
        },
        function1: function(feature, layer, context) {
                const map = context.myRef.current.leafletElement._map;
                L.polylineDecorator(layer, {
                    patterns: [{
                        symbol: L.Symbol.arrowHead({
                            pixelSize: 15,
                            pathOptions: {
                                fillOpacity: 1,
                                weight: 2
                            }
                        })
                    }]
                }).addTo(map);
            }

            ,
        function2: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.props.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }
            return style;
        }
    }
});