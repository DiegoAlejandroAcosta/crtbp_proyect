from scipy.integrate import odeint
import numpy as np

def CRTBP(Y,t,alpha):
    x,y,z,vx,vy,vz = Y
    r1 = np.sqrt(x**2+2*x*alpha+alpha**2+y**2+z**2)
    mmur1 = (1-alpha)/(r1**3)

    r2 = np.sqrt(x**2+y**2+z**2-2*x*(1-alpha)+(1-alpha)**2)
    mur2 = alpha/r2**3

    ax = 2*vy+x-mmur1*(x+alpha)-mur2*(x-(1-alpha))
    ay = -2*vx+y-mmur1*y-mur2*y
    az = -mmur1*z-mur2*z
    return [vx,vy,vz,ax,ay,az]

def database_orbit(orbit_trial,alpha,N = 1e6):
    x1 = orbit_trial["x(1)"]
    x2 = orbit_trial["x(2)"]
    x3 = orbit_trial["x(3)"]
    x4 = orbit_trial["x(4)"]
    x5 = orbit_trial["x(5)"]
    x6 = orbit_trial["x(6)"]

    Y0 = np.array([x1,x2,x3,x4,x5,x6])

    #Se pasa al sistema COM
    Y0[0] += (1-alpha)
    period = orbit_trial["period"]
    t = np.linspace(0,period,int(N))

        #Se pasa al COM
    Yrot = odeint(CRTBP,y0=Y0,t = t,args= (alpha,),atol = 1e-10,rtol =1e-10,mxstep=1000)
    IS = {"Y0":Y0,"alpha":alpha,"P":period,"t":t}

    return Yrot,IS
