var ws = null;
var map = null;
var vectorLayer = null;
var infoLayer = null;


var wkt = null;
var geomFact = null;
var jsts_reader = null;
var jsts_parser = null;
 
  var style= {
      strokeColor: "#ee2200",
      fillColor: "#ee9900",
      fillOpacity: 0.5,
      strokeOpacity: 1,
      strokeWidth: 1.5
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
                                         new OpenLayers.Size(800, 600),
                                         {numZoomLevels: 1,
                                         isBaseLayer : true}
                                         );
                                         
  infoLayer = new OpenLayers.Layer.Image(
                                         'Wegnetz',
                                         '/data/schweiz.png',
                                         new OpenLayers.Bounds(566250, 223400, 570575, 226640),
                                         new OpenLayers.Size(800, 600),
                                         {numZoomLevels: 1}   
                                         ); 

  map.addLayer(layer);
  map.zoomToMaxExtent();
  
  vectorLayer = new OpenLayers.Layer.Vector("CryEngine", {});
  map.addLayer(vectorLayer);
  
  
  wkt = new OpenLayers.Format.WKT();
  geomFact = new jsts.geom.GeometryFactory();
  jsts_reader = new jsts.io.WKTReader();
  jsts_parser = new jsts.io.OpenLayersParser();
  
  
  $("#log").append("connecting<br/>");
  ws = new WebSocket("ws://localhost:8080");
  
  ws.onopen = function() {
  $("#log").append("connected<br/>");
  };
  
  ws.onmessage = function (e) {
      // remove points
  		for(var i = vectorLayer.features.length; i > 19 ; i--) {
  			vectorLayer.removeFeatures([vectorLayer.features[0]]);
  		}
  		

  	
  	
  	
  var points = JSON.parse(e.data);

  for(var i = 0; i < points.length; i++) {
    
  var maxPx = 50.0;
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
  var feature = new OpenLayers.Feature.Vector(jsts_parser.write(jsts_vector), null, style);
  
  vectorLayer.addFeatures([feature]);
  
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




