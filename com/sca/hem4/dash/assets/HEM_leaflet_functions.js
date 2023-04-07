window.HEM_leaflet_functions = Object.assign({}, window.HEM_leaflet_functions, {
	facs:{
		draw_facilities: function(feature, latlng, context)
			{
                const {min,
						max,
						colorscale,
						circleOptions,
						colorProp} = context.props.hideout;
                const csc = chroma.scale(colorscale).domain([min, max]);  // chroma lib to construct colorscale
                circleOptions.fillColor = csc(feature.properties[colorProp]);  // set color based on color prop.
                return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker
			}
		},
	
	
	contour:{
		draw_receptors: function(feature, latlng)
			{
				const square = L.icon({iconUrl: `/assets/greensquare.png`, iconSize: [10, 10]});
				return L.marker(latlng, {icon: square});
			},
		
		
		draw_contours: function(feature, context)
			{
				const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
				const value = feature.properties[colorProp];  // get value the determines the color
				
				for (let i = 0; i < classes.length; ++i) {
					if (value > classes[i]) {
						style.fillColor = colorscale[i];  // set the fill color according to the class
					}
				}
				return style;
			}
		}
	});
		