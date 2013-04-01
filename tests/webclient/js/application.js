var ws = null;
var map = null;
var vectorLayer = null

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
                                         {numZoomLevels: 1}
                                         );
  
  
  map.addLayer(layer);
  map.zoomToMaxExtent();
  
  vectorLayer = new OpenLayers.Layer.Vector("CryEngine", {});
  map.addLayer(vectorLayer);
  
  
  $("#log").append("connecting<br/>");
  ws = new WebSocket("ws://localhost:8080");
  
  ws.onopen = function() {
  $("#log").append("connected<br/>");
  };
  
  ws.onmessage = function (e) {
  var points = JSON.parse(e.data);
  //$("#log").append("received: " + e.data + "<br/>");
  for(var i = 0; i < points.length; i++) {
  console.log("(" + points[i].x + ", " + points[i].y + ")");
  var geom = new OpenLayers.Geometry.Point(points[i].x, points[i].y);
  var feature = new OpenLayers.Feature.Vector(geom, null, null);
  vectorLayer.addFeatures([feature]);
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