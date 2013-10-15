from py4j.java_gateway import JavaGateway

gateway = JavaGateway()
java_object = gateway.jvm.soton.Test()
other_object = java_object.hello()
print other_object
