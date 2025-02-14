import pyfastchem
import numpy as np
import os
from save_output import saveChemistryOutput, saveMonitorOutput, saveChemistryOutputPandas, saveMonitorOutputPandas
import matplotlib.pyplot as plt
from astropy import constants as const

#input values for temperature (in K) and pressure (in bar)
#we only use a single values here
temperature_single = 1000
pressure_single = 1

#the range of C/O ratios we want to calculate the chemistry for
c_to_o = np.linspace(0.1, 10, 100)


#define the directory for the output
#here, we currently use the standard one from FastChem
output_dir = '../output'



#the chemical species we want to plot later
#note that the standard FastChem input files use the Hill notation
plot_species = ['H2O1', 'C1O2', 'C1O1', 'C1H4', 'H3N1', 'C2H2']
#for the plot lables, we therefore use separate strings in the usual notation
plot_species_lables = ['H2O', 'CO2', 'CO', 'CH4', 'NH3', 'C2H2']


#create a FastChem object
#it needs the locations of the element abundance and equilibrium constants files
#these locations have to be relative to the one this Python script is called from
fastchem = pyfastchem.FastChem('../input/element_abundances_solar.dat', '../input/logK.dat', 1)


#we could also create a FastChem object by using the parameter file
#note, however, that the file locations in the parameter file are relative
#to the location from where this Python script is called from
#fastchem = pyfastchem.FastChem('../input/parameters.dat', 1)



#allocate the data for the output
nb_points = c_to_o.size

number_densities = np.zeros((nb_points, fastchem.getSpeciesNumber()))
total_element_density = np.zeros(nb_points)
mean_molecular_weight = np.zeros(nb_points)
element_conserved = np.zeros((nb_points, fastchem.getElementNumber()), dtype=int)
fastchem_flags = np.zeros(nb_points, dtype=int)
nb_chemistry_iterations = np.zeros(nb_points, dtype=int)

temperature = np.zeros(nb_points)
pressure = np.zeros(nb_points)


#make a copy of the solar abundances from FastChem
solar_abundances = np.array(fastchem.getElementAbundances())


#we need to know the indices for O and C from FastChem
index_C = fastchem.getSpeciesIndex('C')
index_O = fastchem.getSpeciesIndex('O')


#loop over the C/O ratios
#since we constantly change the element abundances, we have to call FastChem separately each time
for i in range(0, c_to_o.size):
  element_abundances = np.copy(solar_abundances)
  
  #set the C abundance as a function of the C/O ratio
  element_abundances[index_C] = element_abundances[index_O] * c_to_o[i]

  fastchem.setElementAbundances(element_abundances)

  #create the input and output structures for FastChem
  input_data = pyfastchem.FastChemInput()
  output_data = pyfastchem.FastChemOutput()

  input_data.temperature = [temperature_single]
  input_data.pressure = [pressure_single]

  fastchem_flag = fastchem.calcDensities(input_data, output_data)
  print("FastChem reports:", pyfastchem.FASTCHEM_MSG[fastchem_flag])
  
  #copy the FastChem input and output into the pre-allocated arrays
  temperature[i] = input_data.temperature[0]
  pressure[i] = input_data.pressure[0]


  number_densities[i,:] = np.array(output_data.number_densities[0])

  total_element_density[i] = output_data.total_element_density[0]
  mean_molecular_weight[i] = output_data.mean_molecular_weight[0]
  element_conserved[i,:] = output_data.element_conserved[0]
  fastchem_flags[i] = output_data.fastchem_flag[0]
  nb_chemistry_iterations[i] = output_data.nb_chemistry_iterations[0]



#total gas particle number density from the ideal gas law 
gas_number_density = pressure*1e6 / (const.k_B.cgs * temperature)



#check if output directory exists
#create it if it doesn't
os.makedirs(output_dir, exist_ok=True)


#save the monitor output to a file
#we add an additional output column for the C/O ratio
saveMonitorOutput(output_dir + '/monitor.dat', 
                  temperature, pressure, 
                  element_conserved,
                  fastchem_flags,
                  nb_chemistry_iterations,
                  total_element_density,
                  mean_molecular_weight,
                  fastchem,
                  c_to_o, 'C/O')


#this saves the output of all species
#we add an additional column for the C/O ratio
saveChemistryOutput(output_dir + '/chemistry.dat', 
                    temperature, pressure,
                    total_element_density, 
                    mean_molecular_weight, 
                    number_densities,
                    fastchem, 
                    None, 
                    c_to_o, 'C/O')


#save the monitor output to a file
#here, the data is saved as a pandas DataFrame inside a pickle file
#we add an additional output column for the metallicity
# saveMonitorOutputPandas(output_dir + '/monitor.pkl', 
#                   temperature, pressure, 
#                   element_conserved,
#                   fastchem_flags,
#                   nb_chemistry_iterations,
#                   total_element_density,
#                   mean_molecular_weight,
#                   fastchem,
#                   c_to_o, 'C/O')


#this would save the output of all species
#here, the data is saved as a pandas DataFrame inside a pickle file
# saveChemistryOutputPandas(output_dir + '/chemistry.pkl', 
#                     temperature, pressure,
#                     total_element_density, 
#                     mean_molecular_weight, 
#                     number_densities,
#                     fastchem, 
#                     None, 
#                     c_to_o, 'C/O')



#check the species we want to plot and get their indices from FastChem
plot_species_indices = []
plot_species_symbols = []

for i, species in enumerate(plot_species):
  index = fastchem.getSpeciesIndex(species)

  if index != pyfastchem.FASTCHEM_UNKNOWN_SPECIES:
    plot_species_indices.append(index)
    plot_species_symbols.append(plot_species_lables[i])
  else:
    print("Species", species, "to plot not found in FastChem")


#and plot...
for i in range(0, len(plot_species_symbols)):
  plt.plot(c_to_o, number_densities[:, plot_species_indices[i]]/gas_number_density)

plt.yscale('log')

plt.ylabel("Mixing ratios")
plt.xlabel("C/O")
plt.legend(plot_species_symbols)

plt.show()

#we could also save the figure as a pdf
#plt.savefig(output_dir + '/fastchem_c_to_o_fig.pdf')