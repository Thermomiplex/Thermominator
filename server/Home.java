package cooling;

import java.util.ArrayList;
import java.util.List;

import events.TemperatureListener;

public class Home implements Comparable<Home> {

	public double[] internalTemp;
	public double[] externalTemp;

	public double leakageRate = 90;
	public double airMass = 1500;
	public double heatCapacity = 1000;

	public double setPoint = 23.5;
	public double tolerance = 3;

	int timeResolution;

	public int comfortPeriodStart;
	public int comfortPeriodEnd;

	double omega1 = 1;
	double omega2 = 1;
	double phi1 = 2;
	double phi2 = 2;
	double gamma = 0.8;
	
	public boolean[] cooler;
	double coolerPower = 2000;
	
	private int ID;
	
    private List<TemperatureListener> listeners = new ArrayList<TemperatureListener>();


	public Home(int id, int timeResolution) {
		this.timeResolution = timeResolution;

		int k = getTimeSlotCount();

		comfortPeriodStart = 0;
		comfortPeriodEnd = k;

		cooler = new boolean[k];

		internalTemp = new double[k];
		externalTemp = new double[k];

		for (int t = 1; t < k; t++) {
			internalTemp[t] = 0;
			externalTemp[t] = 0;
		}
		
		ID = id;		
	}

	public void randomTemp() {

		internalTemp[0] = 30;
		externalTemp[0] = 30;

		for (int t = 1; t < getTimeSlotCount(); t++) {
			externalTemp[t] = 35 + (Math.random() > 0.5 ? 1 : -1) * Math.random() * 2;
		}
	}

	public int getTimeSlotCount() {
		return 60 * 24 / timeResolution;
	}

	public static double calculateAirMass(double width, double length, double height) {
		return width * length * height * 1.249;
	}

	public void updateInternalTemperature() {

		int k = getTimeSlotCount();

		for (int t = 1; t < k; t++) {
			double temperature = internalTemp[t - 1];
			temperature += (k * getTotalHeatInput(t)) / (heatCapacity * airMass);
			internalTemp[t] = temperature;
		}
		
		notifyTemperaturesListeners();
	}
	
	public void resetCooler() {
		for (int t = 0; t < getTimeSlotCount(); t++) {
			cooler[t] = false;
		}
	}

	public double getTotalHeatInput(int t) {
		double input = -1 * (cooler[t - 1] ? 1 : 0) * coolerPower;
		input -= leakageRate * (internalTemp[t - 1] - externalTemp[t - 1]);
		return input;
	}

	public double getTotalDiscomfort() {

		double totalDiscomfort = 0;

		int start = Math.max(1, comfortPeriodStart);

		for (int t = start; t < comfortPeriodEnd; t++) {
			totalDiscomfort += omega1 * phi1 * (internalTemp[t] - setPoint) + gamma * omega2 * phi2 * (internalTemp[t - 1] - setPoint);
		}

		return totalDiscomfort;

	}
	
	public double getMaximumTemperatureDeviation() {
		double max = 0;
		
		for (int t = comfortPeriodStart; t < comfortPeriodEnd; t++) {
			
			double diff = Math.abs(internalTemp[t] - setPoint);
			
			if (diff > max) {
				max = diff;
			}
		}
		return max;
	}

	public double getAverageTemperatureDeviation() {

		double avg = 0;

		int start = Math.max(1, comfortPeriodStart);

		for (int t = start; t < comfortPeriodEnd; t++) {
			avg += internalTemp[t];
		}
		
		avg /= (comfortPeriodEnd - start);

		return avg - setPoint;
	}

	public double getConsumption() {

		double consumption = 0;

		for (int t = 0; t < getTimeSlotCount(); t++) {
			consumption += (cooler[t] ? 1 : 0) * coolerPower;
		}

		return consumption;

	}

	public double getConsumptionAtTimeSlot(int t) {
		return (cooler[t] ? 1 : 0) * coolerPower;
	}
	
	public boolean isSatisfied() {
		return getAverageTemperatureDeviation() <= tolerance && getMaximumTemperatureDeviation() <= tolerance;
	}
	
	@Override
	public String toString() {
		return String.valueOf(ID);
	}	
	
	@Override
	public Home clone() {

		Home clone = new Home(1 , timeResolution);

		clone.airMass = airMass;
		clone.leakageRate = leakageRate;
		clone.coolerPower = coolerPower;
		clone.heatCapacity = heatCapacity;

		clone.setPoint = setPoint;
		clone.tolerance = tolerance;

		clone.comfortPeriodStart = comfortPeriodStart;
		clone.comfortPeriodEnd = comfortPeriodEnd;

		System.arraycopy(internalTemp, 0, clone.internalTemp, 0, internalTemp.length);
		System.arraycopy(externalTemp, 0, clone.externalTemp, 0, externalTemp.length);
		System.arraycopy(cooler, 0, clone.cooler, 0, cooler.length);

		return clone;
	}

	@Override
	public int compareTo(Home home) {
		return Double.compare(tolerance/(comfortPeriodStart - comfortPeriodEnd), home.tolerance / (home.comfortPeriodStart - home.comfortPeriodEnd));
	}
	
	public void addTemperatureListener(TemperatureListener listener) {
		listeners.add(listener);
	}
	
	public void notifyTemperaturesListeners() {
		for (TemperatureListener listener : listeners) {
			listener.internalTemperatureChanged();
		}
	}
}
