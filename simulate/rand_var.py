import random as r
import math as m

def U(a,b):
    return lambda: r.uniform(0,1)*(b-a) + a

def Exp(lambd):
    u = U(0,1)
    return lambda: -m.log(u())/lambd

def Poisson(lambd):
    def poisson():
        u = U(0,1)
        t = u()
        i = 1
        maxim = m.exp(-lambd)
        while t >= maxim:
            t *= u() 
            i += 1
        return i-1
    return lambda: poisson()

def Normal(mu, sigma):
    return lambda: r.normalvariate(mu, sigma)

