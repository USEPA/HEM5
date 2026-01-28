window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                colorscale,
                vmin,
                vmax,
                value_property
            } = context.props.hideout;
            const value = feature.properties[value_property];
            if (value === undefined) {
                return {
                    fillColor: '#dddddd',
                    color: 'black',
                    weight: 1,
                    fillOpacity: 0.7
                };
            }
            // use chroma.js to get color from value
            const color = chroma.scale(colorscale).domain([vmin, vmax])(value);
            return {
                fillColor: color.hex(),
                color: 'black',
                weight: 1,
                fillOpacity: 0.7
            };
        }
    }
});