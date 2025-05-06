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

    # 1) Get the lines that these stations exist in
    # 2) Find eges of Lines Graph
    # 3) Find min distance between lines given lines graph and edges
    E_Lines = {(x, y) for (x, y) in Lx if Ld[x] & Ld[y]}

    T = max(graphs.distance(Ld.keys(), E_Lines,
         next(k for k, v in Ld.items() if x[0] in v),
         next(k for k, v in Ld.items() if x[1] in v))
     for x in X)
    return T


def assignCrew(crew, timeslots):
    crewkeys = ["roles", "etcs", "shift", "ptr"]
    trainkeys = ["start", "end", "etcs"]

    shiftTimes = {
        'Morning': (4, 12),
        'Day': (9, 17),
        'Night': (16, 24)
    }

    Sp = {c[0]: {crewkeys[i-1]: c[i] for i in range(1, len(c))} for c in crew}
    St = {t[0]: {trainkeys[i-1]: t[i] for i in range(1, len(t))} for t in timeslots}

    c = {}
    for kt, t in St.items(): 
        c[kt] = E(shiftTimes, Sp, t, c)

    pass
        
def E(shiftTimes, sp, t, c):
    e = (None, None)
    crew = []
    for kp, p in sp.items():
        p_s = shiftTimes[p["shift"]]
        t_s = (t["start"], t["end"])

        available = (p_s[0] <= t_s[0]) and (t_s[1] <= p_s[1])
        etcs = (t["etcs"] == p["etcs"])
        free = all(kp not in v for v in c.values())

        if(all({available, free})):
            crew.append(kp)
            if(len(crew) == 2):
                x = [None, None]
                me = sp[crew[0]]
                bro = sp[crew[1]]
                if(len(me['roles'][0]) < len(bro['roles'][0])):
                    if('Driver' in me['roles']):
                        x[0] = crew[0]
                        x[1] = crew[1]
                    else:
                        x[1] = crew[0]
                        x[0] = crew[1]
                else:
                    if('Driver' in bro['roles']):
                        x[0] = crew[1]
                        x[1] = crew[0]
                    else:
                        x[1] = crew[1]
                        x[0] = crew[0]
                e = tuple(x)
    return tuple(e)

def trainSchedule(timeSlots):
    ...

def trackNetworkCapacity(trackNetwork, blockTimes, destination):
    ...

crew = {
            # Driver,   Roles allowed        ETCS certified, shift,     peekTimeRestricted
            ('Alice',   ('Guard', 'Driver'), True,           'Morning', False),
            ('Bob',     ('Driver'),          False,          'Day',     True),
            ('Charlie', ('Guard'),           True,           'Morning', False),
            ('Denise',  ('Guard', 'Driver'), False,          'Day',     True),
            ('Elaine',  ('Guard', 'Driver'), False,          'Night',   False),
            ('Frank',   ('Guard', 'Driver'), True,           'Night',   False),
        }

slots = {
            # Line,  StartTime, EndTime, ETCS required
            ('IPNA', 6, 9, True),
            ('CASP', 11, 13, False),
            ('RPSP', 17, 19, True)
        }

assignCrew(crew, slots)