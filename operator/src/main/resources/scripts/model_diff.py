import sets
import sys

class ModelDiffer(object):

    def __init__(self, current_dict, past_dict):

        self.final_changed_model=dict()
        self.current_dict = current_dict
        self.past_dict = past_dict
        self.set_current = sets.Set()
        self.set_past = sets.Set()
        for item in self.current_dict.keys():
            self.set_current.add(item)
        for item in self.past_dict.keys():
            self.set_past.add(item)
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        result = sets.Set()
        for o in self.intersect:
            if self.past_dict[o] != self.current_dict[o]:
                result.add(o)
        return result

    def unchanged(self):
        result = sets.Set()
        for o in self.intersect:
            if self.past_dict[o] == self.current_dict[o]:
                result.add(o)
        return result

    def print_diff(self,s, category):
        print category
        if len(s) > 0:
            print s

    def recursive_changed_detail(self, key, token, root):
        #print 'Entering recursive changed detail key=' + str(key) + ' token=' + str(token) + ' root=' + str(root)
        a=ModelDiffer(self.current_dict[key], self.past_dict[key])
        diff=a.changed()
        added=a.added()
        #print 'DEBUG: In recursive changed detail ' + str(diff)
        #print 'DEBUG: In recursive added detail: ' + str(a.added())
        if len(diff) > 0:
            for o in diff:
                # The token is a dotted string that is used to parse and rebuilt the structure later
                #print 'DEBUG: in recursive changed detail walking down1 ' + str(o)
                token=token+'.'+o
                if a.is_dict(o):
                    #print 'DEBUG: in recursive changed detail walking down2 ' + str(token)
                    a.recursive_changed_detail(o,token, root)
                    last=token.rfind('.')
                    token=root
                else:
                    all_changes.append(token)
                    last=token.rfind('.')
                    token=root

        if len(added) > 0:
            for item in added:
                all_added.append(token + '.' + item)
        #print 'Exiting recursive_changed_detail'

    def is_dict(self,key):
        if isinstance(self.current_dict[key],dict):
            return 1
        else:
            return 0

    def calculate_changed_model(self):
        result = dict()
        changed=self.changed()

        for s in changed:
            #print 'DEBUG: calculated_change_model checking item ' + s
            token=s
            x=self.recursive_changed_detail(s, token, s)
            #print 'DEBUG: after recursive changed details ' + str(all_changes)
            for item in all_changes:
                splitted=item.split('.',1)
                n=len(splitted)
                result=dict()
                walked=[]

                while n > 1:
                    tmp=dict()
                    tmp[splitted[0]]=dict()
                    if len(result) > 0:
                        # traverse to the leaf
                        leaf=result
                        for k in walked:
                            leaf = leaf[k]
                        leaf[splitted[0]]=dict()
                        walked.append(splitted[0])
                    else:
                        result=tmp
                        walked.append(splitted[0])
                    splitted=splitted[1].split('.',1)
                    n=len(splitted)

                leaf=result
                value_tree=self.current_dict
                for k in walked:
                    leaf = leaf[k]
                    value_tree=value_tree[k]

                leaf[splitted[0]] =value_tree[splitted[0]]
                self.merge_dictionaries(self.final_changed_model, result)
                # print self.final_changed_model

    def merge_dictionaries(self, dictionary, new_dictionary):
        """
        Merge the values from the new dictionary to the existing one.
        :param dictionary: the existing dictionary
        :param new_dictionary: the new dictionary to be merged
        """
        for key in new_dictionary:
            new_value = new_dictionary[key]
            if key not in dictionary:
                dictionary[key] = new_value
            else:
                value = dictionary[key]
                if isinstance(value, dict) and isinstance(new_value, dict):
                    self.merge_dictionaries(value, new_value)
                else:
                    dictionary[key] = new_value

    def is_safe_diff(self, model):
        if model.has_key('appDeployments'):
            return 0
        if not model:
            return 0
        return 1

    def get_final_changed_model(self):
        return self.final_changed_model


def eval_file(file):
    fh = open(file, 'r')
    content = fh.read()
    return eval(content)


def write_dictionary_to_json_file(dictionary, writer, indent=''):
    """
    Write the python dictionary in json syntax using the provided writer stream.
    :param dictionary: python dictionary to convert to json syntax
    :param writer: where to write the dictionary into json syntax
    :param indent: current string indention of the json syntax. If not provided, indent is an empty string
    """
    _start_dict = '{'
    _end_dict = '}'

    if dictionary is None:
        return
    end_line = ''
    writer.write(_start_dict)
    end_indent = indent

    indent += ' '
    for key, value in dictionary.iteritems():
        writer.write(end_line)
        end_line = ','
        writer.write(indent + '"' + quote_embedded_quotes(key) + '" : ')
        if isinstance(value, dict):
            write_dictionary_to_json_file(value, writer, indent)
        else:
            writer.write(format_json_value(value))
    writer.write(str(end_indent + _end_dict))

    return

def quote_embedded_quotes(text):
    """
    Quote all embedded double quotes in a string with a backslash.
    :param text: the text to quote
    :return: the quotes result
    """
    result = text
    if type(text) is str and '"' in text:
        result = text.replace('"', '\\"')
    return result

def format_json_value(value):
    """
    Format the value as a JSON snippet.
    :param value: the value
    :return: the JSON snippet
    """
    import java.lang.StringBuilder as StringBuilder
    builder = StringBuilder()
    if type(value) == bool or (type(value) == str and (value == 'true' or value == 'false')):
        if value:
            v = "true"
        else:
            v = "false"
        builder.append(v)
    elif type(value) == str:
        builder.append('"').append(quote_embedded_quotes(value)).append('"')
    else:
        builder.append(value)
    return builder.toString()


def main():
    current_dict = eval_file(sys.argv[1])
    past_dict = eval_file(sys.argv[2])
    obj=ModelDiffer(current_dict, past_dict)

    obj.calculate_changed_model()
    net_diff = obj.get_final_changed_model()
    fh=open('/tmp/diffed_model.json', 'w')
    write_dictionary_to_json_file(net_diff, fh)
    # fh.write(str(net_diff))
    fh.close()
    #print 'all added '
    #print all_added
    if not obj.is_safe_diff(net_diff):
        exit(exitcode=1)
    else:
        exit(exitcode=0)


if __name__ == "main":
    all_changes = []
    all_added = []
    main()

