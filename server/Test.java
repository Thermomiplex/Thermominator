package soton;

import py4j.GatewayServer;

public class Test {
	public Test() {
		
	}

	public String hello() {
		System.out.println("Method was called");
		return "Hi";
	}

	public static void main(String[] args) {
		Test t=new Test();

		GatewayServer gatewayServer = new GatewayServer(t);
		gatewayServer.start();
		System.out.println("Gateway Server Started");

		System.out.println("Calling Method");
		System.out.println(t.hello());
	}
}
