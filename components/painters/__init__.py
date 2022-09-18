from .painter import Painter

def painter_factory(private: bool):
    """Given the private parameter it returns a PrivatePainter or SimplePainter"""
    painter = None
    if private:
        from .private_painter import PrivatePainter
        painter = PrivatePainter()
    else:
        from .simple_painter import SimplePainter
        painter = SimplePainter()
    return painter