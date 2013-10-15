package optimisation;

import java.util.Date;
import java.util.List;

import visualisation.TemperaturePlotter;

import cooling.Home;
import events.TemperatureListener;

public class GreedyOptimiser {
	
	public static int MAX_ITERATIONS = 200;

	public static void optimise(Home home) {
		
		home.resetCooler();
		
		home.updateInternalTemperature();

		double bestAvgDeviation = Double.MAX_VALUE;
		double bestMaxDeviation = Double.MAX_VALUE;
		
		Home testHome = home.clone();
		
		int bestTimeToSwitchOn = -1;
		
		int iteration = 0;
		
		while (iteration < MAX_ITERATIONS && (home.getAverageTemperatureDeviation() > home.tolerance || home.getMaximumTemperatureDeviation() > home.tolerance)) {

			for (int time = 0; time < home.getTimeSlotCount(); time++) {
				
				System.arraycopy(home.cooler, 0, testHome.cooler, 0, home.cooler.length);
				
				testHome.cooler[time] = true;

				testHome.updateInternalTemperature();

				double testAvgDeviation = testHome.getAverageTemperatureDeviation();
				double testMaxDeviation = testHome.getMaximumTemperatureDeviation();

				if (testAvgDeviation < bestAvgDeviation && testMaxDeviation < bestMaxDeviation) {
					bestAvgDeviation = testAvgDeviation;
					bestMaxDeviation = testMaxDeviation;
					bestTimeToSwitchOn = time;
				}
				
			}
			
			
			if (bestTimeToSwitchOn > -1) {
				home.cooler[bestTimeToSwitchOn] = true;
				home.updateInternalTemperature();
			}

			iteration++;
			
		}
		
		home.updateInternalTemperature();
		
	}
	
	public static boolean optimise(Home home, List<Integer> constrainedTimes) {
		
		home.resetCooler();
		
		home.updateInternalTemperature();

		double bestAvgDeviation = Double.MAX_VALUE;
		double bestMaxDeviation = Double.MAX_VALUE;
		
		Home testHome = home.clone();
		
		int bestTimeToSwitchOn = -1;
		
		int iteration = 0;
		
		while (iteration < MAX_ITERATIONS && (home.getAverageTemperatureDeviation() > home.tolerance || home.getMaximumTemperatureDeviation() > home.tolerance)) {

			for (int time = 0; time < home.getTimeSlotCount(); time++) {
				
				if (constrainedTimes.contains(time))
					continue;
				
				System.arraycopy(home.cooler, 0, testHome.cooler, 0, home.cooler.length);
				
				testHome.cooler[time] = true;

				testHome.updateInternalTemperature();

				double testAvgDeviation = testHome.getAverageTemperatureDeviation();
				double testMaxDeviation = testHome.getMaximumTemperatureDeviation();

				if (testAvgDeviation < bestAvgDeviation && testMaxDeviation < bestMaxDeviation) {
					bestAvgDeviation = testAvgDeviation;
					bestMaxDeviation = testMaxDeviation;
					bestTimeToSwitchOn = time;
				}
				
			}

			if (bestTimeToSwitchOn > -1) {
				home.cooler[bestTimeToSwitchOn] = true;
				home.updateInternalTemperature();
			}
			iteration++;
		}
		
		home.updateInternalTemperature();
		
		return home.isSatisfied();
	}		
	
	
	public static void convergeEndOfDayTemperature(Home home, List<Integer> constrainedTimes) {
		
		for (int i = 0; i < 5; i++) {
			home.internalTemp[0] = home.internalTemp[home.internalTemp.length-1];
			optimise(home, constrainedTimes);
		}
		
	}
	
	
	public static void convergeEndOfDayTemperature(Home home) {
		
		for (int i = 0; i < 5; i++) {
			optimise(home);
		}
		
	}	

	
	public static void main(String[] args) {
		
		int timeResolution = 10;
		
		final Home h = new Home(1, timeResolution);
		h.randomTemp();
		
		h.setPoint = 23;
		h.tolerance = 1;
		
		h.comfortPeriodStart = 12 * 60 / timeResolution;
		h.comfortPeriodEnd = 14 * 60 / timeResolution;
		
		for (int i = 0; i < h.getTimeSlotCount(); i++) {
			h.externalTemp[i] = 37 + Math.sin(i^2);
		}
		
//		long t0 = new Date().getTime();
		
		GreedyOptimiser.optimise(h);
		
//		long t1 = new Date().getTime();
		
//		System.out.println((t1-t0)/1000D);
		
	}
	
}
