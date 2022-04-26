from cProfile import label
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.pyplot as plt

show = False
save = True

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

# --------------------- plot xy
# Adding title, xlabel and ylabel
#plt.title('Data acquisition top view') # Title of the plot
plt.xlabel('x-axis', fontsize = 13) # X-Label
plt.ylabel('y-axis', fontsize = 13) # Y-Label
plt.rcParams.update({'font.size': 8})
plt.tick_params(labelsize=8)

# plot xy cam
plt.scatter(cX, cY, color=ccolor)
for x,y,i in zip(cX,cY,range(len(cX))):
    plt.text(x, y, clabels[i])

# plot xy objects
plt.plot(oX, oY, color=plotocolor)
plt.scatter(oX, oY, color=ocolor)
for x,y,i in zip(oX,oY,range(len(oX))):
    plt.text(x, y, olabels[i])
   
permutation = [7, 4, 5, 6, 1, 0, 3, 2]
X=[oX[i] for i in permutation]
Y=[oY[i] for i in permutation]
plt.plot(X, Y, color=plotocolor)

# show/save
if save:
    plt.savefig('plot_2d_xy.png', dpi=800, bbox_inches='tight') # bbox_inches='tight' format='svg' dpi=300
if show:
    plt.show()

plt.clf()
# --------------------- plot xz 
# Adding title, xlabel and ylabel
#plt.title('Data acquisition top view') # Title of the plot
plt.xlabel('x-axis', fontsize = 13) # X-Label
plt.ylabel('z-axis', fontsize = 13) # Z-Label
plt.rcParams.update({'font.size': 8})
plt.tick_params(labelsize=8)

# plot xy cam
plt.scatter(cX,cZ, color=ccolor)
for x,z,i in zip(cX,cZ,range(len(cX))):
    plt.text(x, z, clabels[i])

# plot xy objects
plt.plot(oX,oZ, color=plotocolor)
plt.scatter(oX,oZ, color=ocolor)
for x,z,i in zip(oX,oZ,range(len(oX))):
    plt.text(x, z, olabels[i])
   
permutation = [6, 7, 4, 5, 2, 1, 0, 3]
X=[oX[i] for i in permutation]
Z=[oZ[i] for i in permutation]
plt.plot(X, Z, color=plotocolor)

# show/save
if save:
    plt.savefig('plot_2d_xz.png', dpi=800, bbox_inches='tight') # bbox_inches='tight' format='svg' dpi=300
if show:
    plt.show()

plt.clf()
# --------------------- plot yz
# Adding title, xlabel and ylabel
#plt.title('Data acquisition top view') # Title of the plot
plt.xlabel('y-axis', fontsize = 13) # Y-Label
plt.ylabel('z-axis', fontsize = 13) # Z-Label
plt.rcParams.update({'font.size': 8})
plt.tick_params(labelsize=8)

# plot xy cam
plt.scatter(cY,cZ, color=ccolor)
for y,z,i in zip(cY,cZ,range(len(cY))):
    plt.text(y, z, clabels[i])

# plot xy objects
plt.plot(oY,oZ, color=plotocolor)
plt.scatter(oY,oZ, color=ocolor)
for x,z,i in zip(oY,oZ,range(len(oY))):
    plt.text(x, z, olabels[i])
   
permutation = [7, 4, 5, 6, 1, 0, 3, 2]
Y=[oY[i] for i in permutation]
Z=[oZ[i] for i in permutation]
plt.plot(Y, Z, color=plotocolor)

# show/save
if save:
    plt.savefig('plot_2d_yz.png', dpi=800, bbox_inches='tight') # bbox_inches='tight' format='svg' dpi=300
if show:
    plt.show()

plt.clf()
# --------------------- plot yz (only cam 7)
# Adding title, xlabel and ylabel
#plt.title('Data acquisition top view') # Title of the plot
plt.xlabel('y-axis', fontsize = 13) # Y-Label
plt.ylabel('z-axis', fontsize = 13) # Z-Label
plt.rcParams.update({'font.size': 8})
plt.tick_params(labelsize=8)

# plot xy cam
plt.scatter(cY,cZ, color='white')
plt.scatter(cY[6], cZ[6], color=ccolor)
plt.text(cY[6], cZ[6], clabels[6])

# plot xy objects
plt.plot(oY,oZ, color=plotocolor)
plt.scatter(oY,oZ, color=ocolor)
for x,z,i in zip(oY,oZ,range(len(oY))):
    plt.text(x, z, olabels[i])
   
permutation = [7, 4, 5, 6, 1, 0, 3, 2]
Y=[oY[i] for i in permutation]
Z=[oZ[i] for i in permutation]
plt.plot(Y, Z, color=plotocolor)

# show/save
if save:
    plt.savefig('plot_2d_yz_cam7.png', dpi=800, bbox_inches='tight') # bbox_inches='tight' format='svg' dpi=300
if show:
    plt.show()