from .analysis import CuptiActivityKindKernel

import dataclasses
from enum import IntEnum
from math import inf

class SMResourceLimitation(IntEnum):
    NONE = 0
    THREADS = 1
    REGISTERS = 2
    SHARED_MEMORY = 3
    # WARPS = 4 # unnecessary, threads is always an exact factor

@dataclasses.dataclass
class ComputeCapability:
    max_resident_blocks_per_sm: int
    max_resident_threads_per_sm: int
    max_registers_per_sm: int
    max_shmem_per_sm: int
    # max_resident_warps_per_sm: int

class CC75(ComputeCapability):
    def __init__(self):
        self.max_resident_blocks_per_sm = 16
        # self.max_resident_warps_per_sm = 32
        self.max_resident_threads_per_sm = 1024
        self.max_registers_per_sm = 65536
        self.max_shmem_per_sm = 65536

class CC86(ComputeCapability):
    def __init__(self):
        self.max_resident_blocks_per_sm = 16
        # self.max_resident_warps_per_sm = 48
        self.max_resident_threads_per_sm = 1536
        self.max_registers_per_sm = 65536
        self.max_shmem_per_sm = 102400

class CC89(ComputeCapability):
    def __init__(self):
        self.max_resident_blocks_per_sm = 24
        # self.max_resident_warps_per_sm = 48
        self.max_resident_threads_per_sm = 1536
        self.max_registers_per_sm = 65536
        self.max_shmem_per_sm = 102400

@dataclasses.dataclass
class Device:
    name: str
    ver_major: int
    ver_minor: int
    compute_capability: ComputeCapability
    num_sms: int

    @property
    def cc(self) -> ComputeCapability:
        return self.compute_capability

    def maxKernelBlksPerSm(self, kernel: CuptiActivityKindKernel) -> tuple[float, SMResourceLimitation]:
        threads_per_blk = kernel.threads_per_blk
        warps_per_blk = threads_per_blk // 32 + threads_per_blk % 32 != 0
        registers_per_blk = kernel.registersPerThread * threads_per_blk
        shmem_per_blk = kernel.staticSharedMemory + kernel.dynamicSharedMemory

        numBlocksThatFit_byThreads = self.cc.max_resident_threads_per_sm // threads_per_blk
        numBlocksThatFit_byRegisters = self.cc.max_registers_per_sm // registers_per_blk
        numBlocksThatFit_byShmem = self.cc.max_shmem_per_sm // shmem_per_blk if shmem_per_blk > 0 else inf
        # numBlocksThatFit_byWarps = self.cc.max_resident_warps_per_sm // warps_per_blk

        numBlocksThatFit = numBlocksThatFit_byThreads
        limitedBy = SMResourceLimitation.THREADS

        if numBlocksThatFit_byRegisters < numBlocksThatFit:
            numBlocksThatFit = numBlocksThatFit_byRegisters
            limitedBy = SMResourceLimitation.REGISTERS

        if numBlocksThatFit_byShmem < numBlocksThatFit:
            numBlocksThatFit = numBlocksThatFit_byShmem
            limitedBy = SMResourceLimitation.SHARED_MEMORY

        # if numBlocksThatFit_byWarps < numBlocksThatFit:
        #     numBlocksThatFit = numBlocksThatFit_byWarps
        #     limitedBy = SMResourceLimitation.WARPS

        if numBlocksThatFit * threads_per_blk == self.cc.max_resident_threads_per_sm:
            limitedBy = SMResourceLimitation.NONE

        return numBlocksThatFit, limitedBy

    def theoreticalOccupancy(self, kernel: CuptiActivityKindKernel) -> tuple[float, SMResourceLimitation]:
        # TODO: add docstring that notes that this is an upper bound
        # Matches the nsys value
        numBlocksThatFit, limitedBy = self.maxKernelBlksPerSm(kernel)
        occ = numBlocksThatFit * kernel.threads_per_blk / self.cc.max_resident_threads_per_sm
        return occ, limitedBy

    def launchOccupancy(self, kernel: CuptiActivityKindKernel) -> float:
        # TODO: add docstring that notes that this is the occupancy based on the launch grid
        numBlocksThatFit, _ = self.maxKernelBlksPerSm(kernel)
        # TODO: kinda ugly, refactor so we don't recalc things..
        if kernel.totalBlocks > numBlocksThatFit * self.num_sms:
            return self.theoreticalOccupancy(kernel)[0] # can only go up to the theoretical
        else:
            return kernel.totalBlocks * kernel.threads_per_blk / (self.cc.max_resident_threads_per_sm * self.num_sms)

class A10(Device):
    def __init__(self):
        self.name = "A10"
        self.ver_major = 8
        self.ver_minor = 6
        self.compute_capability = CC86()
        self.num_sms = 72




