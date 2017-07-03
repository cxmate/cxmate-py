# python-cxmate-service

Getting Started
---------------

An offical cxMate module for Python exists on PyPi that makes developing Python cxMate services easy.

```python
from cxmate.service inport Service, Stream

class MyEchoService(Service):
    """
    MyService is a subclass 
    """
    
    def process(self, input_stream):
        """
        process is a required method, if it's not implemented, cxmate.service will throw an error
        this process implementation will echo the received network back to the sender
        
        :param input_stream: a python generator that returns CX elements
        :returns: a python generator that returns CX elements
        """
        network = Stream.to_networkx(input_stream)
        return Stream.from_networkx(network)
        
if __name__ == "__main__":
  myService = MyService()
  myService.run() #run starts the service listening for requests from cxMate
```

Stream Class
-------------

A static class with conversion methods to_networkx and from_networkx, which use python generators to translate between NetworkX and cxMate aspects.  Use networkx functions to analyze and modify the network before converting it back to cxMate aspects.
