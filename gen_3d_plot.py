from cProfile import label
from tkinter import font
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt

show = True
save = False

fpath_c = './testdata/pos_modified_for_plotting/Mukisano_cam_POS_AO_RSG.txt'
fpath_o = './testdata/pos_modified_for_plotting/Mukisano_Objects_POS_AO_RSG.txt'
fc = open(fpath_c, 'r')
fo = open(fpath_o, 'r')

# get cam coordinates
cX, cY, cZ, clabels = ([] for i in range(4))
for line in fc.readlines()[1:]:
    pos = line.rstrip().split(' ')
    cX.append(float(pos[1]))
    cY.append(float(pos[2]))
    cZ.append(float(pos[3]))
    clabels.append(pos[0])

# cam point color
ccolor = 'firebrick' # orangered firebrick darkorange

# get object coordinates
oX, oY, oZ, olabels = ([] for i in range(4))
for line in fo.readlines()[1:]:
    pos = line.rstrip().split(' ')
    oX.append(float(pos[1]))
    oY.append(float(pos[2]))
    oZ.append(float(pos[3]))
    olabels.append(pos[0])

# object point & plot color
ocolor = 'blue' # steelblue goldenrod darkgoldenrod
plotocolor = 'lightsteelblue' 

# --------------------- plot 3D
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
#plt.title('Data acquisition 3D view') # Title of the plot
ax.set_xlabel("x-axis") # fontsize = 12
ax.set_ylabel("y-axis")
ax.set_zlabel("z-axis")
plt.rcParams.update({'font.size': 8})
plt.tick_params(labelsize=8)

# plot 3D cam
ax.scatter3D(cX, cY, cZ, color=ccolor)
for x,y,z,i in zip(cX,cY,cZ,range(len(cX))):
    ax.text(x, y, z, clabels[i])

# plot 3D objects
ax.scatter3D(oX, oY, oZ, color=ocolor)
ax.plot(oX, oY, oZ, color=plotocolor)
for x,y,z,i in zip(oX,oY,oZ,range(len(oX))):
    ax.text(x, y, z, olabels[i])

permutation = [7, 4, 5, 6, 1, 0, 3, 2]
X=[oX[i] for i in permutation]
Y=[oY[i] for i in permutation]
Z=[oZ[i] for i in permutation]
ax.plot(X, Y, Z, color=plotocolor)

# show/save
if save:
    plt.savefig('plot_3d.png', dpi=800, bbox_inches='tight') # dpi=300
if show:
    plt.gcf().set_dpi(300)
    plt.show()