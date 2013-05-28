//var style_pt_old = new OpenLayers.Style();

/**for(var i = 0; i < vectorLayer.features.length ; i++){

	var rule[i] = new OpenLayers.Rule({
  		filter: new OpenLayers.Filter.Comparison({
      		type: OpenLayers.Filter.Comparison.EQUAL_TO,
      		property: "count",
      		value: i-1,
  		}),
  
		symbolizer: {strokeColor: "#ee2200",
      	fillColor: "#ee9900",
      	fillOpacity: 1/i,
      	strokeOpacity: 1/i,
      	strokeWidth: 1.5
     	};

	});
	
	style_pt_old.addRules([rule[i]]);
};


*/
var ws = null;
var map = null;
var vectorLayer = null;
var infoLayer = null;
var windLayer = null;
var punktLayer = null;


var wkt = null;
var geomFact = null;
var jsts_reader = null;
var jsts_parser = null;
 
  var style= {
      strokeColor: "#6C2106",
      fillColor: "#8BDF63",
      fillOpacity: 0.3,
      strokeOpacity: 0.6,
      strokeWidth: 1.5
      };
	  
  var style_pt= {
      strokeColor: "#ee2200",
      fillColor: "#ee9900",
      fillOpacity: 0.5,
      strokeOpacity: 1,
      strokeWidth: 1.5
      };
      
  var style_wind= {
      strokeColor: "#5858FA",
      strokeOpacity: 1,
      strokeWidth: 3
      };


function radian(degree) {
    return degree * (Math.PI / 180)
}
function degree(radian) {
    return radian * (180 / Math.PI)
}

