import json
from flask import Flask, current_app, request

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
            indent=None if request.is_xhr else 2, cls=JSONEncoder),
        mimetype='application/json')

def publication_timeline(data, cumulative=False, group=6, provide={7,2}, label_group="date", label_provide={"count", "element"}):
    properties = set(map(lambda x: (str(x[group])), data))

    b = map(lambda x: (x[group],list(map(lambda y: str(x[y]), provide))), data)
    out = {}
    out['publication'] = {}
    out['publication_sorted'] = {}
    out['unknown'] = {}
    for s, k in b:
        try:
            if (k[0] != "None"):
                out['publication'][str(s)].update({(k[0], k[1])})
            else:
                out['unknown'][str(s)].update({(k[0], k[1])})
        except KeyError:
            if (k[0] != "None"):
                out['publication'][str(s)] = {}
                out['publication'][str(s)].update({(k[0], k[1])})
            else:
                out['unknown'][str(s)] = {}
                out['unknown'][str(s)].update({(k[0], k[1])})
    for t in out:
        try:
            a=out[t]
        except KeyError:
            out[t] = 0
    out['publication_sorted'] = []
    for e, v in out['publication'].items():
        prevkey_val = 0
        latest_count = {}
        try: 
            del v["None"]
        except KeyError:
            pass
        for key in sorted(v.iterkeys()):
            newdata = {}
            newdata[label_group] = e
            if (cumulative == True):
                try:
                    latest_count[e] = int(v[key])
                except KeyError:
                    latest_count[e] = 0
                prevkey_val = int(v[key]) + prevkey_val
            newdata["count"] = int(v[key]) + latest_count[e]
            newdata["element"] = key
            out['publication_sorted'].append(newdata)
    return out

def publication_dates_groups(data, cumulative=False, group=6, provide={7,2}, label_group="date", label_provide={"count", "element"}):
    dates = set(map(lambda x: (str(x[group])), data))
    elements = set(map(lambda x: (x[2]), data))
    alldata = map(lambda x: ((str(x[group]), x[2]),x[7]), data)
    
    b = map(lambda x: (x[group],list(map(lambda y: str(x[y]), provide))), data)
    out = {}

    out["dates"] = []
    prev_values = {}
    for p in sorted(dates):
        # get each element
        newdata = {}
        newdata["date"] = p
        for e in elements:
            try:
                prev_values[e]
            except KeyError:
                prev_values[e] = 0
            newdata[e] = 0
            for data in alldata:
                if ((data[0][0] == p) and (data[0][1]==e)):
                    newdata[e] = data[1]
                    prev_values[e] = prev_values[e] + data[1]
                else:
                    newdata[e] = prev_values[e]
            if (newdata[e] == 0):
                newdata[e] = prev_values[e]
        out["dates"].append(newdata)
        # get each date

    return out

def nest_compliance_results(data):
    properties = set(map(lambda x: (x[2]), data))
    b = map(lambda x: (x[2],(x[6], x[7])), data)
    out = {}
    for s, k in b:
        try:
            out[s].update({(k[0], k[1])})
        except KeyError:
            out[s] = {}
            out[s].update({(k[0], k[1])})
    values = {'fc', 'pc', 'uc', 'fp', 'up'}
    for t in out:
        for v in values:
            try:
                a=out[t][v]
            except KeyError:
                out[t][v] = 0
    return out

def nest_compliance_scores(data):
    properties = set(map(lambda x: (x[2]), data))
    b = map(lambda x: (x[2],(x[6], x[7])), data)
    out = {}
    for s, k in b:
        try:
            out[s].update({(k[0], k[1])})
        except KeyError:
            out[s] = {}
            out[s].update({(k[0], k[1])})
    values = {True, None}
    for t in out:
        for v in values:
            try:
                a=out[t][v]
            except KeyError:
                out[t][v] = 0
    return out

def toUs(element):
    # replace hyphen with underscore
    us = re.sub("-", "_", element)
    return us
