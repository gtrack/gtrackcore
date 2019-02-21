

class OperationHelp(object):
    def __init__(self, operation):
        self._info = operation.getInfoDict()
        self._kwArgs = operation.getKwArgumentInfoDict()

    def getName(self):
        return self._info['name']

    def getHelpStr(self):
        return self._info['operationHelp']

    def getTrackHelp(self):
        usageStr = 'Usage: ' + self.getName()
        trackStr = ''
        params = []
        for i, v in enumerate(self._info['trackHelp']):
            params.append('track{}'.format(i))
            trackStr += 'track{}: '.format(i) + v + '\n'
        for k, kw in self._kwArgs.iteritems():
            #required param
            if kw.shortkey is None:
                params.append(kw.key)
        usageStr += '(' + ', '.join(params) + ')'
        return usageStr + '\n' + trackStr

    def getKwArgHelp(self):
        kwArgStr = 'Keyword arguments: \n'
        for k, kw in self._kwArgs.iteritems():
            helpStr = kw.key + ' ({}): '
            if kw.shortkey is None:
                # required
                helpStr = helpStr.format('required')
            else:
                helpStr = helpStr.format('optional')
            helpStr += kw.help
            if kw.contentType is bool:
                if kw.defaultValue:
                    # default is false
                    helpStr += ', default value: False'
                else:
                    helpStr += ', default value: True'

            kwArgStr += '\t' + helpStr + '\n'

        return kwArgStr
