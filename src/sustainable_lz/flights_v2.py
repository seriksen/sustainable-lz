import numpy as np
import pandas as pd
import io
long_cut=2500
interpolate_above=1500
short_haul_factors=pd.read_csv(io.StringIO('''
S,157.86
PLF,0.796
DC,95
CF,0.26
E_CW,1
P_CW,1
B_CW,1.5
F_CW,1.5
EF,3.16
P,0.538
M,3
AF,0.00034
A,11.68
a,0.000007
b,2.775
c,1260.608

'''), header=None)
keys=list(short_haul_factors[0])
vals=list(short_haul_factors[1])
short_haul_factors={k:vals[i] for i,k in enumerate(keys)}
long_haul_factors=pd.read_csv(io.StringIO('''
S,302.58
PLF,0.82
DC,95
CF,0.26
E_CW,1
P_CW,1.5
B_CW,4
F_CW,5
EF,3.16
P,0.538
M,3
AF,0.00034
A,11.68
a,0.00029
b,3.475
c, 3259.691

'''), header=None)
keys=list(long_haul_factors[0])
vals=list(long_haul_factors[1])
long_haul_factors={k:vals[i] for i,k in enumerate(keys)}

class flight_emission_calc_v2:
    def __init__(self,emission_factor=None):
        self.emission_factor=long_haul_factors['M']
        if emission_factor is not None:
            self.emission_factor=emission_factor
            
    def calculate_emission_for_factors(self,factors,distance):
        #caculate kg of CO2
        x=factors['DC']+distance
        E=(factors['a']*x**2+factors['b']*x+factors['c'])/(factors['S']*factors['PLF'])
        E*=(1-factors['CF'])*factors['E_CW']*(factors['EF']*self.emission_factor+factors['P'])
        E+=factors['AF']*x+factors['A']
        return E
    
    def calc_emissions_v2(self,distance):
        #not yet calculating layovers
        if distance>=long_cut:
            return 2*(self.calculate_emission_for_factors(long_haul_factors,distance))/1e3
        elif distance<=interpolate_above:
            return 2*(self.calculate_emission_for_factors(short_haul_factors,distance))/1e3
        else:
            short_haul_co2=self.calculate_emission_for_factors(short_haul_factors,distance)
            long_haul_co2=self.calculate_emission_for_factors(long_haul_factors,distance)
            m=(long_haul_co2-short_haul_co2)/(long_cut-interpolate_above)
            return 2*(m*(distance-interpolate_above)+short_haul_co2)/1e3