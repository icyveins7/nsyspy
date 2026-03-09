# Just a dict with an added runtime dynamic attribute
# so we can access the enum-like values e.g.
# e.CUDA_KERNEL_LAUNCH_TYPE_REGULAR == 1
class EnumIdNameLabel(dict):
    def __init__(self, *args, alertNonDefaults: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self._alertNonDefaults = alertNonDefaults

    def setNameToId(self, name: str, id: int):
        if self._alertNonDefaults:
            if not hasattr(self, name):
                print(f"WARNING: {name} not typically found in enum")
            elif getattr(self, name) != id:
                print(f"WARNING: {name} does not match typical value")
        setattr(self, name, id)

# List all of them for type hinting

class EnumCudaKernelLaunchType(EnumIdNameLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.CUDA_KERNEL_LAUNCH_TYPE_UNKNOWN = 0
        self.CUDA_KERNEL_LAUNCH_TYPE_REGULAR = 1
        self.CUDA_KERNEL_LAUNCH_TYPE_COOPERATIVE_SINGLE_DEVICE = 2
        self.CUDA_KERNEL_LAUNCH_TYPE_COOPERATIVE_MULTI_DEVICE = 3
