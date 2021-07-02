import numpy as np
import math

def derivative_CAL(curve):

    newcurve = curve.drop('256',axis=1)

    y = np.diff(newcurve,axis=-1)
    y = 1.0*y/y.sum(axis=1,keepdims=True)
    x = np.array(range(len(y.transpose())))
    
    mean = np.inner(x+0.5,y)

    sigma2 = 0
    # (x+0.5)**2*y
    sigma2 += np.inner(np.square(x+0.5),y)
    # 2*(x+0.5)*mu
    sigma2 += np.inner(x+0.5,y)*(-2)*mean
    # mu**2
    sigma2 += np.square(mean)

    sigma = np.sqrt(sigma2)    

    # failures                                                                                                    
    failed = np.where(np.isnan(sigma))
    mean[failed] = -100
    sigma[failed] = -100

    return mean, sigma

def derivative_THR(curve,n_pulse=1000):

    newcurve = curve.drop('256',axis=1)

    locations = np.where( ( newcurve > n_pulse) & (abs(newcurve - n_pulse) < np.sqrt(n_pulse)),
                         range(len(newcurve.transpose())) - np.full(len(newcurve.transpose()),n_pulse),
                         range(len(newcurve.transpose())))

    flat_point = np.argmin(locations,axis=1)
    flat_point = np.repeat(np.argmin(locations,axis=1),len(newcurve.transpose())).reshape(newcurve.shape)

    curve_corrected = np.where(locations < flat_point + 5, 1000, newcurve)

    y = -1*np.diff(curve_corrected,axis=1)

    y = 1.0*y/y.sum(axis=1,keepdims=True)
    x = np.array(range(len(y.transpose())))

    mean = np.inner(x+0.5,y)

    sigma2 = 0
    # (x+0.5)**2*y                                                                                                     
    sigma2 += np.inner(np.square(x+0.5),y)
    # 2*(x+0.5)*mu                                                                                                     
    sigma2 += np.inner(x+0.5,y)*(-2)*mean
    # mu**2                                                                                                            
    sigma2 += np.square(mean)

    sigma = np.sqrt(sigma2)

    # failures
    failed = np.where(np.isnan(sigma))
    mean[failed] = -100
    sigma[failed] = -100

    return mean, sigma
