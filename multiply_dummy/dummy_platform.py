from multiply_inference_engine import dummy_inference_engine
from multiply_data_access.aux_data_access import dummy_aux_data_provider
from multiply_prior_engine import dummy_prior_engine
from multiply_data_access.brdf_access import dummy_brdf_archive
from multiply_forward_operators import dummy_optical_forward_operator
from multiply_forward_operators import dummy_sar_forward_operator
from multiply_emulation_engine import dummy_emulation_engine
from multiply_high_resolution_pre_processing import dummy_high_resolution_pre_processor
from multiply_sar_pre_processing import dummy_sar_pre_processor
from multiply_data_access.coarse_res_data_access import dummy_coarse_res_data_provider
from multiply_data_access.high_res_data_access import dummy_high_res_data_provider
from multiply_data_access.sar_data_access import dummy_sar_data_access_provider
from multiply_coarse_resolution_pre_processing import dummy_coarse_resolution_pre_processor
from multiply_visualization import dummy_visualization_component
from multiply_post_processing import dummy_post_processor


from configuration import Configuration
from state import TargetState


import datetime

# specifiy user based configuration
t1 = datetime.datetime(1998,1,1)
t2 = datetime.datetime(2000,12,31)
ul = {'lon' : 11.2, 'lat' : 48.0}
lr = {'lon' : 12.2, 'lat' : 45.0}

tstate = TargetState(state={'lai':True, 'sm':False})


config = Configuration(region={'ul' : ul, 'lr' : lr}, time_start=t1, time_stop=t2, tstate=tstate)   



# run the system
aux_data_constraints = []
aux_data_provider = dummy_aux_data_provider.DummyAuxDataProvider(config)  # config always used when new instances are created
some_aux_data = aux_data_provider.read_aux_data(aux_data_constraints)
prior_engine = dummy_prior_engine.DummyPriorEngine()
prior_1 = prior_engine.create_prior(some_aux_data)
# this command is expected to be executed internally whenever a prior is created
prior_engine.save_prior(prior_1)
prior_id = 'My prior'
prior_2 = prior_engine.get_prior(prior_id)

brdf_archive = dummy_brdf_archive.DummyBRDFArchive(config)
brdf_archive.has_brdf_descriptor(config)
brdf_descriptor = brdf_archive.get_brdf_descriptor()
coarse_res_data_constraints = []
coarse_res_provider = dummy_coarse_res_data_provider.DummyCoarseResDataProvider(config)
coarse_res_data = coarse_res_provider.get_data(config, coarse_res_data_constraints)
coarse_resolution_pre_processor = dummy_coarse_resolution_pre_processor.DummyCoarseResolutionPreProcessor()
brdf_descriptor = coarse_resolution_pre_processor.pre_process(coarse_res_data)

high_res_data_constraints = []
high_res_data_provider = dummy_high_res_data_provider.DummyHighResDataProvider()
high_res_data = high_res_data_provider.get_data(config, high_res_data_constraints)

sar_data_constraints = []
sar_data_provider = dummy_sar_data_access_provider.DummySARDataAccessProvider()
sar_data = sar_data_provider.get_data(config, sar_data_constraints)

high_res_pre_processor = dummy_high_resolution_pre_processor.DummyHighResolutionPreProcessor()
high_res_sdr = high_res_pre_processor.pre_process(brdf_descriptor, high_res_data)

sar_pre_processor = dummy_sar_pre_processor.DummySARPreProcessor()
grd_sar_data = sar_pre_processor.pre_process(sar_data)

optical_forw_operator_1 = dummy_optical_forward_operator.DummyOpticalForwardOperator()
sar_forw_operator_1 = dummy_sar_forward_operator.DummySARForwardOperator()

emulation_engine = dummy_emulation_engine.DummyEmulationEngine()
optical_forw_operator_emulator_1 = emulation_engine.emulate_optical_forward_operator(dummy_optical_forward_operator)
sar_forw_operator_emulator_1 = emulation_engine.emulate_sar_forward_operator(dummy_sar_forward_operator)
optical_forw_operator_emulator_2 = emulation_engine.get_optical_forward_operator_emulator('optical_forward_operator_id')
sar_forw_operator_emulator_2 = emulation_engine.get_sar_forward_operator_emulator('sar_forward_operator_id')

# harmonize data
inference_engine = dummy_inference_engine.DummyInferenceEngine()
high_res_biophysical_params = inference_engine.infer(brdf_descriptor, high_res_sdr, grd_sar_data, prior_2,
                               optical_forw_operator_emulator_2, sar_forw_operator_emulator_1)

#from here on: use of inferred products

vis_component = dummy_visualization_component.DummyVisualizationComponent()
vis_component.visualize(high_res_biophysical_params)

# do we need to define an interface here?
post_processor = dummy_post_processor.DummyPostProcessor()
post_processor.post_process(high_res_biophysical_params)

# dummy_assimilation_engine.assimilate()



