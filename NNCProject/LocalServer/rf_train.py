from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
import pandas as pd
import pickle

x = pickle.load(open('x.con','rb'))
y = pickle.load(open('y.con', 'rb'))
x_array = np.array(x)
y_array = np.array(y)

rf = RandomForestRegressor(n_jobs=-1, n_estimators=40)
rf.fit(x_array, y_array)
pickle.dump(rf, open('rf_estimator.pickle','wb'))