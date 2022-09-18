from .model import Model

def model_factory(
    multiple: bool, gpu_enable: bool, model_path: str, proto_path: str
) -> Model:
    """Given the requested parameters it return the right model for the job."""
    model = None
    if multiple:
        from .model_multiple import MultipleDetectionsModel
        model = MultipleDetectionsModel(model_path, proto_path)
    else:
        from .model_single import SingleDetectionModel
        model = SingleDetectionModel(model_path, proto_path)
    model.init_net()
    if gpu_enable:
        model.enable_gpu()
    return model
