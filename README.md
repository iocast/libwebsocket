<pre style="border: 0px; padding: 0px;">
 _ _ _                 _                    _        _   
| (_) |____      _____| |__  ___  ___   ___| | _____| |_ 
| | | '_ \ \ /\ / / _ \ '_ \/ __|/ _ \ / __| |/ / _ \ __|
| | | |_) \ V  V /  __/ |_) \__ \ (_) | (__|   &lt;  __/ |_ 
|_|_|_.__/ \_/\_/ \___|_.__/|___/\___/ \___|_|\_\___|\__|
</pre>

# prerequisite

* Python >= 2.7.2
* cElementTree >= 1.0.5-20051216


# test
Currently two different test servers has been implemented. A echo, which sends the incoming message back to the client, and a broadcast server, which sends messages at a predefined interval to all connected clients. Each example can be found in `tests/server` where `echo_server.py` is the echo and `broadcast_server.py` the broadcast server.

You can run a server as follow:

    python echo_server.py

In addition a web client for testing is available, which can be found in the folder `tests/webclient`. Open a terminal an go to the folder `cd tests/webclient` and start a python web server as follow:

    python -m SimpleHTTPServer 8000
    
Open the browser and enter `http://localhost:8000` to view the example.
