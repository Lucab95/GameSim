from scipy.stats import norm,poisson

class distribution:
    def __init__(self, mu=10):
        self.mu = mu
        # self.data = norm.rvs(loc=0, scale=1,size=1000)
        self.data = poisson.rvs(loc=0, mu=self.mu, size=5000)
        self.count = 0

    def getNext(self):
        next = self.data[self.count]
        if next < 1:
            next = 1
        self.count +=1
        if self.count == 5000:
            self.count = 0
            self.data = poisson.rvs(loc=0, mu=self.mu, size=5000)
        return next

    def getCount(self):
        return self.count