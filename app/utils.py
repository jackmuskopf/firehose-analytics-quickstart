from math import sqrt
from itertools import count, islice

def is_prime(n):
    return n > 1 and all(n % i for i in islice(count(2), int(sqrt(n)-1)))

def soft_index(*args, default=None):

    '''
    A function of soft indexing JSON objects

    e.g.

    my_obj = {'some_list' : [ {'color' : 'red'}, {'color' : 'blue'} ] }

    soft_index(my_obj, 'some_list', 0, 'color') == 'red'
    
    soft_index(my_obj, 'some_list', 12, 'color') is None
    '''

    if not args:
        return default
    
    obj = args[0]
    
    # if only an object and no index path, return the object
    if len(args) == 1:
        return obj

    # attempt to access each index provided after the object in args
    for index in args[1:]:

        # soft index for dictionary
        if isinstance(obj, dict) or isinstance(obj, list):
            try:
                obj = obj[index]
            except:
                obj = default
                break

        # if we try to index an unexpected type, return default
        else:
            obj = default
            break
            
    return obj


class dutil:

    '''
    A dictionary utility class
    '''

    class PathConflict(ValueError):
      pass

    @classmethod
    def soft_index(cls, *args, **kwargs):
      return soft_index(*args, **kwargs)
    
    @classmethod
    def dot_paths(cls, d, expand_lists=False):

        '''

        This function recursively transforms a dictionary of nested dictionaries into
        a non-nested dictionary with "." used to indicate json paths;

        Avoid using "." in dictionary keys or integers, as the result be ambiguous

        Example:


        example = {
            "name" : "jack",
            "food" : "tacos",
            "brain" : {
                "cortex" : {
                    "exists" : True
                },
                "color" : "grey" 
            },
            "activities" : [
                {
                    "name" : "programming",
                    "fun" : True,
                    "exciting" : True
                },
                {
                    "name" : "sleeping",
                    "fun" : True
                }
            ]
        }

        dot_paths(example)
        {'name': 'jack',
         'food': 'tacos',
         'brain.cortex.exists': True,
         'brain.color': 'grey',
         'activities': [{'name': 'programming', 'fun': True, 'exciting': True},
          {'name': 'sleeping', 'fun': True}]}


          dot_paths(example, expand_lists=True)
        {'name': 'jack',
         'food': 'tacos',
         'brain.cortex.exists': True,
         'brain.color': 'grey',
         'activities.0.name': 'programming',
         'activities.0.fun': True,
         'activities.0.exciting': True,
         'activities.1.name': 'sleeping',
         'activities.1.fun': True}

        '''
        
        dot_path_d = dict()
        
        if isinstance(d, dict):
        
            for k, v in d.items():
                
                # unpack child value
                dot_path_v = cls.dot_paths(v, expand_lists=expand_lists)
                
                if isinstance(dot_path_v, dict):
                
                    # add key for child to each path found
                    dot_path_v = {"{}.{}".format(k, v_k) : v_v for v_k, v_v in dot_path_v.items()}
                    
                    # update result dictionary
                    dot_path_d.update(dot_path_v)
                
                else:
                    
                    dot_path_d[k] = dot_path_v
                    
                    

        elif isinstance(d, list) and expand_lists:
            
            for ix, item in enumerate(d):
                
                # unpack item
                dot_path_item = cls.dot_paths(item, expand_lists=expand_lists)
                
                if isinstance(dot_path_item, dict):  
                
                    # add index to each path found in item
                    dot_path_item = {"{}.{}".format(ix, item_k) : item_v for item_k, item_v in dot_path_item.items()}
                    
                    # update result dictionary
                    dot_path_d.update(dot_path_item)
                
                else:
                    
                    dot_path_d[ix] = dot_path_item
        
        else:

            dot_path_d = d
                
        return dot_path_d
    
    @classmethod
    def terminal_paths(cls, d):

        paths = list()

        for key, val in d.items():

            if not isinstance(key, str):
                raise TypeError("Only string keys are allowed")
            
            if isinstance(val, dict):
                
                new_paths = [[key,] + p for p in cls.terminal_paths(val)]
                paths.extend(new_paths)

            else:
                paths.append([key,])
                
        return paths
    
    @classmethod
    def filter_dictionaries(cls, source, filter):
        '''
        source is a list of dictionaries
        filter is a dictionary that represents a filter on source

        dicitonaries that do not have the data in filter will be
        filtered from the result
        '''

        paths_to_check = cls.terminal_paths(filter)

        result = list()

        for item in source:

            keep_item = True
            for path in paths_to_check:
                item_val = cls.soft_index(item, *path)
                filter_val = cls.soft_index(filter, *path)

                if item_val != filter_val:
                    keep_item = False
                    break

            if keep_item:
                result.append(item)

        return result
    
    @classmethod
    def soft_set_path(cls, obj, value, path):
        
        if not path:
            return obj
        
        _obj = obj
        
        for key in path[:-1]:
            if key not in _obj:
                _obj[key] = dict()
            _obj = _obj[key]
        _obj[path[-1]] = value
        
        return obj

    @classmethod
    def recursive_values(cls, obj, **kwargs):

        expand_lists = kwargs.get('expand_lists', False)

        res = list()

        if isinstance(obj, list):

            if expand_lists:

                for item in obj:

                    res.extend(cls.recursive_values(item, **kwargs))
            
            else:

                res.append(obj)

        elif isinstance(obj, dict):

            for key, value in obj.items():

                res.extend(cls.recursive_values(value, **kwargs))

        else:

            res.append(obj)

        return res



        for key, value in obj.items():

            if isinstance(value, dict):

                values.extend(cls.recursive_values(value))

            elif isinstance(value, list):

                if expand_list:

                    for item in value:

                        if isinstance(item, dict):

                            values.extend()

        
    @classmethod 
    def obj_from_string_paths(cls, obj, delimeter="."):
        
        for str_path in obj.keys():
            for other_path in obj.keys():
                if str_path in other_path and str_path != other_path:
                    raise cls.PathConflict("{} overwrites {}".format(str_path, other_path))
        
        result = dict()
        for key, value in obj.items():
            path = key.split(delimeter)
            cls.soft_set_path(result, value, path)
        
        return result