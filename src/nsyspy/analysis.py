import sqlite3 as sq
import sew
from sew.condition import Condition
import dataclasses

@dataclasses.dataclass
class CuptiActivityKindKernel:
    """
    Dataclass representing a row in the CUPTI_ACTIVITY_KIND_KERNEL table.
    This is probably the most pertinent table in GPU kernel benchmarks.
    """
    start: int
    end: int
    deviceId: int
    contextId: int
    greenContextId: int
    streamId: int
    correlationId: int
    globalPid: int
    demangledName: str
    shortName: str
    mangledName: str
    launchType: int
    cacheConfig: int
    registersPerThread: int
    gridX: int
    gridY: int
    gridZ: int
    blockX: int
    blockY: int
    blockZ: int
    staticSharedMemory: int
    dynamicSharedMemory: int
    localMemoryPerThread: int
    localMemoryTotal: int
    gridId: int
    sharedMemoryExecuted: int
    graphNodeId: int
    sharedMemoryLimitConfig: int
    # qmdBulkReleaseDone: int
    # qmdPreexitDone: int
    # qmdLastCtaDone: int
    # graphId: int
    # clusterX: int
    # clusterY: int
    # clusterZ: int
    # clusterSchedulingPolicy: int
    # maxPotentialClusterSize: int
    # maxActiveClusters: int

    def duration(self) -> int:
        return self.end - self.start

    def grid(self) -> tuple[int, int, int]:
        return (self.gridX, self.gridY, self.gridZ)

    def blocks(self) -> tuple[int, int, int]:
        return (self.blockX, self.blockY, self.blockZ)

    # def clusters(self) -> tuple[int, int, int]:
    #     return (self.clusterX, self.clusterY, self.clusterZ)


class NsysSqlite(sew.Database):
    def __init__(self, dbfilepath: str):
        super().__init__(dbfilepath)

    @property
    def path(self) -> str:
        return self.dbpath

    def findStringIdsContaining(self, stringlist: list[str]):
        condition = [
            f"(value LIKE '%{string}%')"
            for string in stringlist
        ]
        condition = " OR ".join(condition)
        self['StringIds'].select(
            ["id", "value"],
            condition)
        stringmap = {row['id']: row['value'] for row in self.fetchall()}
        return stringmap

    def findStringMatchingId(self, id: int):
        self['StringIds'].select("value", f"id = {id}")
        return str(self.fetchone())

    def getKernels(
        self,
        viaShortNames: str | list[str] | None = None,
        viaDemangledNames: str | list[str] | None = None,
        viaMangledNames: str | list[str] | None = None
    ):
        # Try in order
        if viaShortNames is not None:
            viaShortNames = [viaShortNames] if isinstance(viaShortNames, str) else viaShortNames
            idstringmap = self.findStringIdsContaining(viaShortNames)
            filterColumn = "shortName"
        elif viaDemangledNames is not None:
            viaDemangledNames = [viaDemangledNames] if isinstance(viaDemangledNames, str) else viaDemangledNames
            idstringmap = self.findStringIdsContaining(viaDemangledNames)
            filterColumn = "demangledName"
        elif viaMangledNames is not None:
            viaMangledNames = [viaMangledNames] if isinstance(viaMangledNames, str) else viaMangledNames
            idstringmap = self.findStringIdsContaining(viaMangledNames)
            filterColumn = "mangledName"
        else:
            raise ValueError("Must provide at least one of viaShortName, viaDemangledName, viaMangledName")

        self['CUPTI_ACTIVITY_KIND_KERNEL'].select(
            "*",
            [str(Condition(filterColumn).IN([str(i) for i in idstringmap]))]
        )

        rows = self.fetchall()
        # Parse into dataclass
        kernels = [
            CuptiActivityKindKernel(
                start=row['start'],
                end=row['end'],
                deviceId=row['deviceId'],
                contextId=row['contextId'],
                greenContextId=row['greenContextId'],
                streamId=row['streamId'],
                correlationId=row['correlationId'],
                globalPid=row['globalPid'],
                demangledName=self.findStringMatchingId(row['demangledName']),
                shortName=self.findStringMatchingId(row['shortName']),
                mangledName=self.findStringMatchingId(row['mangledName']),
                launchType=row['launchType'],
                cacheConfig=row['cacheConfig'],
                registersPerThread=row['registersPerThread'],
                gridX=row['gridX'],
                gridY=row['gridY'],
                gridZ=row['gridZ'],
                blockX=row['blockX'],
                blockY=row['blockY'],
                blockZ=row['blockZ'],
                staticSharedMemory=row['staticSharedMemory'],
                dynamicSharedMemory=row['dynamicSharedMemory'],
                localMemoryPerThread=row['localMemoryPerThread'],
                localMemoryTotal=row['localMemoryTotal'],
                gridId=row['gridId'],
                sharedMemoryExecuted=row['sharedMemoryExecuted'],
                graphNodeId=row['graphNodeId'],
                sharedMemoryLimitConfig=row['sharedMemoryLimitConfig'],
                # qmdBulkReleaseDone=row['qmdBulkReleaseDone'],
                # qmdPreexitDone=row['qmdPreexitDone'],
                # qmdLastCtaDone=row['qmdLastCtaDone'],
                # graphId=row['graphId'],
                # clusterX=row['clusterX'],
                # clusterY=row['clusterY'],
                # clusterZ=row['clusterZ'],
                # clusterSchedulingPolicy=row['clusterSchedulingPolicy'],
                # maxPotentialClusterSize=row['maxPotentialClusterSize'],
                # maxActiveClusters=row['maxActiveClusters']
            )
            for row in rows
        ]
        return kernels


