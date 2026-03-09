from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .analysis import NsysSqlite, CuptiActivityKindKernel

import dataclasses

@dataclasses.dataclass
class Stream:
    streamId: int
    hwId: int
    vmId: int
    processId: int
    contextId: int
    priority: int
    flag: int


    # @staticmethod
    # def filterKernels(kernels: list[CuptiActivityKindKernel]) -> dict[int, CuptiActivityKindKernel]:
    #     kv = dict()
    #     for k in kernels:
    #         if k.streamId not in kv:
    #             kv[k.streamId] = list()
    #         kv[k.streamId].append(k)
    #     return kv
