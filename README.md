cxmate-py
=========

Installation
------------

Install the cxMate SDK via pip.

```
pip install cxmate
```

Getting Started
---------------

Import the cxmate python mode:
```python
import cxmate
```

Create a subclass of the `cxMate.Service` class from the module:
```python
class MyEchoService(cxmate.Service):
```

Implement a single method in the class called process. It takes two arguments, a dictionary of parameters, and an element generator:
```python
class MyEchoService(cxmate.Service):

    def process(self, params, input_stream):
        """
        process is a required method, if it's not implemented, cxmate.service will throw an error
        this process implementation will echo the received network back to the sender

        :param input_stream: a python generator that returns CX elements
        :returns: a python generator that returns CX elements
        """
```

Whenever your service is called, cxMate will call your process method for you. you must extract networks from the element generator to create your input networks. cxMate comes with an adapter class to make conversion to popular network formats simple.
To send networks back to cxMate, you must return a network element generator. cxMate's adapter class can handle this also for various popular network formats:
```python

    def process(self, params, input_stream):
        network = Stream.to_networkx(input_stream)
        # Do stuff with network here
        return Stream.from_networkx(network)
```

Finally, setup your service to run when envoked. the cxmate.Service superclass implements a run method for you that takes an optional 'address:port' string.
```python
if __name__ == "__main__":
  myService = MyService()
  myService.run() #run starts the service listening for requests from cxMate
```
