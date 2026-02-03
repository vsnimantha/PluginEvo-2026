fitness_mode=const.Fitness_Mode.COMPILER  

Make sure when running the gp algorithm configuration is correct, if not it will talk to the wrong server.
Also make sure all the keys are properly passed. Like for an example, adaptive fitness may talk to wrong server with wrong config
Moreover, make sure to check the keys for the compiler testing, for coverage testing is a valid scenario to makesure that program is correct.
For compiler testing this is not the case, therefore be sure to adjust it accordingly.