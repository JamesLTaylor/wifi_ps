import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import minimize


def func(x, K, x0, d):
    y = K / np.sqrt((x-x0)**2 + d**2 + 0.1)
    return y
    
def func2(x, K, d):
    x0 = 0.21
    y = K / np.sqrt((x-x0)**2 + d**2 + 0.00001)
    return y    
    
def func3(x, K, x0, ml, mr):
    y = np.zeros(x.shape)
    y[x<=x0] = K- (x[x<=x0]-x0)*ml
    y[x>x0] = K- (x0-x[x>x0])*mr    
    return y      
    
def func4(x, K, ml, mr):
    x0 = 0.21
    y = np.zeros(x.shape)
    y[x<=x0] = K- (x[x<=x0]-x0)*ml
    y[x>x0] = K- (x0-x[x>x0])*mr    
    return y     
    
def func5(x, K, x0, al, bl, ar, br):
    y = np.zeros(x.shape)
    y[x<=x0] = K + al*(( x0 - x[x<=x0] )**2) - bl*( x0 - x[x<=x0] )
    y[x>x0]  = K + ar*(( x[x>x0]- x0  )**2) -  br*( x[x>x0]- x0  )    
    return y
    
def func5_res(p, x, y):
    K, x0, al, bl, ar, br = p
    y_model = func5(x, K, x0, al, bl, ar, br)
    res = np.sum((y-y_model)**2)
    return res



mac_id = 81
x = np.array([p["frac"] for p in original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])
y = np.array([p["stats"][mac_id][1] for p in original_points if p["stats"].has_key(mac_id) and p.has_key("frac")])

x0 = [-50, 0.5, 0, 0, 50, 50]
bounds = ((-80, 0),
            (0, 1),
            (0.1, None),
            (0, None),
            (0.1, None),
            (0, None))
            
res = minimize(func5_res, x0, args=(x,y), method = "L-BFGS-B", bounds = bounds, options={'gtol': 1e-6, 'disp': True})
res.x
x2 = np.arange(0,1,1.0/100)
y2 = func5(x2,*res.x)
plt.plot(x2,y2)
plt.plot(x,y,'.')

"""
popt, pcov = curve_fit(func5, x, y, [-50, 0.21, 0, 0, 50, 50])
x2 = np.arange(0,1,1.0/100)
y2 = func5(x2,*popt)
plt.plot(x2,y2)
plt.plot(x,y,'.')
"""