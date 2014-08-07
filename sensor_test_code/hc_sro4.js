// Generate trigger pulses for HC-SR04 sonar using Bonescript

// Could be used to measure distance using edge triggering on P8_15
// accuracy wouldn't be that good though

var b = require('bonescript');

b.pinMode("P9_12", b.OUTPUT);
b.digitalWrite("P8_12", b.LOW);
b.pinMode("P8_15", b.INPUT);

setInterval(function(){
        b.digitalWrite("P9_12", b.HIGH);
        setTimeout(function() {
            b.digitalWrite("P9_12", b.LOW);
        }, 0.01);
}, 50);        
