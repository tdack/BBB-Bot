    function init() {
      $("#BeagleURL").val("ws://beaglebone.local:8000/");
      $("#fwd, #left, #right, #stop, #rev, #speed").attr('disabled', 'disabled');
      $("#connectButton").on('click', function(){
        doConnect();
      });
      $("#fwd, #left, #right, #rev, #stop, #speed").on('click', function(){
        doSend(this.id + " " +$("#speed_value").val());
      });
    }
    
    function doConnect() {
      websocket = new WebSocket($("#BeagleURL").val());
      websocket.onopen = function(evt) { onOpen(evt) };
      websocket.onclose = function(evt) { onClose(evt) };
      websocket.onmessage = function(evt) { onMessage(evt) };
      websocket.onerror = function(evt) { onError(evt) };
      clearText();
      writeToScreen("connecting\n");
      $("#connectButton").html('<span class="glyphicon glyphicon-flash">');
      $("#connectButton").removeClass("btn-success").addClass("btn-info");
      setTimeout(function(){
            if (websocket.readyState == 0 || websocket.readyState == 3) {
                writeToScreen("connection failed\n");
                $("#connectButton").removeClass("btn-info").addClass("btn-success");
                $("#connectButton").html('<span class="glyphicon glyphicon-play">');
            }
       }, 5000);
    }
    
    function onOpen(evt) {
      writeToScreen("connected\n");  
      $("#connectButton").html('<span class="glyphicon glyphicon-stop">');
      $("#connectButton").removeClass("btn-success").addClass("btn-danger");
      $("#connectButton").off('click').on('click', function(){
        doDisconnect();
      });
      $("#fwd, #left, #right, #stop, #rev, #speed").removeAttr('disabled');
    }
    
    function onClose(evt) {
      writeToScreen("disconnected\n");
      $("#fwd, #left, #right, #stop, #rev, #speed").attr('disabled', 'disabled');
      $("#connectButton").html('<span class="glyphicon glyphicon-play">');
      $("#connectButton").removeClass("btn-danger").addClass("btn-success");
      $("#connectButton").off('click').on('click', function(){
        doConnect();
      });
    }
    
    function onMessage(evt) {
      if (evt.data.search("connected") != -1 ) {
          doSend("stop " +$("#speed_value").val());
          doSend("speed " +$("#speed_value").val());
      }
      if (evt.data.search("obstacle") != -1) {
        $("body").addClass("flash");
        setTimeout( function(){ $("body").removeClass("flash"); }, 3000); 
      }
      writeToScreen(evt.data + '\n');
    }
    
    function onError(evt) {
      writeToScreen(evt.data + '\n');
      websocket.close();
    }
    
    function doSend(message) {
      websocket.send(message);
    }
    
    function clearText() {
        $("#ticker").html("");
    }
    function writeToScreen(message) {
      $("#ticker").append(message.replace('\n', '<br />'));
      $("#ticker").scrollTop($("#ticker")[0].scrollHeight);
    }
    
    function doDisconnect() {
      //doSend("stop 0");
      websocket.close();
    }
  
    $(document).ready(function() {
      init();
    });