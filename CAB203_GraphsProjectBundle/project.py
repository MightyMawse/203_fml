import graphs, digraphs, csv

## Optional imports
import itertools
# import functools

def maxMinTransfers(fileName):
    f = open(fileName, "r")
    r = list(csv.reader(f))

    Vl = [l for l in r] # All separate lines
    Ld = {l[0]: frozenset(l[1:]) for l in Vl}
    Lx = {(x, y) for x, y in itertools.permutations(Ld.keys(), 2)}
    S = {e for x in r for e in x[1:]} # All stations
    X = {(x, y) for x, y in itertools.product(S, S)} # cross product of stations
    E_Lines = {(x, y) for (x, y) in Lx if Ld[x] & Ld[y]}
    T = max(graphs.distance(Ld.keys(), E_Lines, next(k for k, v in Ld.items() if x[0] in v), next(k for k, v in Ld.items() if x[1] in v)) for x in X)
    return T


def assignCrew(crew, timeslots):
    shiftTimes = {
        'Morning': (4, 12),
        'Day': (9, 17),
        'Night': (16, 24)
    }

    etcsSet = {i for i in crew if i[2]}
    onlyDrivers = {i for i in crew if 'Driver' in i[1] and len(i[1]) == 1 and i not in etcsSet}
    onlyGuards = {i for i in crew if 'Guard' in i[1] and len(i[1]) == 1}
    driverAndGuard = {i for i in crew if 'Driver' in i[1] and 'Guard' in i[1] and i not in etcsSet}

    c = {"{}-{}-{}".format(t[0], t[1], t[2]): E(shiftTimes, t, onlyDrivers, onlyGuards, driverAndGuard, etcsSet) for t in sorted(timeslots)}

    return c
        
# Task 2
def E(shiftTimes, t, oD, oG, dG, eT):
    trainDriver = None
    trainGuard = None
    if(t[3]): # If ETCS on current train
        trainDriver = next((d[0] for d in eT if qualifies(shiftTimes, d, t)), None)
        if trainDriver is not None:
            eT.discard(next(d for d in eT if d[0] == trainDriver))
    else:
        if(len(oD) > 0): # If not ETCS, use ONLY DRIVERS first
            trainDriver = next((d[0] for d in oD if qualifies(shiftTimes, d, t)), None)
            if trainDriver is not None:
                oD.discard(next(d for d in oD if d[0] == trainDriver))
        else: # Otherwise use anything that qualifies
            trainDriver = next((d[0] for d in dG if qualifies(shiftTimes, d, t)), None)
            if trainDriver is not None:
                dG.discard(next(d for d in dG if d[0] == trainDriver))
    trainGuard = next((g[0] for g in oG if qualifies(shiftTimes, g, t)), None) # Do ONLY GUARDS first
    if trainGuard is not None:
        oG.discard(next(g for g in oG if g[0] == trainGuard))  # Find and remove the exact match
    if(trainGuard == None): # If still nothing then use the others that qualify
        trainGuard = next((x[0] for x in dG if qualifies(shiftTimes, x, t)), None)
        if trainGuard is not None:
            dG.discard(next(x for x in dG if x[0] == trainGuard))
    if(trainDriver != None and trainGuard != None):
        return (trainDriver, trainGuard)

    return None
def qualifies(shiftTimes, p, t):
    t_s = (t[1], t[2])
    p_m = t_s[0] in range(8, 10) or t_s[1] in range(8, 10)
    p_a = t_s[0] in range(16, 18) or t_s[1] in range(16, 18)
    s_n = next(n for n, (s, e) in shiftTimes.items() if s <= t_s[1] < e)
    shift = s_n == p[3]
    peak = ((p_m or p_a) and not p[4]) or (not(p_m or p_a))
    return shift and peak

def trainSchedule(timeSlots):
    tr = set()

    # Go from 'a', find next timeslot, go from 'b', find next and so on...
    for a in timeSlots:
        flat = {ts for t in tr for ts in t}
        if(a not in flat):
            newSubset = {a} # For each element we make a new subset (train)
            alias = a # Used for comparison which is changed
            for b in timeSlots: # Then we go through and try all that fit
                flat = {ts for t in tr for ts in t}
                free = alias not in flat and b not in flat and (b not in newSubset)
                match = (b[1] - alias[2] >= 1)
                if(free and match): # If we find one that fits
                    newSubset.add(b) # Add time slot to train
                    alias = b # Set the alias, now we start from b
            tr.add(frozenset(newSubset))    
    return len(tr)

def trackNetworkCapacity(trackNetwork, blockTimes, destination):
    e = [v for v in blockTimes] # All (a, b)
    s = [] #[i[0] for i in trackNetwork if len(digraphs.N_in(trackNetwork, e, i)) == 0] # Super source
    V = {*[item for sublist in trackNetwork for item in sublist]}

    # Get starting vertices to go inside of super source
    s = [q for m in trackNetwork for q in m if len(digraphs.N_in(V, e, q)) == 0]

    e = [
        ('s' if a in s else a, 's' if b in s else b)
        for (a, b) in e
    ]

    V.difference_update(s)
    V.add('s')

    # Fix dictionary duplicates for edges leaving source
    c = [(60 / blockTimes[x]) for x in blockTimes]
    w = {}
    w[e[E]] = w.get(e[E], 0) + c[E]
    n = digraphs.maxFlow(V, e, w, 's', destination)

    return int(sum(n[N] for N in n if N[1] == destination))

