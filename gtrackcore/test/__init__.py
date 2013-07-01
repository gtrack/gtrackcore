from gtrackcore.core.Config import Config

def get_data_path():
    import pkg_resources
    return pkg_resources.resource_filename('gtrackcore', 'data')

def get_data_output_path(data_path=None):
    import os
    
    if not data_path:
        data_path = get_data_path()
    
    return os.path.join(data_path, 'test_output')

def setup_paths():
    import os, shutil
    
    TRACK_NAME_PREFIX = 'GESourceTracks'
    
    data_path = get_data_path()
    gesource_tracks_data_path = os.path.join(data_path, TRACK_NAME_PREFIX)
    data_output_path = get_data_output_path(data_path)
    track_output_path = os.path.join(data_output_path, 'gtrackcore_data')
    testgenome_output_path = os.path.join(track_output_path, 'Original', 'TestGenome')
    gesource_tracks_output_path = os.path.join(testgenome_output_path, TRACK_NAME_PREFIX)
    config_fn = os.path.join(data_output_path, 'gtrackcore_config')

    if not os.path.exists(testgenome_output_path):
        os.makedirs(testgenome_output_path)

    assert os.path.exists(gesource_tracks_data_path)
    if not os.path.lexists(gesource_tracks_output_path):
        os.symlink(gesource_tracks_data_path, gesource_tracks_output_path)

    Config.initialize(configFileName=config_fn, \
                      dataDir=track_output_path)
    
def setup_package():
    pass

def teardown_package():
    import shutil
    data_path = get_data_path()
    data_output_path = get_data_output_path(data_path)
    
    #shutil.rmtree(data_output_path)

setup_paths()