from traitlets.config.configurable import LoggingConfigurable
from traitlets import Unicode


__author__ = 'Manfred Minimair <manfred@minimair.org>'


class LaunchConfig(LoggingConfigurable): 

    gate_tunnel_user = Unicode('chconnect', config=True,
                               help='ssh user name on gate for tunnel to kernel')

    kernel_gate = Unicode('in.chgate.net', config=True,
                          help='gate ssh server that can see host and\
 from which to start kernel sessions; gate and host must have\
 idential user names and matching ssh keys to log in for starting the kernel')

    def __init__(self):
        super(LaunchConfig, self).__init__()

