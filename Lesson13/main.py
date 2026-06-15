import numpy as np

array_2D= np.array([
                    [1,2,3,4,5],
                    [6,7,8,9,10]
])

print(array_2D)

elemnti = array_2D[0][2]
print(elemnti)
print(array_2D[1][4])

#dimensioni
dimension = array_2D.ndim
print(dimension)

#tipi
shape = array_2D.shape
print(shape)

#madhesia
madheshia = array_2D.size
print(madheshia)
print(array_2D[0])

sub_array = array_2D[:2, :2]
print(sub_array)