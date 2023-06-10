# Import libraries

import numpy as np

import matplotlib.pyplot as plt


origin_x = [0]

origin_y = [0]

 # Directional vectors

sin_x = [0] 

sin_y = [10*(np.sqrt(2))] 

 # Creating plot

plt.quiver(origin_x, origin_y, sin_x, sin_y, color='b', units='xy', scale=1)

plt.title('Single Vector')

 # x-lim and y-lim

plt.xlim(-2, 15)

plt.ylim(-2, 15)

 # Show plot with grid

plt.grid()

plt.show()