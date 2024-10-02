from App.helpers import env
from config import ROOT

__CONFIG__ = {
    # Proto yaml file path
    "proto_file_path": env("PROTO_FILE_PATH", f"{ROOT}/proto.yaml"),

    # Proto max packet size
    "max_packet_size": env("PROTO_MAX_PACKET_SIZE", 1024 * 16),
}
