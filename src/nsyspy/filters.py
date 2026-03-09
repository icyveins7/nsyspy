from .analysis import CuptiActivityKindKernel

def filterKernelsByStream(kernels: list[CuptiActivityKindKernel]) -> dict[int, CuptiActivityKindKernel]:
    """
    Filters a list of kernels into separate lists corresponding to streams.

    Parameters
    ----------
    kernels : list[CuptiActivityKindKernel]
        Input list of kernels.

    Returns
    -------
    filtered : dict[int, CuptiActivityKindKernel]
        Key is the stream ID, value is the list of kernels for that stream.
        Ordering should be maintained.
    """
    kv = dict()
    for k in kernels:
        if k.streamId not in kv:
            kv[k.streamId] = list()
        kv[k.streamId].append(k)
    return kv
