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
    rowid: int
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
    qmdBulkReleaseDone: int | None = None
    qmdPreexitDone: int | None = None
    qmdLastCtaDone: int | None = None
    graphId: int | None = None
    clusterX: int | None = None
    clusterY: int | None = None
    clusterZ: int | None = None
    clusterSchedulingPolicy: int | None = None
    maxPotentialClusterSize: int | None = None
    maxActiveClusters: int | None = None

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

    def findStringIdsContaining(self, stringlist: list[str]) -> dict[int, str]:
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

    def findStringMatchingId(self, id: int) -> str:
        self['StringIds'].select("value", f"id = {id}")
        return str(self.fetchone()['value'])

    def getKernelsBetween(
        self,
        start: float | None = None,
        end: float | None = None
    ) -> list[CuptiActivityKindKernel]:
        conditions = []
        if start is not None:
            conditions.append(
                f"start > {start}"
            )
        if end is not None:
            conditions.append(
                f"end < {end}"
            )
        self['CUPTI_ACTIVITY_KIND_KERNEL'].select(
            "rowid, *", conditions
        )
        rows = self.fetchall()
        # Parse into dataclass
        kernels = [CuptiActivityKindKernel(**row) for row in rows]
        return kernels


    def getKernels(
        self,
        viaShortNames: str | list[str] | None = None,
        viaDemangledNames: str | list[str] | None = None,
        viaMangledNames: str | list[str] | None = None
    ) -> list[CuptiActivityKindKernel]:
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
            "rowid, *",
            [str(Condition(filterColumn).IN([str(i) for i in idstringmap]))]
        )

        rows = self.fetchall()
        # Parse into dataclass
        kernels = [CuptiActivityKindKernel(**row) for row in rows]
        return kernels

    def getKernelsAfter(self, kernel: CuptiActivityKindKernel, count: int = 1) -> list[CuptiActivityKindKernel]:
        self["CUPTI_ACTIVITY_KIND_KERNEL"].select(
            "rowid, *",
            [f"rowid > {kernel.rowid}"]
        )
        # sew has no support for LIMIT yet so we just iterate until we reach it
        r = list()
        for _ in range(count):
            r.append(CuptiActivityKindKernel(**self.fetchone()))
        return r

    def getCudaApiCall(self, target):
        if isinstance(target, int):
            correlationId = target

        elif isinstance(target, CuptiActivityKindKernel):
            correlationId = target.correlationId

        else:
            raise TypeError("Must be int or CuptiActivityKindKernel (for now)")

        self["CUPTI_ACTIVITY_KIND_RUNTIME"].select(
            "rowid, *",
            [f"correlationId={correlationId}"]
        )

        apicalls = self.fetchall()

        return apicalls


