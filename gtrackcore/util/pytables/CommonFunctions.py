import os
from gtrackcore.core.Config import Config


def genome_and_trackname(filename):
    genome_track_name_list = filename.split(Config.PROCESSED_DATA_PATH)[1][1:].split(os.sep)
    genome = genome_track_name_list[0]
    track_name = genome_track_name_list[1:-1]
    return genome, track_name