def ResizeYAxis(Default_Size, pitch, ax, DynamicSizing):
    if DynamicSizing:
        buffer = 100
        if pitch > Default_Size - buffer:
            size = pitch + buffer
        else:
            size = Default_Size
        ax.set_ylim(0, size)