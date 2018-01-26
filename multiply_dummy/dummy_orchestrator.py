# import subprocess
#
# class DummyOrchestrator(object):
#
#     def run_dummy_code_1(self, multiply_config):
#         # this will download data and populate the MULTIPLY database
#         # download high res, SAR, ancillary data (that is ECMWF) and brdf descriptors
#         data_types = ['S2_MSI_L1C', 'S1_L1C', 'BRDF']
#         subprocess.call(['multiply', 'get_data_urls', '--config', multiply_config,
#                          '--roi', 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
#                          '--start_time', '2017-01-01T12:00:00', '--end_time', '2017-01-05T12:00:00',
#                          '--data_types', data_types,
#                          '--working_dir', './user/home/', # where to store the list with urls
#                          '--download_dir', './user/data/']) # where to locally store data
#
#         # once data for one observation time slot has been downloaded
#         if do_pre_process:  # pre-processing is necessary
#             if is_optical(url):
#                 # again: populate database
#                 subprocess.call(['multiply', 'pre_process_high_res', '--config', multiply_config,
#                                  '--url', 'url', # also use ECMWF, brdf descriptors
#                                  '--output_dir', './user/data/']) # where to store the pre-processed product
#             elif is_sar(url):
#                 # again: populate database
#                 subprocess.call(['multiply', 'pre_process_sar', '--config', multiply_config,
#                              '--url', 'url', '--roi', 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))',
#                              '--output_dir', './user/data/'])  # where to store the pre-processed product
#
#         subprocess.call(['multiply', 'infer', '--config', multiply_config,
#                          '--roi', 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
#                          '--start_time', '2017-01-01T12:00:00', '--end_time', '2017-01-05T12:00:00',
#                          '--spatial_res', '60', '--time_interval', '12h', '--observations', 'urls',
#                          '--output_dir', './user/data/'])
#
#     def run_dummy_code_2(self, multiply_config):
#         # this will download data and populate the MULTIPLY database
#         # download high res, SAR, ancillary data (that is ECMWF) and brdf descriptors
#         data_types = ['S2_MSI_L1C', 'S1_L1C', 'BRDF']
#         subprocess.call(['multiply', 'get_data_urls', '--config', multiply_config,
#                          '--roi', 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
#                                   '--start_time', '2017-01-01T12:00:00', '--end_time', '2017-01-05T12:00:00',
#                          '--data_types', data_types,
#                          '--working_dir', './user/home/',  # where to store the list with urls
#                          '--download_dir', './user/data/'])  # where to locally store data
#         # once data for one observation time slot has been downloaded
#         if do_pre_process:  # pre-processing is necessary
#             if is_optical(url):
#                 # again: populate database
#                 subprocess.call(['multiply', 'pre_process_high_res', '--config', multiply_config,
#                                  '--url', 'url',  # also use ECMWF, brdf descriptors
#                                  '--output_dir', './user/data/'])  # where to store the pre-processed product
#             elif is_sar(url):
#                 # again: populate database
#                 subprocess.call(['multiply', 'pre_process_sar', '--config', multiply_config,
#                                  '--url', 'url', '--roi', 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))',
#                                  '--output_dir', './user/data/'])  # where to store the pre-processed product
#
#         # Inference will happen over a time period
#         # With intervals given by time_grid
#         # e.g.
#         # time_grid = [ "2017-01-01", "2017-01-02"]
#         inference_config, time_grid = define_problem(multiply_config)
#         # x is state vector
#         # c_inv is sparse INVERSE covariance matrix
#         x = None
#         c_inv = None
#
#         for i, time_step in enumerate(time_grid):
#             # First, get the prior information for
#             # current time step
#             x, c_inv = prior_engine(inference_config, time_step, x, c_inv)
#             subprocess.call(['multiply', 'get_prior_information', '--config', multiply_config,
#                              '--time_step', time_step, '--x', x, '--c_inv', c_inv,
#                              '--output_dir', './user/data/']) # where to put a yaml file with new values for x and c_inv
#
#             # Query the observations database
#             observations = query_observations(inference_config, time_step) # how to achieve this?
#             # Inference stage
#             for observation in observations:
#                 # what would be the output of this?
#                 subprocess.call(['multiply', 'infer', '--config', multiply_config,
#                                 '--observation', observation, '--x', x, '--c_inv', c_inv])
#
#             # Propagation stage
#             subprocess.call(['multiply', 'propagate', '--config', multiply_config, # does this have an output?
#                              '--time_step', time_step, '--x', x, '--c_inv', c_inv])
#
#
