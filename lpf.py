'''First order low pass filter, takes number of points as parameter

    numpoints is ralated to time constant of the filter as follows
        tau = N * T where T is the sample period
        
'''
 
class LPF():
    def __init__(self, numpoints, init_value):
        assert numpoints == int(numpoints) and numpoints > 0, "numpoints must be an integer >0"
        self.alpha = numpoints/(numpoints + 1.)
        self.beta = 1./(numpoints + 1.)
        self.avg_prev = init_value
 
    def reset(self, value):
        self.avg_prev = value

    def __call__(self, n):
        avg = self.alpha * self.avg_prev + self.beta * n
        self.avg_prev = avg
 
        return avg