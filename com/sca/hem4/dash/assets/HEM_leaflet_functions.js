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
		draw_block_receptors: function(feature, latlng)
			{
				const square = L.icon({iconUrl: `/assets/lightbluesquare.png`, iconSize: [10, 10]});
				return L.marker(latlng, {icon: square});
			},
			
        draw_polar_receptors: function(feature, latlng)
			{
				const dot = L.icon({iconUrl: `/assets/orangecircle.png`, iconSize: [10, 10]});
				return L.marker(latlng, {icon: dot});
			},
			
        draw_polar_receptors2: function(feature, latlng)
			{
				circleOptions = {
    				fillColor: 'orange',
    				fillOpacity: 1,
    				radius: 5,
    				stroke: false
    				};
                return L.circleMarker(latlng, circleOptions);  // sender a simple circle marker
			},
		
		// For potential future use	
        draw_cluster: function(feature, latlng, index, context)
            {
        
                const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
                const csc = chroma.scale(colorscale).domain([min, max]);
                // Set color based on maximum value of leaves.
                const leaves = index.getLeaves(feature.properties.cluster_id);
                let valueMax = 0;
                for (let i = 0; i < leaves.length; ++i) {
                    const value = leaves[i].properties[colorProp];
                    if (value > valueMax) {
                        valueMax = value;
                    }
                }
            // Render a circle with the max value written in the center.
                const icon = L.divIcon.scatter({
                    html: '<div style="background-color:white;"><span>' + feature.properties.point_count_abbreviated + '</span></div>',
                    className: "marker-cluster",
                    iconSize: L.point(40, 40),
                    color: csc(valueMax)
                });
                return L.marker(latlng, {icon : icon})
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
		