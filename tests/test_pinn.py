import PINN_ICE as pinn
import os
import numpy as np
from datetime import datetime
import deepxde as dde
dde.config.set_default_float('float64')
dde.config.disable_xla_jit()

weights = [7, 7, 5, 5, 3, 3, 5];

inputFileName="Helheim_fastflow.mat"
expFileName = "fastflow_CF.exp"

# path for loading data and saving models
repoPath = os.path.dirname(__file__) + "/../examples/"
appDataPath = os.path.join(repoPath, "dataset")
path = os.path.join(appDataPath, inputFileName)
yts =3600*24*365
loss_weights = [10**(-w) for w in weights]
loss_weights[2] = loss_weights[2] * yts*yts
loss_weights[3] = loss_weights[3] * yts*yts

hp = {}
# General parameters
hp["epochs"] = 2
hp["loss_weights"] = loss_weights
hp["learning_rate"] = 0.001
hp["loss_function"] = "MSE"
hp["is_save"] = False

# NN
hp["activation"] = "tanh"
hp["initializer"] = "Glorot uniform"
hp["num_neurons"] = 20
hp["num_layers"] = 6

# data
hp["data_path"] = path

# domain
hp["shapefile"] = os.path.join(repoPath, "dataset", expFileName)
hp["num_collocation_points"] = 9000

# physics
SSA = {}
SSA["scalar_variables"] = {"B":1.26802073401e+08}
hp["equations"] = {"SSA":SSA}

def test_compile_no_data():
    hp["data_size"] = {}
    experiment = pinn.PINN(hp)
    experiment.compile()
    assert experiment.loss_names == ['fSSA1', 'fSSA2']
    assert experiment.param.nn.output_variables == ['u', 'v', 's', 'H', 'C']
    assert experiment.param.nn.output_lb[0]<0.0
    assert experiment.param.nn.output_ub[0]>0.0
    assert experiment.param.nn.output_lb[1]<0.0
    assert experiment.param.nn.output_ub[1]>0.0

def test_save_and_load_setting(tmp_path):
    experiment = pinn.PINN(hp)
    experiment.save_setting(path=tmp_path)
    assert experiment.param.param_dict == experiment.load_setting(path=tmp_path)

def test_train(tmp_path):
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = True
    hp["data_size"] = {"u":4000, "v":4000, "s":4000, "H":4000, "C":None}
    experiment = pinn.PINN(hp)
    experiment.compile()
    experiment.train()
    assert experiment.loss_names == ['fSSA1', 'fSSA2', 'u', 'v', 's', 'H', 'C']

def test_plot(tmp_path):
    hp["save_path"] = str(tmp_path)
    hp["is_save"] = True
    hp["data_size"] = {"u":4000, "v":4000, "s":4000, "H":4000, "C":None}
    experiment = pinn.PINN(hp)
    experiment.compile()
    assert experiment.plot_predictions(X_ref=experiment.model_data.X_dict, sol_ref=experiment.model_data.data_dict, resolution=10) == None
    X_ref = np.hstack((experiment.model_data.X_dict['x'].flatten()[:,None],experiment.model_data.X_dict['y'].flatten()[:,None]))
    assert experiment.plot_predictions(X_ref=X_ref, sol_ref=experiment.model_data.data_dict, resolution=10) == None
