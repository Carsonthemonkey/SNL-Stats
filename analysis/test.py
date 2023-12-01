import scipy.stats as stats

def test():
    print("Hello from test.py")
    print(stats.ttest_ind([1,2,3], [4,5,6])) # t-test example
    print(stats.f_oneway([1,2,3], [4,5,6])) # ANOVA example (one-way)

if __name__ == "__main__":
    test()