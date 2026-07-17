def trend(values):

    if len(values)<2:
        return "?"

    diff=values[-1]-values[0]

    if diff>0:
        return "UP"

    if diff<0:
        return "DOWN"

    return "FLAT"