$(function() {
  map = new OpenLayers.Map('map', {
                           controls : [],
                           projection: new OpenLayers.Projection('EPSG:21781'),
                           displayProjection: new OpenLayers.Projection('EPSG:21781'),
                           });
  
  var layer = new OpenLayers.Layer.Image(
                                         'Orthophoto',
                                         '/data/orthophoto_small.png',
                                         new OpenLayers.Bounds(566250, 223400, 570575, 226640),
                                         new OpenLayers.Size(1000, 750),
                                         {numZoomLevels: 1,
                                         isBaseLayer : true}
                                         );
                                         
  infoLayer = new OpenLayers.Layer.Image(
                                         'Wegnetz',
                                         '/data/map_final.png',
                                         new OpenLayers.Bounds(566250, 223400, 570575, 226640),
                                         new OpenLayers.Size(1000, 750),
                                         {numZoomLevels: 1}   
                                         ); 

  map.addLayer(layer);
  map.zoomToMaxExtent();
  
  vectorLayer = new OpenLayers.Layer.Vector("CryEngine", {});
  map.addLayer(vectorLayer);
  
  punktLayer = new OpenLayers.Layer.Vector("Aktuelle Position",{});
  map.addLayer(punktLayer);
  
  windLayer = new OpenLayers.Layer.Vector("Windrichtugn", {});
  map.addLayer(windLayer);
  
  
  wkt = new OpenLayers.Format.WKT();
  geomFact = new jsts.geom.GeometryFactory();
  jsts_reader = new jsts.io.WKTReader();
  jsts_parser = new jsts.io.OpenLayersParser();
  
  //console.log("connecting");
  ws = new WebSocket("ws://129.132.91.204:8080");
  
  ws.onopen = function() {
  //console.log("connected");
  };
  
  ws.onmessage = function (e) {
  	// remove points
  		for(var i = vectorLayer.features.length; i > 9 ; i--) {
  			vectorLayer.removeFeatures([vectorLayer.features[0]]);
  		}
  		
  windLayer.removeAllFeatures(windLayer);
  
  punktLayer.removeAllFeatures(punktLayer);
  		
  var points = JSON.parse(e.data);

  for(var i = 0; i < points.length; i++) {
    
 // Position mit Blickrichtung anzeigen
 
  var maxPx = 75.0;
  var maxHeight = 2000.0;
  
  var centroid = {
  x : parseFloat(points[i].x) + 565252,
  y : parseFloat(points[i].y) + 218749,
  z : parseFloat(points[i].z) + 685
  }
  var yaw = parseFloat(points[i].yaw);
  var r = centroid.z / maxHeight * maxPx;
  
  var pointOnCircle = {
  x : centroid.x + 2*r * Math.cos(radian(yaw)),
  y : centroid.y + 2*r * Math.sin(radian(yaw))
  }
  
  var r2 = Math.sqrt(r*r + (2*r)*(2*r))
  var alpha = Math.acos((r*r - (2*r)*(2*r) - r2*r2)/(-2 * (2*r) * r2))
  
  var rectangle_coord = [
                         new jsts.geom.Coordinate(centroid.x, centroid.y),
                         new jsts.geom.Coordinate(centroid.x + r2 * Math.sin(radian(yaw) + alpha), centroid.y + r2 * Math.cos(radian(yaw) + alpha)),
                         new jsts.geom.Coordinate(centroid.x + r2 * Math.sin(radian(yaw) - alpha), centroid.y + r2 * Math.cos(radian(yaw) - alpha))
                         ];
  
  
  
  var jsts_rectangle = geomFact.createPolygon(geomFact.createLinearRing(rectangle_coord));
  
  
  var circle = OpenLayers.Geometry.Polygon.createRegularPolygon(new OpenLayers.Geometry.Point(centroid.x, centroid.y), r, 30, 0);
  
  var jsts_circle = jsts_reader.read(wkt.write(new OpenLayers.Feature.Vector(circle, null, null)));
  
  jsts_rectangle = jsts_reader.read(wkt.write(new OpenLayers.Feature.Vector(jsts_parser.write(jsts_rectangle), null, null)));
 
  var jsts_vector = jsts_rectangle.union(jsts_circle);
  var feature = new OpenLayers.Feature.Vector(jsts_parser.write(jsts_circle), null, style);
  var feature2 = new OpenLayers.Feature.Vector(jsts_parser.write(jsts_vector), null, style_pt);
  
  vectorLayer.addFeatures([feature]);
  punktLayer.addFeatures([feature2]);
  
  // Windrichtung anzeigen
  var w_richtung = 0;
  if(points[i].W_Richtung == "Nord") {
  	w_richtung = 180;
  	}
  	
  else if (points[i].W_Richtung == "Ost") {
  	w_richtung = 270;
 	}
 	
  else if (points[i].W_Richtung == "Sued") {
 	w_richtung = 0;
  	}
  	
  else if (points[i].W_Richtung == "West") {
  	w_richtung = 90;
  	}
  	
  else {
  	w_richtung = 300;
 	}

  
  var point = new OpenLayers.Geometry.Point(570200, 223700);
  var point2 = new OpenLayers.Geometry.Point(point.x + 100 * Math.sin(radian(w_richtung)), point.y + 100 * Math.cos(radian(w_richtung)));
  var point3 = new OpenLayers.Geometry.Point(point2.x + 66 * Math.sin(radian(w_richtung + 210)), point2.y + 100 * Math.cos(radian(w_richtung + 210)));
  var point4 = new OpenLayers.Geometry.Point(point2.x + 66 * Math.sin(radian(w_richtung + 150)), point2.y + 100 * Math.cos(radian(w_richtung + 150)));
  var point5 = new OpenLayers.Geometry.Point(point.x + 66 * Math.sin(radian(w_richtung + 180)), point.y + 150 * Math.cos(radian(w_richtung + 180)));
  
  var pointList = [
  				   point,
  				   point2
 				   ];
 				   
  var pointList2 =[ 
  				   point2,
  				   point3
  				   ];
  				   
  var pointList3 =[ 
  				   point2,
  				   point4
  				   ];
  				   
  var pointList4 =[ 
  				   point,
  				   point5
  				   ];
    
  var lineFeature  = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(pointList),null, style_wind);
  var lineFeature2 = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(pointList2),null, style_wind);
  var lineFeature3 = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(pointList3),null, style_wind);
  var lineFeature4 = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.LineString(pointList4),null, style_wind);
  
  windLayer.addFeatures([lineFeature, lineFeature2, lineFeature3, lineFeature4]);
  
  
  // Verschiedene Layereinblenden
  
  if(points[i].Input_LB == "show") {
  	map.removeLayer(layer);
  	map.addLayer(infoLayer);
 	} 
  else if (points[i].Input_LB == "hide") {
  	map.removeLayer(infoLayer);
  	map.addLayer(layer);
  	}
  
  }
  
  vectorLayer.redraw();
  windLayer.redraw();
  punktLayer.redraw();
  };
  
  
  $("#exec").click(function() {
                   msg = $("#msg").val();
                   $("#log").append("sent: " + msg + "<br/>");
                   ws.send(msg);
                   return false;
                   });
  
  });






/*
 window.onbeforeunload = function() {
 ws.send("DISCONNECTED");
 ws.onclose = function () {}; // disable onclose handler first
 ws.close()
 };
 */




